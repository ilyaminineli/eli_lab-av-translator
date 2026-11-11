from __future__ import annotations

import logging
import time
from typing import Any

from config import OPENGL_REQUIREMENT
from core.composition import Composition
from effects.settings import EffectSettings
from generators.rasterizer import GeneratorRasterizer
from rendering.compositor import Compositor

_LOG = logging.getLogger(__name__)


class RenderEngine:
    """Owns per-window ModernGL resources and reports CPU-side render costs."""

    def __init__(self, raster_service=None) -> None:
        self.context: Any | None = None
        self.compositor: Compositor | None = None
        self.initialized = False
        self.renderer_name = "Not initialized"
        self.version_code = 0
        self._uploaded_revisions: dict[str, int] = {}
        self.last_render_ms = 0.0
        self.last_upload_ms = 0.0
        self.last_composite_ms = 0.0
        self.last_upload_bytes = 0
        self.raster_service = raster_service
        # Keep shader phase small and stable during long performances.
        self._time_origin = time.perf_counter()
        self._generator_signatures: dict[str, str] = {}
        self._generator_sources: dict[str, str] = {}
        self._generator_errors: dict[str, str] = {}
        self._pending_generator_textures: dict[str, tuple[str, Any]] = {}
        self._generator_requested: dict[str, str] = {}
        self._pending_generator_errors: dict[str, str] = {}
        self._active_generator_ids: set[str] = set()

    def accept_generator_raster(
            self,
            layer_id: str,
            fingerprint: str,
            pixels: Any,
    ) -> None:
        if layer_id not in self._active_generator_ids:
            return
        self._pending_generator_textures[layer_id] = (fingerprint, pixels)
        self._generator_requested.pop(layer_id, None)
        self._pending_generator_errors.pop(layer_id, None)

    def accept_generator_error(self, layer_id: str, message: str) -> None:
        if layer_id not in self._active_generator_ids:
            return
        self._generator_requested.pop(layer_id, None)
        self._pending_generator_errors[layer_id] = message

    def initialize(self) -> None:
        try:
            import moderngl
        except ImportError as exc:
            raise RuntimeError(
                "ModernGL is not installed. Install requirements-dev.txt or requirements.txt."
            ) from exc

        # QOpenGLWidget.initializeGL makes Qt's context current before this call.
        self.context = moderngl.create_context(require=OPENGL_REQUIREMENT)
        self.compositor = Compositor(self.context)
        info = self.context.info
        self.renderer_name = str(info.get("GL_RENDERER", "Unknown renderer"))
        self.version_code = int(info.get("GL_VERSION_CODE", 0))
        self.initialized = True
        _LOG.info(
            "OpenGL initialized: %s (version code %s)",
            self.renderer_name,
            self.version_code,
        )

    def render(
            self,
            composition: Composition,
            frames: dict[str, object],
            target_fbo: int,
            width: int,
            height: int,
            effects: EffectSettings | None = None,
            time_seconds: float | None = None,
    ) -> None:
        if not self.initialized or self.compositor is None:
            return
        render_started = time.perf_counter()
        upload_started = render_started
        uploaded_bytes = 0
        for source_id, snapshot in frames.items():
            revision = int(getattr(snapshot, "revision", -1))
            if revision >= 0 and self._uploaded_revisions.get(source_id) == revision:
                continue
            frame = getattr(snapshot, "frame", snapshot)
            pixels = getattr(frame, "pixels", None)
            if pixels is not None:
                self.compositor.update_texture(source_id, pixels)
                uploaded_bytes += int(getattr(pixels, "nbytes", 0))
                if revision >= 0:
                    self._uploaded_revisions[source_id] = revision
        generator_layers = [
            layer for layer in composition.layers
            if layer.source_type == "generator" and layer.visible
        ]
        active_generator_ids = {layer.id for layer in generator_layers}
        self._active_generator_ids = active_generator_ids
        # CPU rasterization is shared by all output renderers and happens on a
        # worker. This context only uploads completed pixel snapshots.
        for layer_id, message in tuple(self._pending_generator_errors.items()):
            self._generator_errors[layer_id] = message
            self._pending_generator_errors.pop(layer_id, None)
        for layer in generator_layers:
            source_id = layer.source_id or f"generator:{layer.id}"
            if layer.generator_type == "particles":
                self.compositor.remove_texture(source_id)
                self._generator_signatures.pop(layer.id, None)
                self._generator_sources.pop(layer.id, None)
                self._generator_errors.pop(layer.id, None)
                self._pending_generator_textures.pop(layer.id, None)
                continue

            pending = self._pending_generator_textures.get(layer.id)
            if pending is not None:
                fingerprint, pixels = pending
                if self._generator_signatures.get(layer.id) != fingerprint:
                    self.compositor.update_texture(source_id, pixels)
                    uploaded_bytes += int(pixels.nbytes)
                    self._generator_signatures[layer.id] = fingerprint
                    self._generator_sources[layer.id] = source_id
                self._pending_generator_textures.pop(layer.id, None)

            try:
                from generators.rasterizer import GeneratorRasterizer

                fingerprint = GeneratorRasterizer.fingerprint(layer)
            except Exception as exc:
                self._generator_errors[layer.id] = str(exc)
                continue

            if (
                    self._generator_signatures.get(layer.id) == fingerprint
                    or (pending is not None and pending[0] == fingerprint)
                    or self._generator_requested.get(layer.id) == fingerprint
            ):
                continue
            if self.raster_service is not None:
                self._generator_requested[layer.id] = fingerprint
                self.raster_service.request(
                    layer.id,
                    layer.generator_type or "geometry",
                    dict(layer.generator_settings),
                )

        tracked_generator_ids = (
                set(self._generator_signatures) | set(self._generator_errors)
        )
        removed_ids = tracked_generator_ids - active_generator_ids
        for layer_id in removed_ids:
            source_id = self._generator_sources.pop(layer_id, None)
            if source_id:
                self.compositor.remove_texture(source_id)
            self._generator_signatures.pop(layer_id, None)
            self._generator_errors.pop(layer_id, None)
        self._pending_generator_textures = {
            layer_id: value
            for layer_id, value in self._pending_generator_textures.items()
            if layer_id in active_generator_ids
        }
        self._generator_requested = {
            layer_id: value
            for layer_id, value in self._generator_requested.items()
            if layer_id in active_generator_ids
        }

        # Dispose textures for overlay layers removed from the composition.
        active_source_ids = {
            layer.source_id for layer in composition.layers if layer.source_id
        }
        for source_id in tuple(self._uploaded_revisions):
            if source_id not in active_source_ids:
                self.compositor.remove_texture(source_id)
                self._uploaded_revisions.pop(source_id, None)

        composite_started = time.perf_counter()
        self.last_upload_ms = (composite_started - upload_started) * 1000.0
        self.last_upload_bytes = uploaded_bytes
        self.compositor.render(
            composition.layers,
            target_fbo,
            width,
            height,
            effects=effects,
            time_seconds=(max(0.0, float(time_seconds)) if time_seconds is not None
                          else max(0.0, time.perf_counter() - self._time_origin)),
            canvas_width=composition.width,
            canvas_height=composition.height,
        )
        finished = time.perf_counter()
        self.last_composite_ms = (finished - composite_started) * 1000.0
        self.last_render_ms = (finished - render_started) * 1000.0

    def release(self) -> None:
        if self.compositor is not None:
            self.compositor.release()
            self.compositor = None
        self._uploaded_revisions.clear()
        self._generator_signatures.clear()
        self._generator_sources.clear()
        self._generator_errors.clear()
        self._pending_generator_textures.clear()
        self._generator_requested.clear()
        self._pending_generator_errors.clear()
        self._active_generator_ids.clear()
        self.context = None
        self.initialized = False
