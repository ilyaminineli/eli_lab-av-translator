from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from PySide6.QtCore import QObject, Signal

from generators.rasterizer import GeneratorRasterizer

_LOG = logging.getLogger(__name__)


class GeneratorRasterService(QObject):
    """Single-worker, latest-request-wins CPU raster service shared by outputs.

    The worker sees only immutable settings snapshots and creates CPU-side NumPy
    pixels. Renderers consume completed snapshots and upload them only while
    their own OpenGL context is current.
    """

    raster_ready = Signal(str, int, str, object)
    raster_failed = Signal(str, int, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="generator-raster",
        )
        self._lock = threading.Lock()
        self._latest_revision: dict[str, int] = {}
        self._latest_fingerprint: dict[str, str] = {}
        self._completed: dict[str, tuple[str, Any]] = {}
        self._futures: dict[str, Future] = {}
        self._closed = False
        self._rasterizer = GeneratorRasterizer()
        self._worker_rasterizer = GeneratorRasterizer()

    def request(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
    ) -> tuple[str, int]:
        """Request a snapshot and return its per-layer, monotonically increasing revision.

        A new fingerprint advances the revision immediately, before cancellation
        or submission. This makes older completions stale as soon as a committed
        text/font update reaches the service, even if the next paint has not run.
        """
        snapshot = dict(settings)
        fingerprint = self._rasterizer.fingerprint_settings(
            generator_type, snapshot
        )
        replay = None
        previous_to_cancel = None
        with self._lock:
            if self._closed:
                return fingerprint, self._latest_revision.get(layer_id, 0)
            if self._latest_fingerprint.get(layer_id) == fingerprint:
                revision = self._latest_revision.get(layer_id, 0)
                completed = self._completed.get(layer_id)
                if completed is not None and completed[0] == fingerprint:
                    replay = completed[1]
                else:
                    # The identical snapshot is already queued or running.
                    return fingerprint, revision
            else:
                revision = self._latest_revision.get(layer_id, 0) + 1
                self._latest_revision[layer_id] = revision
                self._latest_fingerprint[layer_id] = fingerprint
                self._completed.pop(layer_id, None)
                previous = self._futures.get(layer_id)
                if previous is not None and not previous.done():
                    previous_to_cancel = previous

        if previous_to_cancel is not None:
            # Future callbacks can run synchronously inside cancel(), so never
            # cancel while holding the service lock.
            previous_to_cancel.cancel()

        if replay is not None:
            # A newly opened projector/preview renderer must be able to acquire
            # the last successful CPU snapshot without another QPainter pass.
            self.raster_ready.emit(layer_id, revision, fingerprint, replay)
            return fingerprint, revision

        future = self._executor.submit(
            self._worker_rasterizer.render_settings,
            layer_id,
            generator_type,
            snapshot,
        )
        with self._lock:
            if (
                    not self._closed
                    and self._latest_revision.get(layer_id) == revision
                    and self._latest_fingerprint.get(layer_id) == fingerprint
            ):
                self._futures[layer_id] = future
        future.add_done_callback(
            lambda result, key=layer_id, version=revision, expected=fingerprint:
            self._finish(key, version, expected, result)
        )
        return fingerprint, revision

    def is_current(self, layer_id: str, revision: int, fingerprint: str) -> bool:
        """Return whether a completion still matches the newest requested snapshot."""
        with self._lock:
            return (
                not self._closed
                and self._latest_revision.get(layer_id) == revision
                and self._latest_fingerprint.get(layer_id) == fingerprint
            )

    def _finish(
            self,
            layer_id: str,
            revision: int,
            expected_fingerprint: str,
            future: Future,
    ) -> None:
        try:
            fingerprint, pixels = future.result()
        except Exception as exc:
            with self._lock:
                current = (
                    not self._closed
                    and self._latest_revision.get(layer_id) == revision
                    and self._latest_fingerprint.get(layer_id) == expected_fingerprint
                )
                if self._futures.get(layer_id) is future:
                    self._futures.pop(layer_id, None)
            if current:
                from concurrent.futures import CancelledError

                if not isinstance(exc, CancelledError):
                    self.raster_failed.emit(
                        layer_id, revision, expected_fingerprint, str(exc)
                    )
                    _LOG.exception("Generator rasterization failed for %s", layer_id)
            return

        with self._lock:
            current = (
                not self._closed
                and self._latest_revision.get(layer_id) == revision
                and self._latest_fingerprint.get(layer_id) == expected_fingerprint
                and fingerprint == expected_fingerprint
            )
            if self._futures.get(layer_id) is future:
                self._futures.pop(layer_id, None)
            if current:
                self._completed[layer_id] = (fingerprint, pixels)
        if current:
            self.raster_ready.emit(layer_id, revision, fingerprint, pixels)

    def invalidate(self, layer_id: str) -> None:
        with self._lock:
            self._latest_revision[layer_id] = self._latest_revision.get(layer_id, 0) + 1
            self._latest_fingerprint.pop(layer_id, None)
            self._completed.pop(layer_id, None)
            future = self._futures.pop(layer_id, None)
        if future is not None:
            future.cancel()

    def invalidate_missing(self, active_layer_ids: set[str]) -> None:
        futures_to_cancel: list[Future] = []
        with self._lock:
            for layer_id in set(self._latest_revision) - active_layer_ids:
                self._latest_revision[layer_id] = self._latest_revision.get(layer_id, 0) + 1
                self._latest_fingerprint.pop(layer_id, None)
                self._completed.pop(layer_id, None)
                future = self._futures.pop(layer_id, None)
                if future is not None:
                    futures_to_cancel.append(future)
        for future in futures_to_cancel:
            future.cancel()

    def shutdown(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._latest_revision.clear()
            self._latest_fingerprint.clear()
            self._completed.clear()
            futures = tuple(self._futures.values())
            self._futures.clear()
        for future in futures:
            future.cancel()
        self._executor.shutdown(wait=False, cancel_futures=True)
