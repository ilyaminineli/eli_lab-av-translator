from __future__ import annotations

import logging
import threading
from collections import OrderedDict
from typing import Any

from PySide6.QtCore import QObject, Signal

from generators.rasterizer import GeneratorRasterizer

_LOG = logging.getLogger(__name__)

_RasterJob = tuple[int, str, str, dict[str, Any]]


class GeneratorRasterService(QObject):
    """Single-worker, latest-request-wins CPU raster service shared by outputs.

    Pending work is coalesced by layer in an ordered map. A text edit replaces
    that layer's pending snapshot instead of adding another executor work item.
    The worker creates CPU-side NumPy pixels only; renderers upload them while
    their own OpenGL context is current.
    """

    raster_ready = Signal(str, int, str, object)
    raster_failed = Signal(str, int, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._latest_revision: dict[str, int] = {}
        self._latest_fingerprint: dict[str, str] = {}
        self._completed: dict[str, tuple[str, Any]] = {}
        self._failed: dict[str, tuple[int, str]] = {}
        self._pending_requests: OrderedDict[str, _RasterJob] = OrderedDict()
        self._active_requests: dict[str, tuple[int, str]] = {}
        self._closed = False
        self._rasterizer = GeneratorRasterizer()
        self._worker_rasterizer = GeneratorRasterizer()
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="generator-raster",
            daemon=True,
        )
        self._worker_thread.start()

    def request(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
    ) -> tuple[str, int]:
        """Queue or replay a settings snapshot and return its layer revision."""
        snapshot = dict(settings)
        fingerprint = self._rasterizer.fingerprint_settings(
            generator_type, snapshot
        )
        replay = None
        with self._condition:
            revision = self._latest_revision.get(layer_id, 0)
            if self._closed:
                return fingerprint, revision

            if self._latest_fingerprint.get(layer_id) == fingerprint:
                completed = self._completed.get(layer_id)
                if completed is not None and completed[0] == fingerprint:
                    replay = completed[1]
                elif (
                        layer_id in self._pending_requests
                        or self._active_requests.get(layer_id) == (
                            revision, fingerprint
                        )
                        or self._failed.get(layer_id) == (revision, fingerprint)
                ):
                    # Identical snapshots are already pending, running, or failed.
                    return fingerprint, revision
                else:
                    # No matching work exists; allow an explicit retry.
                    revision += 1
                    self._latest_revision[layer_id] = revision
                    self._failed.pop(layer_id, None)
            else:
                revision += 1
                self._latest_revision[layer_id] = revision
                self._latest_fingerprint[layer_id] = fingerprint
                self._completed.pop(layer_id, None)
                self._failed.pop(layer_id, None)

            if replay is None:
                # Assignment replaces any previous pending snapshot for this
                # layer without changing its queue position. At most one pending
                # job per layer can exist, regardless of typing speed.
                self._pending_requests[layer_id] = (
                    revision, fingerprint, generator_type, snapshot
                )
                self._condition.notify()

        if replay is not None:
            # A newly opened renderer can acquire the last CPU snapshot without
            # another QPainter pass.
            self.raster_ready.emit(layer_id, revision, fingerprint, replay)
        return fingerprint, revision

    def has_latest_snapshot(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
    ) -> bool:
        """Return whether the latest request already represents this static raster."""
        fingerprint = self._rasterizer.fingerprint_settings(
            generator_type, settings
        )
        with self._lock:
            return (
                not self._closed
                and self._latest_fingerprint.get(layer_id) == fingerprint
            )

    def is_current(self, layer_id: str, revision: int, fingerprint: str) -> bool:
        """Return whether a completion matches the newest requested snapshot."""
        with self._lock:
            return (
                not self._closed
                and self._latest_revision.get(layer_id) == revision
                and self._latest_fingerprint.get(layer_id) == fingerprint
            )

    def _worker_loop(self) -> None:
        while True:
            with self._condition:
                while not self._closed and not self._pending_requests:
                    self._condition.wait()
                if self._closed:
                    return
                layer_id, job = self._pending_requests.popitem(last=False)
                revision, expected_fingerprint, generator_type, settings = job
                self._active_requests[layer_id] = (
                    revision, expected_fingerprint
                )

            try:
                fingerprint, pixels = self._worker_rasterizer.render_settings(
                    layer_id, generator_type, settings
                )
                if fingerprint != expected_fingerprint:
                    raise RuntimeError(
                        "Generator rasterizer returned an unexpected fingerprint"
                    )
            except Exception as exc:
                with self._condition:
                    current = (
                        not self._closed
                        and self._latest_revision.get(layer_id) == revision
                        and self._latest_fingerprint.get(layer_id)
                        == expected_fingerprint
                    )
                    if self._active_requests.get(layer_id) == (
                            revision, expected_fingerprint
                    ):
                        self._active_requests.pop(layer_id, None)
                    if current:
                        self._failed[layer_id] = (revision, expected_fingerprint)
                if current:
                    self.raster_failed.emit(
                        layer_id, revision, expected_fingerprint, str(exc)
                    )
                    _LOG.exception(
                        "Generator rasterization failed for %s", layer_id
                    )
                continue

            with self._condition:
                current = (
                    not self._closed
                    and self._latest_revision.get(layer_id) == revision
                    and self._latest_fingerprint.get(layer_id)
                    == expected_fingerprint
                )
                if self._active_requests.get(layer_id) == (
                        revision, expected_fingerprint
                ):
                    self._active_requests.pop(layer_id, None)
                if current:
                    self._completed[layer_id] = (fingerprint, pixels)
                    self._failed.pop(layer_id, None)
            if current:
                self.raster_ready.emit(
                    layer_id, revision, fingerprint, pixels
                )

    def invalidate(self, layer_id: str) -> None:
        with self._condition:
            self._latest_revision[layer_id] = (
                self._latest_revision.get(layer_id, 0) + 1
            )
            self._latest_fingerprint.pop(layer_id, None)
            self._completed.pop(layer_id, None)
            self._failed.pop(layer_id, None)
            self._pending_requests.pop(layer_id, None)

    def invalidate_missing(self, active_layer_ids: set[str]) -> None:
        with self._condition:
            for layer_id in set(self._latest_revision) - active_layer_ids:
                self._latest_revision[layer_id] = (
                    self._latest_revision.get(layer_id, 0) + 1
                )
                self._latest_fingerprint.pop(layer_id, None)
                self._completed.pop(layer_id, None)
                self._failed.pop(layer_id, None)
                self._pending_requests.pop(layer_id, None)

    def shutdown(self) -> None:
        with self._condition:
            if self._closed:
                return
            self._closed = True
            self._latest_fingerprint.clear()
            self._completed.clear()
            self._failed.clear()
            self._pending_requests.clear()
            self._condition.notify_all()
