from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from config import MAX_DECODE_FPS, MAX_DECODE_HEIGHT, MAX_DECODE_WIDTH
from media.frame_queue import FrameQueue, VideoFrameData

_LOG = logging.getLogger(__name__)


class VideoDecoder:
    """Timestamp-paced decoder with bounded preview output and segment playback."""

    def __init__(
            self,
            path: str | Path,
            frame_queue: FrameQueue,
            loop: bool = True,
            segment_start: float = 0.0,
            segment_end: float | None = None,
            max_output_width: int = MAX_DECODE_WIDTH,
            max_output_height: int = MAX_DECODE_HEIGHT,
            max_output_fps: float | None = MAX_DECODE_FPS,
    ) -> None:
        self.path = Path(path).expanduser().resolve()
        self.frame_queue = frame_queue
        self.loop = bool(loop)
        self.segment_start = max(0.0, float(segment_start))
        self.segment_end = (
            max(self.segment_start + 0.05, float(segment_end))
            if segment_end is not None else None
        )
        self.max_output_width = max(2, int(max_output_width))
        self.max_output_height = max(2, int(max_output_height))
        self.max_output_fps = (
            max(1.0, float(max_output_fps))
            if max_output_fps is not None else None
        )
        self._condition = threading.Condition()
        self._thread: threading.Thread | None = None
        self._running = False
        self._playing = False
        self._seek_request: float | None = None
        self._paused_at: float | None = None
        self._timeline_shift = 0.0
        self._last_error: str | None = None
        self.seek_fallbacks = 0
        self.decoded_frames = 0
        self.published_frames = 0
        self.skipped_output_frames = 0
        self.decode_time_ms = 0.0
        self.conversion_time_ms = 0.0

    @property
    def is_playing(self) -> bool:
        with self._condition:
            return self._playing and self._running

    @property
    def is_running(self) -> bool:
        with self._condition:
            return self._running

    @property
    def worker_alive(self) -> bool:
        with self._condition:
            return bool(self._thread and self._thread.is_alive())

    @property
    def last_error(self) -> str | None:
        with self._condition:
            return self._last_error

    def start(self, autoplay: bool = True) -> None:
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        with self._condition:
            if self._thread is not None and self._thread.is_alive():
                if not self._running:
                    raise RuntimeError("Decoder is still shutting down; load a new deck instance.")
                self._playing = autoplay
                self._condition.notify_all()
                return
            self._thread = None
            self._running = True
            self._playing = autoplay
            self._seek_request = None
            self._paused_at = None
            self._timeline_shift = 0.0
            self._last_error = None
            self.decoded_frames = 0
            self.published_frames = 0
            self.skipped_output_frames = 0
            self.decode_time_ms = 0.0
            self.conversion_time_ms = 0.0
            thread = threading.Thread(
                target=self._decode_loop,
                name=f"VideoDecoder-{self.path.name}",
                daemon=True,
            )
            self._thread = thread
            thread.start()

    def play(self) -> None:
        with self._condition:
            if self._paused_at is not None:
                self._timeline_shift += time.monotonic() - self._paused_at
                self._paused_at = None
            self._playing = True
            self._condition.notify_all()

    def pause(self) -> None:
        with self._condition:
            if self._playing:
                self._paused_at = time.monotonic()
            self._playing = False
            self._condition.notify_all()

    def seek(self, seconds: float) -> None:
        with self._condition:
            self._seek_request = max(self.segment_start, float(seconds))
            if self.segment_end is not None:
                self._seek_request = min(self._seek_request, self.segment_end)
            self.frame_queue.clear()
            self._condition.notify_all()

    def set_loop(self, enabled: bool) -> None:
        with self._condition:
            self.loop = bool(enabled)

    def stop(self, timeout: float = 1.0) -> bool:
        """Request shutdown and wait at most timeout seconds for the worker."""
        with self._condition:
            self._running = False
            self._playing = False
            self._condition.notify_all()
            thread = self._thread
        if thread is not None and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=max(0.0, float(timeout)))
        stopped = thread is None or not thread.is_alive()
        if stopped:
            with self._condition:
                if self._thread is thread:
                    self._thread = None
        self.frame_queue.clear()
        return stopped

    def _wait_for_deadline(self, deadline: float) -> str:
        with self._condition:
            while self._running:
                if self._seek_request is not None:
                    return "seek"
                if not self._playing:
                    self._condition.wait(timeout=0.1)
                    continue
                remaining = deadline + self._timeline_shift - time.monotonic()
                if remaining <= 0:
                    return "frame"
                self._condition.wait(timeout=min(remaining, 0.05))
        return "stop"

    def _take_seek_request(self, default: float) -> float:
        with self._condition:
            if self._seek_request is None:
                return default
            value = self._seek_request
            self._seek_request = None
            self._timeline_shift = 0.0
            self._paused_at = None
            return value

    def _preview_pixels(self, frame):
        width = int(frame.width)
        height = int(frame.height)
        scale = min(
            1.0,
            self.max_output_width / max(1, width),
            self.max_output_height / max(1, height),
        )
        if scale < 1.0:
            width = max(2, int(round(width * scale)))
            height = max(2, int(round(height * scale)))
            frame = frame.reformat(width=width, height=height, format="rgb24")
        return frame.to_ndarray(format="rgb24")

    def _decode_loop(self) -> None:
        try:
            import av
        except ImportError:
            self._set_error("PyAV is not installed.")
            return

        seek_to = self.segment_start
        try:
            while True:
                with self._condition:
                    if not self._running:
                        break
                try:
                    with av.open(str(self.path)) as container:
                        stream = next(
                            (item for item in container.streams if item.type == "video"),
                            None,
                        )
                        if stream is None:
                            raise ValueError("No video stream was found.")
                        if seek_to > 0 and stream.time_base:
                            try:
                                container.seek(
                                    int(seek_to / float(stream.time_base)),
                                    stream=stream,
                                    backward=True,
                                )
                            except av.error.PermissionError as exc:
                                # Some Windows filesystems / media demuxers allow
                                # sequential reads but reject random-access seeking.
                                # Keep the requested timestamp filter below and scan
                                # from the beginning rather than killing the deck.
                                self.seek_fallbacks += 1
                                if self.seek_fallbacks == 1:
                                    _LOG.warning(
                                        "Random seek is unavailable for %s; "
                                        "falling back to sequential decode and frame "
                                        "discard (further failures: %s)",
                                        self.path,
                                        exc,
                                    )

                        average_rate = float(stream.average_rate) if stream.average_rate else 30.0
                        first_timestamp: float | None = None
                        timeline_start = 0.0
                        frame_index = 0
                        last_published_timestamp: float | None = None
                        restart = False

                        frame_iterator = iter(container.decode(stream))
                        while True:
                            decode_started = time.perf_counter()
                            try:
                                frame = next(frame_iterator)
                            except StopIteration:
                                break
                            self.decode_time_ms += (
                                                           time.perf_counter() - decode_started
                                                   ) * 1000.0

                            with self._condition:
                                if not self._running:
                                    return
                                pending_seek = self._seek_request
                            if pending_seek is not None:
                                seek_to = self._take_seek_request(seek_to)
                                restart = True
                                break

                            if frame.pts is not None and stream.time_base:
                                timestamp = float(frame.pts * stream.time_base)
                            else:
                                timestamp = frame_index / max(average_rate, 0.1)
                            frame_index += 1
                            self.decoded_frames += 1

                            if timestamp + 0.03 < seek_to:
                                continue
                            if self.segment_end is not None and timestamp >= self.segment_end:
                                break

                            if first_timestamp is None:
                                first_timestamp = timestamp
                                timeline_start = time.monotonic()

                            due = timeline_start + (timestamp - first_timestamp)
                            wait_result = self._wait_for_deadline(due)
                            if wait_result == "stop":
                                return
                            if wait_result == "seek":
                                seek_to = self._take_seek_request(seek_to)
                                restart = True
                                break

                            frame_interval = (
                                1.0 / self.max_output_fps
                                if self.max_output_fps is not None else 0.0
                            )
                            if (
                                    last_published_timestamp is not None
                                    and frame_interval > 0
                                    and timestamp - last_published_timestamp < frame_interval * 0.92
                            ):
                                self.skipped_output_frames += 1
                                continue

                            conversion_started = time.perf_counter()
                            pixels = self._preview_pixels(frame)
                            conversion_elapsed = time.perf_counter() - conversion_started
                            self.conversion_time_ms += conversion_elapsed * 1000.0
                            height, width, _ = pixels.shape
                            self.frame_queue.push_latest(
                                VideoFrameData(
                                    pixels=pixels,
                                    width=int(width),
                                    height=int(height),
                                    timestamp=timestamp,
                                )
                            )
                            last_published_timestamp = timestamp
                            self.published_frames += 1

                    if restart:
                        continue
                    with self._condition:
                        should_loop = self.loop
                    if should_loop:
                        seek_to = self.segment_start
                        continue
                    with self._condition:
                        self._playing = False
                        self._running = False
                    break
                except Exception as exc:
                    self._set_error(str(exc))
                    _LOG.exception("Video decoding failed: %s", self.path)
                    break
        finally:
            with self._condition:
                self._playing = False
                self._running = False
                if self._thread is threading.current_thread():
                    self._thread = None
                self._condition.notify_all()

    def _set_error(self, message: str) -> None:
        with self._condition:
            self._last_error = message
            self._playing = False
            self._running = False
            self._condition.notify_all()
