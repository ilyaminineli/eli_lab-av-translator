from __future__ import annotations

import logging
import time

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSizePolicy, QWidget

from config import RENDER_TARGET_FPS
from core.application import Application
from core.render_engine import RenderEngine

_LOG = logging.getLogger(__name__)


class PerformanceView(QOpenGLWidget):
    """Qt OpenGL output surface used for preview and external projector windows."""

    render_status_changed = Signal(str)

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self.engine = RenderEngine(application.generator_raster_service)
        application.generator_raster_service.raster_ready.connect(
            self._on_generator_raster_ready
        )
        application.generator_raster_service.raster_failed.connect(
            self._on_generator_raster_failed
        )
        self._initialization_error: str | None = None
        self._last_render_error: str | None = None
        self._last_fps_time = time.perf_counter()
        self._frame_count = 0
        self._render_time_sum_ms = 0.0
        self._upload_time_sum_ms = 0.0
        self._upload_bytes_sum = 0
        self._last_decode_time_ms = 0.0
        self._last_conversion_time_ms = 0.0
        self._last_decoded_frames = 0
        self._last_published_frames = 0
        self._last_dropped_frames = 0
        # This widget is also used inside a narrow dockable local-preview pane.
        # The fullscreen projector window supplies its own unconstrained surface.
        self.setMinimumSize(240, 135)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setObjectName("masterPerformanceView")

        self._timer = QTimer(self)
        interval_ms = max(1, round(1000.0 / max(1, RENDER_TARGET_FPS)))
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.update)
        self._timer.start()

    def _on_generator_raster_ready(
            self, layer_id: str, revision: int, fingerprint: str, pixels
    ) -> None:
        self.engine.accept_generator_raster(
            layer_id, revision, fingerprint, pixels
        )
        self.update()

    def _on_generator_raster_failed(
            self, layer_id: str, revision: int, fingerprint: str, message: str
    ) -> None:
        self.engine.accept_generator_error(
            layer_id, revision, fingerprint, message
        )
        self.update()

    def initializeGL(self) -> None:
        try:
            self.engine.initialize()
            self._initialization_error = None
            self.render_status_changed.emit(
                f"OpenGL ready · {self.engine.renderer_name}"
            )
        except Exception as exc:
            self._initialization_error = str(exc)
            _LOG.exception("Could not initialize the OpenGL renderer")
            self.render_status_changed.emit(f"OpenGL initialization failed · {exc}")

    def paintGL(self) -> None:
        if self._initialization_error:
            self._paint_message(
                "RENDERER INITIALIZATION FAILED",
                self._initialization_error,
            )
            return
        if not self.engine.initialized:
            self._paint_message("INITIALIZING RENDERER", "Waiting for OpenGL context…")
            return

        ratio = self.devicePixelRatioF()
        width = max(1, round(self.width() * ratio))
        height = max(1, round(self.height() * ratio))
        try:
            self.engine.render(
                self.application.composition,
                self.application.current_frames(),
                int(self.defaultFramebufferObject()),
                width,
                height,
                effects=self.application.effects,
                time_seconds=self.application.animation_time(),
            )
        except Exception as exc:
            message = str(exc)
            if message != self._last_render_error:
                _LOG.exception("Render frame failed; keeping the renderer alive for recovery")
                self.render_status_changed.emit(f"Render error · {message}")
            self._last_render_error = message
            self._paint_message("RENDER FRAME FAILED", message)
            return

        if self._last_render_error is not None:
            _LOG.info("Renderer recovered after transient frame error")
            self._last_render_error = None

        self._frame_count += 1
        self._render_time_sum_ms += self.engine.last_render_ms
        self._upload_time_sum_ms += self.engine.last_upload_ms
        self._upload_bytes_sum += self.engine.last_upload_bytes
        elapsed = time.perf_counter() - self._last_fps_time
        if elapsed >= 1.0:
            fps = self._frame_count / elapsed
            average_render_ms = self._render_time_sum_ms / max(1, self._frame_count)
            average_upload_ms = self._upload_time_sum_ms / max(1, self._frame_count)
            stats = self.application.performance_snapshot()
            upload_megabytes_per_second = (
                    self._upload_bytes_sum / max(elapsed, 0.001) / (1024.0 * 1024.0)
            )
            self._frame_count = 0
            self._render_time_sum_ms = 0.0
            self._upload_time_sum_ms = 0.0
            self._upload_bytes_sum = 0
            self._last_fps_time = time.perf_counter()

            decode_time_delta = max(
                0.0, float(stats["decode_time_ms"]) - self._last_decode_time_ms
            )
            conversion_time_delta = max(
                0.0,
                float(stats["conversion_time_ms"]) - self._last_conversion_time_ms,
            )
            decoded_frames_delta = max(
                0, int(stats["decoded_frames"]) - self._last_decoded_frames
            )
            published_frames_delta = max(
                0, int(stats["published_frames"]) - self._last_published_frames
            )
            dropped_frames_delta = max(
                0, int(stats["dropped_frames"]) - self._last_dropped_frames
            )
            self._last_decode_time_ms = float(stats["decode_time_ms"])
            self._last_conversion_time_ms = float(stats["conversion_time_ms"])
            self._last_decoded_frames = int(stats["decoded_frames"])
            self._last_published_frames = int(stats["published_frames"])
            self._last_dropped_frames = int(stats["dropped_frames"])

            decode_ms_per_frame = decode_time_delta / max(1, decoded_frames_delta)
            convert_ms_per_frame = conversion_time_delta / max(1, published_frames_delta)
            status = (
                f"{fps:0.1f} FPS · decode {decode_ms_per_frame:0.1f} "
                f"ms/f · convert {convert_ms_per_frame:0.1f} ms/f · "
                f"render CPU {average_render_ms:0.1f} ms "
                f"(upload {average_upload_ms:0.1f} ms / "
                f"{upload_megabytes_per_second:0.0f} MB/s) · "
                f"{stats['playing_decks']} decks · "
                f"drop {dropped_frames_delta}/s · "
                f"{self.engine.renderer_name}"
            )
            self.render_status_changed.emit(status)

    def _paint_message(self, title: str, detail: str) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#101114"))
        painter.setPen(QColor("#E5E5E8"))
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        painter.setFont(title_font)
        painter.drawText(
            self.rect().adjusted(28, 28, -28, -28),
            0x0001 | 0x0080,
            title,
        )
        painter.setPen(QColor("#A7A9B0"))
        painter.setFont(QFont("Consolas", 9))
        painter.drawText(
            self.rect().adjusted(28, 72, -28, -28),
            0x0001 | 0x0080,
            detail,
        )
        painter.end()

    def shutdown_renderer(self) -> None:
        self._timer.stop()
        try:
            self.application.generator_raster_service.raster_ready.disconnect(
                self._on_generator_raster_ready
            )
            self.application.generator_raster_service.raster_failed.disconnect(
                self._on_generator_raster_failed
            )
        except (RuntimeError, TypeError):
            pass
        if self.engine.initialized and self.isValid():
            self.makeCurrent()
            try:
                self.engine.release()
            finally:
                self.doneCurrent()


class AspectRatioPreview(QWidget):
    """Keep the local performance canvas at the project's 16:9 aspect ratio."""

    def __init__(
            self,
            view: PerformanceView,
            parent=None,
            aspect_ratio: float = 16.0 / 9.0,
    ) -> None:
        super().__init__(parent)
        self.view = view
        self.aspect_ratio = max(0.1, float(aspect_ratio))
        self.setMinimumSize(0, 0)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setStyleSheet("background-color: #000000;")
        self.view.setParent(self)
        self.view.setMinimumSize(0, 0)
        self._fit_view()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._fit_view()

    def _fit_view(self) -> None:
        bounds = self.contentsRect()
        width = max(1, bounds.width())
        height = max(1, round(width / self.aspect_ratio))
        if height > bounds.height():
            height = max(1, bounds.height())
            width = max(1, round(height * self.aspect_ratio))
        x = bounds.x() + (bounds.width() - width) // 2
        y = bounds.y() + (bounds.height() - height) // 2
        self.view.setGeometry(x, y, width, height)

