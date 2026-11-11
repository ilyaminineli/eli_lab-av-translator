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

    raster_ready = Signal(str, str, object)
    raster_failed = Signal(str, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="generator-raster",
        )
        self._lock = threading.Lock()
        self._generation: dict[str, int] = {}
        self._latest_fingerprint: dict[str, str] = {}
        self._closed = False
        self._rasterizer = GeneratorRasterizer()

    def request(
            self,
            layer_id: str,
            generator_type: str,
            settings: dict[str, Any],
    ) -> str:
        """Queue a normalized-by-rasterizer snapshot; supersede older requests."""
        snapshot = dict(settings)
        fingerprint = self._rasterizer.fingerprint_settings(
            generator_type, snapshot
        )
        with self._lock:
            if self._closed:
                return fingerprint
            generation = self._generation.get(layer_id, 0) + 1
            self._generation[layer_id] = generation
            self._latest_fingerprint[layer_id] = fingerprint

        future = self._executor.submit(
            self._rasterizer.render_settings,
            layer_id,
            generator_type,
            snapshot,
        )
        future.add_done_callback(
            lambda result, key=layer_id, version=generation:
            self._finish(key, version, result)
        )
        return fingerprint

    def _finish(
            self,
            layer_id: str,
            generation: int,
            future: Future,
    ) -> None:
        try:
            fingerprint, pixels = future.result()
        except Exception as exc:
            with self._lock:
                current = not self._closed and (
                    self._generation.get(layer_id) == generation
                )
            if current:
                self.raster_failed.emit(layer_id, "", str(exc))
            _LOG.exception("Generator rasterization failed for %s", layer_id)
            return

        with self._lock:
            current = not self._closed and (
                self._generation.get(layer_id) == generation
                and self._latest_fingerprint.get(layer_id) == fingerprint
            )
        if current:
            self.raster_ready.emit(layer_id, fingerprint, pixels)

    def invalidate(self, layer_id: str) -> None:
        with self._lock:
            self._generation[layer_id] = self._generation.get(layer_id, 0) + 1
            self._latest_fingerprint.pop(layer_id, None)

    def invalidate_missing(self, active_layer_ids: set[str]) -> None:
        with self._lock:
            for layer_id in set(self._generation) - active_layer_ids:
                self._generation[layer_id] = self._generation.get(layer_id, 0) + 1
                self._latest_fingerprint.pop(layer_id, None)

    def shutdown(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._generation.clear()
            self._latest_fingerprint.clear()
        self._executor.shutdown(wait=False, cancel_futures=True)
