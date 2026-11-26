from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import asdict, dataclass, field

import numpy as np


@dataclass
class AudioAnalysisSettings:
    sensitivity: float = 1.8
    attack_ms: float = 24.0
    release_ms: float = 180.0
    onset_threshold: float = 0.22
    beat_min_bpm: float = 60.0
    beat_max_bpm: float = 180.0
    beat_confidence_min: float = 0.45

    def normalize(self) -> None:
        self.sensitivity = max(0.1, min(12.0, float(self.sensitivity)))
        self.attack_ms = max(1.0, min(1000.0, float(self.attack_ms)))
        self.release_ms = max(5.0, min(3000.0, float(self.release_ms)))
        self.onset_threshold = max(0.02, min(0.95, float(self.onset_threshold)))
        self.beat_min_bpm = max(40.0, min(180.0, float(self.beat_min_bpm)))
        self.beat_max_bpm = max(
            self.beat_min_bpm,
            min(240.0, float(self.beat_max_bpm)),
        )
        self.beat_confidence_min = max(
            0.05,
            min(0.95, float(self.beat_confidence_min)),
        )

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class AudioAnalysisFrame:
    timestamp: float
    sample_rate: int
    rms: float
    peak: float
    low: float
    mid: float
    high: float
    onset: float
    bpm: float | None
    beat_confidence: float

    def sources(self) -> dict[str, float]:
        values = {
            "audio.rms": self.rms,
            "audio.peak": self.peak,
            "audio.low": self.low,
            "audio.mid": self.mid,
            "audio.high": self.high,
            "audio.onset": self.onset,
            "audio.beat_confidence": self.beat_confidence,
        }
        if self.bpm is not None:
            values["audio.bpm_normalized"] = max(0.0, min(1.0, self.bpm / 240.0))
        return values


