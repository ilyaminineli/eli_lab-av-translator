from __future__ import annotations

import logging
from pathlib import Path

from media.frame_queue import FrameQueue, FrameSnapshot, VideoFrameData
from media.video_decoder import VideoDecoder

_LOG = logging.getLogger(__name__)


class VideoDeck:
    def __init__(self, deck_id: str) -> None:
        self.id = deck_id
        self.frame_queue = FrameQueue(max_size=3)
        self.decoder: VideoDecoder | None = None
        self._retired_decoders: list[VideoDecoder] = []
        self.current_frame: VideoFrameData | None = None
        self.frame_revision = 0
        self.path: str | None = None
        self.asset_id: str | None = None
        self.collection_id: str | None = None
        self.segment_start = 0.0
        self.segment_end: float | None = None
        self.loop = True
        self.locked = False
        self._held = False

    @property
    def is_playing(self) -> bool:
        return bool(self.decoder and self.decoder.is_playing)

    @property
    def error(self) -> str | None:
        return self.decoder.last_error if self.decoder else None

    @property
    def is_held(self) -> bool:
        return self._held

    @property
    def is_paused(self) -> bool:
        return bool(
            self.decoder
            and self.decoder.is_running
            and not self.decoder.is_playing
            and not self._held
        )

    def _retire_decoder(self, decoder: VideoDecoder) -> None:
        stopped = decoder.stop(timeout=0.2)
        if not stopped:
            self._retired_decoders.append(decoder)
            _LOG.debug(
                "%s decoder is still exiting; replacement playback is "
                "isolated on a new frame queue",
                self.id,
            )
        self._reap_retired_decoders()

    def _reap_retired_decoders(self) -> None:
        self._retired_decoders = [
            decoder for decoder in self._retired_decoders if decoder.worker_alive
        ]

    def load(
            self,
            path: str | Path,
            asset_id: str | None = None,
            collection_id: str | None = None,
            segment_start: float = 0.0,
            segment_end: float | None = None,
            loop: bool | None = None,
    ) -> None:
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        start = max(0.0, float(segment_start))
        end = float(segment_end) if segment_end is not None else None
        if end is not None and end <= start:
            raise ValueError("Segment end must be later than segment start.")

        # A decoder always owns its queue. If the old worker is finishing an
        # in-flight PyAV call, it cannot publish into the replacement deck.
        if self.decoder is not None:
            self._retire_decoder(self.decoder)
        self.frame_queue = FrameQueue(max_size=3)
        self.decoder = None
        self.current_frame = None
        self.frame_revision += 1
        self.path = str(source)
        self._held = False
        self.asset_id = asset_id
        self.collection_id = collection_id
        self.segment_start = start
        self.segment_end = end
        if loop is not None:
            self.loop = bool(loop)

        self.decoder = VideoDecoder(
            source,
            self.frame_queue,
            loop=self.loop,
            segment_start=self.segment_start,
            segment_end=self.segment_end,
        )
        self.decoder.start(autoplay=True)
        self._reap_retired_decoders()

    def play(self) -> None:
        if not self.path:
            return
        self._held = False
        if self.decoder is None or not self.decoder.is_running:
            self.load(
                self.path,
                self.asset_id,
                self.collection_id,
                segment_start=self.segment_start,
                segment_end=self.segment_end,
                loop=self.loop,
            )
        else:
            self.decoder.play()

    def pause(self) -> None:
        self._held = False
        if self.decoder:
            self.decoder.pause()

    def hold(self) -> bool:
        """Hold the most recently presented frame without releasing the deck source."""
        if self.current_frame is None or self.decoder is None:
            return False
        self.decoder.pause()
        self._held = True
        return True

    def release_hold(self) -> None:
        if self._held:
            self.play()

    def restart(self) -> None:
        """Restart the loaded source from its current segment in-point."""
        if not self.path:
            return
        self.load(
            self.path,
            asset_id=self.asset_id,
            collection_id=self.collection_id,
            segment_start=self.segment_start,
            segment_end=self.segment_end,
            loop=self.loop,
        )

    def stop(self) -> None:
        self._held = False
        if self.decoder:
            self._retire_decoder(self.decoder)
            self.decoder = None
        for decoder in self._retired_decoders:
            decoder.stop(timeout=0.5)
        self._reap_retired_decoders()
        self.frame_queue.clear()
        self.current_frame = None
        self._held = False
        self.frame_revision += 1

    def seek(self, seconds: float) -> None:
        if self.decoder:
            self.decoder.seek(seconds)

    def set_loop(self, enabled: bool) -> None:
        self.loop = bool(enabled)
        if self.decoder:
            self.decoder.set_loop(enabled)

    def consume_latest_frame(self) -> VideoFrameData | None:
        latest = self.frame_queue.pop_latest()
        if latest is not None:
            self.current_frame = latest
            self.frame_revision += 1
        self._reap_retired_decoders()
        return latest

    def snapshot_frame(self) -> FrameSnapshot | None:
        if self.current_frame is None:
            return None
        return FrameSnapshot(self.frame_revision, self.current_frame)

    def performance_stats(self) -> dict[str, int | float | bool]:
        decoder = self.decoder
        return {
            "playing": self.is_playing,
            "queue_depth": len(self.frame_queue),
            "dropped_frames": self.frame_queue.dropped_frames,
            "decoded_frames": decoder.decoded_frames if decoder else 0,
            "published_frames": decoder.published_frames if decoder else 0,
            "skipped_output_frames": decoder.skipped_output_frames if decoder else 0,
            "decode_time_ms": decoder.decode_time_ms if decoder else 0.0,
            "conversion_time_ms": decoder.conversion_time_ms if decoder else 0.0,
            "retired_workers": sum(item.worker_alive for item in self._retired_decoders),
        }

    def close(self) -> None:
        self.stop()
        self.path = None
        self.asset_id = None
        self.collection_id = None
        self.segment_start = 0.0
        self.segment_end = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "path": self.path,
            "asset_id": self.asset_id,
            "collection_id": self.collection_id,
            "segment_start": self.segment_start,
            "segment_end": self.segment_end,
            "loop": self.loop,
            "playing": self.is_playing,
            "locked": self.locked,
        }
