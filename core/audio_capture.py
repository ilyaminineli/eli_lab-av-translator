from __future__ import annotations

import logging
import threading
import time
import warnings
from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import numpy as np

from core.audio_analysis import AudioAnalysisFrame, AudioAnalysisSettings, AudioAnalyzer

_LOG = logging.getLogger(__name__)


class AudioCaptureState(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEVICE_LOST = "device_lost"
    ERROR = "error"


@dataclass(frozen=True)
class AudioInputDevice:
    id: str
    name: str
    channels: int
    is_loopback: bool
    kind: str = "input"

    @property
    def label(self) -> str:
        suffix = " · SYS LOOPBACK" if self.is_loopback else " · INPUT"
        return f"{self.name}{suffix} ({self.channels} ch)"


@dataclass(frozen=True)
class AudioBlock:
    samples: np.ndarray
    sample_rate: int
    timestamp: float


class AudioFrameQueue:
    """Bounded latest-value queue; stale analysis frames are discarded first."""

    def __init__(self, capacity: int = 8) -> None:
        self.capacity = max(1, int(capacity))
        self._frames: deque[AudioAnalysisFrame] = deque()
        self._lock = threading.Lock()
        self.dropped = 0

    def push_latest(self, frame: AudioAnalysisFrame) -> None:
        with self._lock:
            if len(self._frames) >= self.capacity:
                self._frames.popleft()
                self.dropped += 1
            self._frames.append(frame)

    def drain(self, limit: int = 8) -> list[AudioAnalysisFrame]:
        with self._lock:
            count = min(max(0, int(limit)), len(self._frames))
            return [self._frames.popleft() for _ in range(count)]

    def latest(self) -> AudioAnalysisFrame | None:
        with self._lock:
            return self._frames[-1] if self._frames else None

    def clear(self) -> None:
        with self._lock:
            self._frames.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._frames)


class SoundCardBackend:
    """Optional SoundCard adapter for physical input and supported loopback."""

    def list_devices(self) -> list[AudioInputDevice]:
        try:
            import soundcard as sc
        except ImportError as exc:
            raise RuntimeError(
                "Audio capture requires SoundCard. Install with: "
                "python -m pip install soundcard"
            ) from exc

        devices: list[AudioInputDevice] = []
        for microphone in sc.all_microphones(include_loopback=True):
            channels = getattr(microphone, "channels", 0)
            if isinstance(channels, (list, tuple)):
                channel_count = len(channels)
            else:
                channel_count = int(channels or 0)
            if channel_count < 1:
                continue
            device_id = str(getattr(microphone, "id", ""))
            if not device_id:
                continue
            is_loopback = bool(getattr(microphone, "isloopback", False))
            devices.append(
                AudioInputDevice(
                    id=device_id,
                    name=str(getattr(microphone, "name", device_id)),
                    channels=channel_count,
                    is_loopback=is_loopback,
                    kind="loopback" if is_loopback else "input",
                )
            )
        return devices

    def open_recorder(
            self,
            device_id: str,
            sample_rate: int,
            block_size: int,
    ) -> Any:
        import soundcard as sc

        # Windows WASAPI can emit one warning per recorder block when a buffer
        # discontinuity occurs. Keep the first diagnostic but avoid flooding the
        # console with the same non-fatal warning on every block.
        warnings.filterwarnings(
            "once",
            message=r"data discontinuity in recording",
            module=r"soundcard\.mediafoundation",
        )

        microphone = next(
            (
                mic
                for mic in sc.all_microphones(include_loopback=True)
                if str(getattr(mic, "id", "")) == device_id
            ),
            None,
        )
        if microphone is None:
            raise FileNotFoundError("The selected audio device is no longer available.")
        # Keep all channels. Some WASAPI configurations return invalid data
        # for a single selected channel; AudioAnalyzer safely downmixes instead.
        return microphone.recorder(
            samplerate=sample_rate,
            blocksize=block_size,
        )


class SyntheticAudio:
    """Deterministic test signal: low oscillator, upper tone and periodic transients."""

    def __init__(self, sample_rate: int = 48000, bpm: float = 120.0) -> None:
        self.sample_rate = max(8000, int(sample_rate))
        self.bpm = max(40.0, min(240.0, float(bpm)))
        self._sample_index = 0

    def next_block(self, frames: int = 1024) -> np.ndarray:
        count = max(1, int(frames))
        indices = np.arange(self._sample_index, self._sample_index + count)
        time_values = indices / self.sample_rate
        beat_period = 60.0 / self.bpm
        phase = np.mod(time_values, beat_period)
        transient = np.exp(-phase * 35.0) * (phase < 0.04)
        signal = (
                0.16 * np.sin(2.0 * np.pi * 110.0 * time_values)
                + 0.08 * np.sin(2.0 * np.pi * 880.0 * time_values)
                + 0.60 * transient
        )
        self._sample_index += count
        return np.asarray(signal, dtype=np.float32).reshape(-1, 1)