@dataclass
class AudioAnalyzer:
    """Small-block FFT and envelope analysis; no audio I/O is performed here."""

    settings: AudioAnalysisSettings = field(default_factory=AudioAnalysisSettings)
    _smoothed: dict[str, float] = field(default_factory=dict, repr=False)
    _previous_rms: float = 0.0
    _last_beat_at: float | None = None
    _beat_intervals: deque[float] = field(
        default_factory=lambda: deque(maxlen=12),
        repr=False,
    )
    _last_onset_at: float = 0.0
    _last_timestamp: float | None = None

    def reset(self) -> None:
        self._smoothed.clear()
        self._previous_rms = 0.0
        self._last_beat_at = None
        self._beat_intervals.clear()
        self._last_onset_at = 0.0
        self._last_timestamp = None

    def configure(self, settings: AudioAnalysisSettings) -> None:
        settings.normalize()
        self.settings = settings

    def _smooth(self, key: str, value: float, dt: float) -> float:
        previous = self._smoothed.get(key, value)
        tau_ms = (
            self.settings.attack_ms if value > previous else self.settings.release_ms
        )
        tau = max(0.001, tau_ms / 1000.0)
        alpha = 1.0 - math.exp(-max(0.0, dt) / tau)
        result = previous + alpha * (value - previous)
        self._smoothed[key] = result
        return result

    def _estimate_tempo(self, now: float) -> tuple[float | None, float]:
        if len(self._beat_intervals) < 3:
            return None, 0.0
        intervals = np.asarray(self._beat_intervals, dtype=np.float64)
        median = float(np.median(intervals))
        if median <= 0:
            return None, 0.0
        deviation = float(np.median(np.abs(intervals - median)))
        consistency = max(0.0, 1.0 - (deviation / max(0.001, median * 0.22)))
        freshness = max(0.0, 1.0 - (now - (self._last_beat_at or now)) / 4.0)
        confidence = min(1.0, consistency * freshness * min(1.0, len(intervals) / 6.0))
        bpm = 60.0 / median
        while bpm < self.settings.beat_min_bpm:
            bpm *= 2.0
        while bpm > self.settings.beat_max_bpm:
            bpm /= 2.0
        if not self.settings.beat_min_bpm <= bpm <= self.settings.beat_max_bpm:
            return None, 0.0
        if confidence < self.settings.beat_confidence_min:
            return None, confidence
        return round(bpm, 1), confidence

    def process(
        self,
        samples: np.ndarray,
        sample_rate: int,
        now: float | None = None,
    ) -> AudioAnalysisFrame:
        stamp = time.monotonic() if now is None else float(now)
        rate = max(1, int(sample_rate))
        data = np.asarray(samples, dtype=np.float32)
        if data.ndim == 2:
            if data.shape[1] > 1:
                # Downmix all captured channels; avoid SoundCard's Windows mono bug.
                mono = np.mean(data, axis=1, dtype=np.float32)
            elif data.shape[1] == 1:
                mono = data[:, 0]
            else:
                mono = np.zeros(0, dtype=np.float32)
        elif data.ndim == 1:
            mono = data
        else:
            raise ValueError("Audio samples must be a one- or two-dimensional array.")
        if mono.size == 0:
            return AudioAnalysisFrame(stamp, rate, 0, 0, 0, 0, 0, 0, None, 0)

        mono = np.nan_to_num(mono, copy=True, nan=0.0, posinf=0.0, neginf=0.0)
        mono = np.clip(mono, -1.0, 1.0)
        frame_seconds = mono.size / rate
        dt = (
            frame_seconds
            if self._last_timestamp is None
            else max(0.001, min(1.0, stamp - self._last_timestamp))
        )
        self._last_timestamp = stamp

        raw_rms = float(np.sqrt(np.mean(np.square(mono, dtype=np.float64))))
        raw_peak = float(np.max(np.abs(mono)))
        sensitivity = self.settings.sensitivity
        rms = min(1.0, raw_rms * sensitivity)
        peak = min(1.0, raw_peak * sensitivity)

        window = np.hanning(mono.size).astype(np.float32)
        spectrum = np.abs(np.fft.rfft(mono * window))
        frequencies = np.fft.rfftfreq(mono.size, d=1.0 / rate)
        spectral_power = np.square(spectrum, dtype=np.float64)
        bands: dict[str, float] = {}
        for name, low_hz, high_hz in (
            ("low", 20.0, 250.0),
            ("mid", 250.0, 2000.0),
            ("high", 2000.0, min(10000.0, rate / 2.0)),
        ):
            mask = (frequencies >= low_hz) & (frequencies < high_hz)
            band_rms = (
                float(np.sqrt(2.0 * np.sum(spectral_power[mask])) / mono.size)
                if np.any(mask)
                else 0.0
            )
            bands[name] = min(1.0, band_rms * sensitivity * 2.0)

        raw_onset = max(
            0.0, (rms - self._previous_rms) / max(0.08, self._previous_rms + 0.02)
        )
        onset = min(1.0, raw_onset)
        self._previous_rms = rms

        if (
            onset >= self.settings.onset_threshold
            and stamp - self._last_onset_at >= 0.22
        ):
            if self._last_beat_at is not None:
                interval = stamp - self._last_beat_at
                minimum_interval = 60.0 / self.settings.beat_max_bpm
                maximum_interval = 60.0 / self.settings.beat_min_bpm * 2.0
                if minimum_interval <= interval <= maximum_interval:
                    self._beat_intervals.append(interval)
            self._last_beat_at = stamp
            self._last_onset_at = stamp

        smoothed = {
            "rms": self._smooth("rms", rms, dt),
            "peak": self._smooth("peak", peak, dt),
            "low": self._smooth("low", bands["low"], dt),
            "mid": self._smooth("mid", bands["mid"], dt),
            "high": self._smooth("high", bands["high"], dt),
            "onset": self._smooth("onset", onset, dt),
        }
        bpm, confidence = self._estimate_tempo(stamp)
        return AudioAnalysisFrame(
            timestamp=stamp,
            sample_rate=rate,
            rms=smoothed["rms"],
            peak=smoothed["peak"],
            low=smoothed["low"],
            mid=smoothed["mid"],
            high=smoothed["high"],
            onset=smoothed["onset"],
            bpm=bpm,
            beat_confidence=confidence,
        )
