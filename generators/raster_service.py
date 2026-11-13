from __future__ import annotations

import logging
import threading
import time
from collections import OrderedDict
from typing import Any

from PySide6.QtCore import QObject, Signal

from generators.rasterizer import GENERATOR_HEIGHT, GENERATOR_WIDTH, GeneratorRasterizer

_LOG = logging.getLogger(__name__)
_RasterJob = tuple[int, str, str, dict[str, Any], int, int]


class GeneratorRasterService(QObject):
    """Single-worker, latest-request-wins CPU raster service shared by outputs.

    Pending work is coalesced by layer. Text jobs are rate-limited separately
    from other generators. The worker creates CPU pixels only; each renderer
    uploads completed snapshots while its own OpenGL context is current.
    """

    raster_started = Signal(str, int)
    raster_ready = Signal(str, int, str, object)
    raster_failed = Signal(str, int, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._latest_revision: dict[str, int] = {}
        self._latest_fingerprint: dict[str, str] = {}
        self._latest_dimensions: dict[str, tuple[int, int]] = {}
        self._latest_snapshots: dict[str, tuple[str, dict[str, Any], int, int]] = {}
        self._completed: dict[str, tuple[str, Any]] = {}
        self._failed: dict[str, tuple[int, str]] = {}
        self._pending_requests: OrderedDict[str, _RasterJob] = OrderedDict()
        self._active_requests: dict[str, tuple[int, str]] = {}
        self._deferred: set[str] = set()
        self._frozen: set[str] = set()
        self._phase: dict[str, str] = {}
        self._live_preview_enabled = True
        self._text_preview_scale = 0.5
        self._max_text_update_hz = 4.0
        self._next_text_update_at = 0.0
        self._keep_last_valid_texture = True
        self._cache_cleanup_pending = False
        self._closed = False
        self._worker_rasterizer = GeneratorRasterizer()
        self._worker_thread = threading.Thread(
            target=self._worker_loop, name="generator-raster", daemon=True
        )
        self._worker_thread.start()

    def _dimensions(self, generator_type: str, *, full_resolution: bool = False) -> tuple[int, int]:
        if generator_type != "text":
            return GENERATOR_WIDTH, GENERATOR_HEIGHT
        scale = 1.0 if full_resolution else self._text_preview_scale
        return (max(320, round(GENERATOR_WIDTH * scale)), max(180, round(GENERATOR_HEIGHT * scale)))

    def fingerprint_for(self, layer_id: str, generator_type: str, settings: dict[str, Any]) -> str:
        """Fingerprint using the resolution currently assigned to this layer."""
        with self._lock:
            width, height = self._latest_dimensions.get(
                layer_id, self._dimensions(generator_type)
            )
        return GeneratorRasterizer.fingerprint_settings(
            generator_type, settings, width=width, height=height
        )

    def set_text_preview_scale(self, scale: float) -> None:
        with self._condition:
            self._text_preview_scale = min(1.0, max(0.25, float(scale)))

    def set_max_text_update_hz(self, value: float) -> None:
        with self._condition:
            self._max_text_update_hz = min(20.0, max(1.0, float(value)))
            self._condition.notify_all()

    def set_live_preview_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        replays = []
        with self._condition:
            if self._live_preview_enabled == enabled:
                return
            self._live_preview_enabled = enabled
            if not enabled:
                for layer_id, snapshot in tuple(self._latest_snapshots.items()):
                    generator_type, _settings, _width, _height = snapshot
                    if generator_type != "text":
                        continue
                    self._latest_revision[layer_id] = (
                            self._latest_revision.get(layer_id, 0) + 1
                    )
                    self._pending_requests.pop(layer_id, None)
                    self._deferred.add(layer_id)
                    self._phase[layer_id] = (
                        "frozen" if layer_id in self._frozen else "editing"
                    )
            else:
                replays = self._queue_deferred_locked()
            self._condition.notify_all()
        for replay in replays:
            self.raster_ready.emit(*replay)

    def set_frozen(self, layer_id: str, frozen: bool) -> None:
        replay = None
        with self._condition:
            if frozen:
                self._frozen.add(layer_id)
                if layer_id in self._latest_snapshots:
                    self._latest_revision[layer_id] = (
                            self._latest_revision.get(layer_id, 0) + 1
                    )
                    self._pending_requests.pop(layer_id, None)
                    self._deferred.add(layer_id)
                self._phase[layer_id] = "frozen"
            else:
                self._frozen.discard(layer_id)
                if layer_id in self._deferred and self._live_preview_enabled:
                    replay = self._queue_layer_locked(layer_id)
                elif layer_id in self._deferred:
                    self._phase[layer_id] = "editing"
            self._condition.notify_all()
        if replay is not None:
            self.raster_ready.emit(*replay)

    def set_keep_last_valid_texture(self, enabled: bool) -> None:
        with self._lock:
            self._keep_last_valid_texture = bool(enabled)

    @property
    def keep_last_valid_texture(self) -> bool:
        with self._lock:
            return self._keep_last_valid_texture

    def status(self, layer_id: str) -> str:
        with self._lock:
            return self._phase.get(layer_id, "ready")

    def is_frozen(self, layer_id: str) -> bool:
        with self._lock:
            return layer_id in self._frozen

    def _queue_layer_locked(
            self, layer_id: str
    ) -> tuple[str, int, str, Any] | None:
        snapshot = self._latest_snapshots.get(layer_id)
        fingerprint = self._latest_fingerprint.get(layer_id)
        if snapshot is None or not fingerprint or self._closed:
            return None
        completed = self._completed.get(layer_id)
        if completed is not None and completed[0] == fingerprint:
            self._phase[layer_id] = "ready"
            self._deferred.discard(layer_id)
            return (
                layer_id,
                self._latest_revision.get(layer_id, 0),
                fingerprint,
                completed[1],
            )
        generator_type, settings, width, height = snapshot
        if layer_id in self._frozen:
            self._phase[layer_id] = "frozen"
            self._deferred.add(layer_id)
            return None
        if generator_type == "text" and not self._live_preview_enabled:
            self._phase[layer_id] = "editing"
            self._deferred.add(layer_id)
            return None
        revision = self._latest_revision.get(layer_id, 0)
        self._pending_requests[layer_id] = (
            revision, fingerprint, generator_type, dict(settings), width, height
        )
        self._deferred.discard(layer_id)
        self._phase[layer_id] = "rasterizing"
        self._condition.notify()
        return None

    def _queue_deferred_locked(self) -> list[tuple[str, int, str, Any]]:
        replays = []
        for layer_id in tuple(self._deferred):
            if layer_id not in self._frozen:
                replay = self._queue_layer_locked(layer_id)
                if replay is not None:
                    replays.append(replay)
        return replays

    def request(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
            *,
            force: bool = False,
            full_resolution: bool | None = None,
    ) -> tuple[str, int]:
        """Queue/replay a snapshot; force bypasses Live Preview, never Freeze."""
        snapshot = dict(settings)
        with self._condition:
            if full_resolution is None and layer_id in self._latest_dimensions:
                width, height = self._latest_dimensions[layer_id]
            else:
                width, height = self._dimensions(
                    generator_type,
                    full_resolution=bool(full_resolution),
                )
            fingerprint = GeneratorRasterizer.fingerprint_settings(
                generator_type, snapshot, width=width, height=height
            )
            revision = self._latest_revision.get(layer_id, 0)
            if self._closed:
                return fingerprint, revision
            same_snapshot = self._latest_fingerprint.get(layer_id) == fingerprint
            self._latest_snapshots[layer_id] = (generator_type, snapshot, width, height)
            self._latest_dimensions[layer_id] = (width, height)
            if not same_snapshot:
                revision += 1
                self._latest_revision[layer_id] = revision
                self._latest_fingerprint[layer_id] = fingerprint
                self._completed.pop(layer_id, None)
                self._failed.pop(layer_id, None)
                self._pending_requests.pop(layer_id, None)
                self._deferred.discard(layer_id)
            if layer_id in self._frozen:
                self._pending_requests.pop(layer_id, None)
                self._deferred.add(layer_id)
                self._phase[layer_id] = "frozen"
                return fingerprint, revision
            if generator_type == "text" and not self._live_preview_enabled and not force:
                self._pending_requests.pop(layer_id, None)
                self._deferred.add(layer_id)
                self._phase[layer_id] = "editing"
                return fingerprint, revision
            completed = self._completed.get(layer_id)
            if same_snapshot and completed is not None and completed[0] == fingerprint:
                replay = completed[1]
                self._phase[layer_id] = "ready"
            else:
                replay = None
                active = self._active_requests.get(layer_id) == (revision, fingerprint)
                pending = layer_id in self._pending_requests
                failed = self._failed.get(layer_id) == (revision, fingerprint)
                if same_snapshot and failed and force:
                    revision += 1
                    self._latest_revision[layer_id] = revision
                    self._failed.pop(layer_id, None)
                    failed = False
                if same_snapshot and (active or pending or failed):
                    return fingerprint, revision
                self._pending_requests[layer_id] = (
                    revision, fingerprint, generator_type, snapshot, width, height
                )
                self._phase[layer_id] = "rasterizing"
                self._condition.notify()
        if replay is not None:
            self.raster_ready.emit(layer_id, revision, fingerprint, replay)
        return fingerprint, revision

    def has_latest_snapshot(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
    ) -> bool:
        fingerprint = self.fingerprint_for(layer_id, generator_type, settings)
        with self._lock:
            return not self._closed and self._latest_fingerprint.get(layer_id) == fingerprint

    def is_current(self, layer_id: str, revision: int, fingerprint: str) -> bool:
        with self._lock:
            return (
                    not self._closed
                    and self._latest_revision.get(layer_id) == revision
                    and self._latest_fingerprint.get(layer_id) == fingerprint
            )

    def _worker_loop(self) -> None:
        while True:
            cache_layer_ids: set[str] | None = None
            with self._condition:
                while not self._closed:
                    if self._cache_cleanup_pending:
                        # The rasterizer cache is worker-owned. Snapshot the
                        # surviving layer IDs here so eviction happens on the
                        # same thread that reads/writes its pixel arrays.
                        cache_layer_ids = set(self._latest_snapshots)
                        self._cache_cleanup_pending = False
                        break
                    now = time.monotonic()
                    selected_layer = None
                    for candidate_id, candidate_job in self._pending_requests.items():
                        if candidate_job[2] != "text" or now >= self._next_text_update_at:
                            selected_layer = candidate_id
                            break
                    if selected_layer is not None:
                        break
                    if not self._pending_requests:
                        self._condition.wait()
                    else:
                        self._condition.wait(max(0.001, self._next_text_update_at - now))
                if self._closed:
                    # Release all retained CPU pixel arrays on the owner thread.
                    self._worker_rasterizer.clear()
                    return
                if cache_layer_ids is None:
                    layer_id = selected_layer
                    job = self._pending_requests.pop(layer_id)
                    revision, expected_fingerprint, generator_type, settings, width, height = job
                    self._active_requests[layer_id] = (revision, expected_fingerprint)
                    if generator_type == "text":
                        self._next_text_update_at = (
                                time.monotonic() + 1.0 / self._max_text_update_hz
                        )
            if cache_layer_ids is not None:
                self._worker_rasterizer.remove_missing(cache_layer_ids)
                continue
            self.raster_started.emit(layer_id, revision)
            try:
                fingerprint, pixels = self._worker_rasterizer.render_settings(
                    layer_id,
                    generator_type,
                    settings,
                    width=width,
                    height=height,
                )
                if fingerprint != expected_fingerprint:
                    raise RuntimeError("Generator rasterizer returned an unexpected fingerprint")
            except Exception as exc:
                with self._condition:
                    current = (
                            not self._closed
                            and self._latest_revision.get(layer_id) == revision
                            and self._latest_fingerprint.get(layer_id) == expected_fingerprint
                    )
                    if self._active_requests.get(layer_id) == (revision, expected_fingerprint):
                        self._active_requests.pop(layer_id, None)
                    if current:
                        self._failed[layer_id] = (revision, expected_fingerprint)
                        self._phase[layer_id] = "failed"
                if current:
                    self.raster_failed.emit(layer_id, revision, expected_fingerprint, str(exc))
                    _LOG.exception("Generator rasterization failed for %s", layer_id)
                continue
            with self._condition:
                current = (
                        not self._closed
                        and self._latest_revision.get(layer_id) == revision
                        and self._latest_fingerprint.get(layer_id) == expected_fingerprint
                )
                if self._active_requests.get(layer_id) == (revision, expected_fingerprint):
                    self._active_requests.pop(layer_id, None)
                if current:
                    self._completed[layer_id] = (fingerprint, pixels)
                    self._failed.pop(layer_id, None)
                    self._phase[layer_id] = "ready"
            if current:
                self.raster_ready.emit(layer_id, revision, fingerprint, pixels)

    def invalidate(self, layer_id: str) -> None:
        with self._condition:
            self._latest_revision[layer_id] = self._latest_revision.get(layer_id, 0) + 1
            self._latest_fingerprint.pop(layer_id, None)
            self._latest_dimensions.pop(layer_id, None)
            self._latest_snapshots.pop(layer_id, None)
            self._completed.pop(layer_id, None)
            self._failed.pop(layer_id, None)
            self._pending_requests.pop(layer_id, None)
            self._deferred.discard(layer_id)
            self._frozen.discard(layer_id)
            self._phase.pop(layer_id, None)
            self._cache_cleanup_pending = True
            self._condition.notify_all()

    def invalidate_missing(self, active_layer_ids: set[str]) -> None:
        with self._condition:
            known_ids = (
                    set(self._latest_revision)
                    | set(self._latest_snapshots)
                    | set(self._completed)
            )
            for layer_id in known_ids - active_layer_ids:
                self._latest_revision[layer_id] = self._latest_revision.get(layer_id, 0) + 1
                self._latest_fingerprint.pop(layer_id, None)
                self._latest_dimensions.pop(layer_id, None)
                self._latest_snapshots.pop(layer_id, None)
                self._completed.pop(layer_id, None)
                self._failed.pop(layer_id, None)
                self._pending_requests.pop(layer_id, None)
                self._deferred.discard(layer_id)
                self._frozen.discard(layer_id)
                self._phase.pop(layer_id, None)
            if known_ids - active_layer_ids:
                self._cache_cleanup_pending = True
            self._condition.notify_all()

    def shutdown(self) -> None:
        with self._condition:
            if self._closed:
                return
            self._closed = True
            self._latest_fingerprint.clear()
            self._latest_dimensions.clear()
            self._latest_snapshots.clear()
            self._completed.clear()
            self._failed.clear()
            self._pending_requests.clear()
            self._deferred.clear()
            self._frozen.clear()
            self._condition.notify_all()