class AudioCaptureService:
    """Owns one capture/analysis worker and publishes bounded feature snapshots."""

    def __init__(
            self,
            backend: Any | None = None,
            settings: AudioAnalysisSettings | None = None,
            sample_rate: int = 48000,
            block_size: int = 1024,
    ) -> None:
        self.backend = backend or SoundCardBackend()
        self.settings = settings or AudioAnalysisSettings()
        self.settings.normalize()
        self.sample_rate = max(8000, int(sample_rate))
        self.block_size = max(256, min(8192, int(block_size)))
        self.frames = AudioFrameQueue(8)
        self._lock = threading.RLock()
        self._cancel = threading.Event()
        self._thread: threading.Thread | None = None
        self._state = AudioCaptureState.STOPPED
        self._error = ""
        self._selected_device_id = ""
        self._selected_device_name = ""
        self._source_kind = "none"
        self._worker_generation = 0
        self._synthetic: SyntheticAudio | None = None
        self._replay_samples: np.ndarray | None = None
        self._replay_repeat = False

    @property
    def state(self) -> AudioCaptureState:
        with self._lock:
            return self._state

    @property
    def error(self) -> str:
        with self._lock:
            return self._error

    @property
    def source_kind(self) -> str:
        with self._lock:
            return self._source_kind

    @property
    def selected_device_id(self) -> str:
        with self._lock:
            return self._selected_device_id

    @property
    def selected_device_name(self) -> str:
        with self._lock:
            return self._selected_device_name

    def list_devices(self) -> list[AudioInputDevice]:
        return self.backend.list_devices()

    def start(self, device_id: str) -> None:
        devices = self.list_devices()
        selected = next((item for item in devices if item.id == device_id), None)
        if selected is None:
            raise FileNotFoundError("The selected audio input is not available.")
        self._start_worker(
            source_kind="loopback" if selected.is_loopback else "input",
            device_id=selected.id,
            device_name=selected.name,
        )

    def start_test_signal(self, bpm: float = 120.0) -> None:
        self._synthetic = SyntheticAudio(self.sample_rate, bpm)
        self._start_worker(
            source_kind="test",
            device_id="test-signal",
            device_name=f"Deterministic test signal · {bpm:g} BPM",
        )

    def start_replay(
            self,
            samples: np.ndarray,
            sample_rate: int,
            repeat: bool = False,
    ) -> None:
        data = np.asarray(samples, dtype=np.float32)
        if data.ndim not in {1, 2} or data.size == 0:
            raise ValueError(
                "Replay audio must be a non-empty mono or multichannel array."
            )
        self._replay_samples = np.array(data, dtype=np.float32, copy=True)
        self.sample_rate = max(8000, int(sample_rate))
        self._replay_repeat = bool(repeat)
        self._start_worker(
            source_kind="replay",
            device_id="replay-fixture",
            device_name="Recorded audio fixture",
        )

    def _start_worker(
            self,
            source_kind: str,
            device_id: str,
            device_name: str,
    ) -> None:
        if self._thread is not None and self._thread.is_alive():
            self.stop()
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError(
                    "The previous audio capture worker has not stopped yet."
                )
        self.frames.clear()
        self._cancel = threading.Event()
        self._worker_generation += 1
        generation = self._worker_generation
        with self._lock:
            self._state = AudioCaptureState.STARTING
            self._error = ""
            self._selected_device_id = device_id
            self._selected_device_name = device_name
            self._source_kind = source_kind
        analyzer = AudioAnalyzer(self.settings)
        thread = threading.Thread(
            target=self._run_worker,
            args=(generation, source_kind, device_id, analyzer, self._cancel),
            name=f"AudioCapture-{generation}",
            daemon=True,
        )
        self._thread = thread
        thread.start()

    def _publish_samples(
            self,
            analyzer: AudioAnalyzer,
            samples: np.ndarray,
            timestamp: float,
    ) -> None:
        frame = analyzer.process(samples, self.sample_rate, timestamp)
        self.frames.push_latest(frame)

    def _run_worker(
            self,
            generation: int,
            source_kind: str,
            device_id: str,
            analyzer: AudioAnalyzer,
            cancel: threading.Event,
    ) -> None:
        try:
            if source_kind in {"input", "loopback"}:
                recorder = self.backend.open_recorder(
                    device_id,
                    self.sample_rate,
                    self.block_size,
                )
                with recorder as active_recorder:
                    self._set_state(AudioCaptureState.RUNNING, "")
                    while not cancel.is_set():
                        samples = active_recorder.record(numframes=self.block_size)
                        if samples is None or np.asarray(samples).size == 0:
                            continue
                        self._publish_samples(
                            analyzer,
                            np.asarray(samples, dtype=np.float32),
                            time.monotonic(),
                        )
            elif source_kind == "test":
                self._set_state(AudioCaptureState.RUNNING, "")
                synthetic = self._synthetic or SyntheticAudio(self.sample_rate)
                block_duration = self.block_size / self.sample_rate
                while not cancel.is_set():
                    samples = synthetic.next_block(self.block_size)
                    self._publish_samples(analyzer, samples, time.monotonic())
                    cancel.wait(block_duration)
            elif source_kind == "replay":
                self._set_state(AudioCaptureState.RUNNING, "")
                samples = self._replay_samples
                if samples is None:
                    raise ValueError("No replay fixture has been loaded.")
                cursor = 0
                duration = self.block_size / self.sample_rate
                while not cancel.is_set():
                    end = min(samples.shape[0], cursor + self.block_size)
                    block = samples[cursor:end]
                    if block.size == 0:
                        if self._replay_repeat:
                            cursor = 0
                            analyzer.reset()
                            continue
                        break
                    self._publish_samples(analyzer, block, time.monotonic())
                    cursor = end
                    cancel.wait(duration)
            else:
                raise ValueError(f"Unknown audio source kind: {source_kind}")
        except FileNotFoundError as exc:
            self._set_state(AudioCaptureState.DEVICE_LOST, str(exc))
        except Exception as exc:
            _LOG.exception("Audio capture/analysis worker failed")
            self._set_state(AudioCaptureState.ERROR, str(exc))
        finally:
            if cancel.is_set() and self.state != AudioCaptureState.DEVICE_LOST:
                self._set_state(AudioCaptureState.STOPPED, "")
            elif self.state == AudioCaptureState.RUNNING:
                self._set_state(AudioCaptureState.STOPPED, "")
            with self._lock:
                if generation == self._worker_generation:
                    self._thread = None

    def _set_state(self, state: AudioCaptureState, error: str) -> None:
        with self._lock:
            self._state = state
            self._error = error

    def stop(self, timeout: float = 2.0) -> bool:
        thread = self._thread
        if thread is None:
            self._set_state(AudioCaptureState.STOPPED, "")
            return True
        self._cancel.set()
        thread.join(max(0.0, float(timeout)))
        stopped = not thread.is_alive()
        if stopped:
            with self._lock:
                self._thread = None
                self._state = AudioCaptureState.STOPPED
                self._error = ""
        else:
            self._set_state(
                AudioCaptureState.ERROR,
                "Audio recorder did not release before the shutdown timeout.",
            )
        return stopped

    def refresh_device_state(self) -> bool:
        """Detect removed devices without blocking the media/render threads."""
        if self.source_kind not in {"input", "loopback"}:
            return self.state in {AudioCaptureState.STARTING, AudioCaptureState.RUNNING}
        try:
            devices = self.list_devices()
        except Exception as exc:
            self._set_state(AudioCaptureState.ERROR, str(exc))
            return False
        present = any(item.id == self.selected_device_id for item in devices)
        if not present and self.state == AudioCaptureState.RUNNING:
            self._cancel.set()
            self._set_state(
                AudioCaptureState.DEVICE_LOST,
                "Selected audio device was disconnected. Refresh and select another input.",
            )
        return present

    def update_settings(self, settings: AudioAnalysisSettings) -> None:
        settings.normalize()
        with self._lock:
            # Preserve the shared settings object referenced by the active analyzer.
            self.settings.sensitivity = settings.sensitivity
            self.settings.attack_ms = settings.attack_ms
            self.settings.release_ms = settings.release_ms
            self.settings.onset_threshold = settings.onset_threshold
            self.settings.beat_min_bpm = settings.beat_min_bpm
            self.settings.beat_max_bpm = settings.beat_max_bpm
            self.settings.beat_confidence_min = settings.beat_confidence_min

    def latest_frame(self) -> AudioAnalysisFrame | None:
        return self.frames.latest()

    def drain_frames(self, limit: int = 8) -> list[AudioAnalysisFrame]:
        return self.frames.drain(limit)

    def shutdown(self) -> None:
        self.stop()
        self.frames.clear()
        self._replay_samples = None
        self._synthetic = None
