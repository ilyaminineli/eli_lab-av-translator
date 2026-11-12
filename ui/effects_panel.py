from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from effects.settings import PRESETS, EffectSettings

_SLIDERS = (
    ("mix", "Effect mix", 0, 100, 100.0),
    ("brightness", "Brightness", -50, 50, 100.0),
    ("exposure", "Exposure", -200, 200, 100.0),
    ("contrast", "Contrast", 25, 225, 100.0),
    ("saturation", "Saturation", 0, 225, 100.0),
    ("gamma", "Gamma", 25, 225, 100.0),
    ("temperature", "Temperature", -100, 100, 100.0),
    ("tint", "Tint", -100, 100, 100.0),
    ("hue", "Hue shift", -180, 180, 1.0),
    ("vignette", "Vignette", 0, 100, 100.0),
    ("grain", "Film grain", 0, 100, 100.0),
    ("scanlines", "Scanlines", 0, 100, 100.0),
    ("chromatic", "RGB split", 0, 100, 100.0),
    ("glitch", "Signal glitch", 0, 100, 100.0),
    ("pixelate", "Pixelation", 0, 100, 100.0),
    ("posterize", "Posterize", 0, 100, 100.0),
    ("invert", "Invert", 0, 100, 100.0),
    ("halftone", "Halftone print", 0, 100, 100.0),
    ("solarize", "Solarization", 0, 100, 100.0),
)

_ADVANCED_SLIDERS = (
    ("transform_mix", "Transform mix", 0, 100, 100.0),
    ("kaleidoscope_slices", "Kaleidoscope slices", 2, 32, 1.0),
    ("kaleidoscope_rotation", "Kaleidoscope rotation", -180, 180, 1.0),
    ("kaleidoscope_zoom", "Kaleidoscope zoom", 25, 200, 100.0),
    ("mosaic_tiles", "Mosaic tile count", 4, 256, 1.0),
    ("pixel_sort_amount", "Scan displacement amount", 0, 100, 100.0),
    ("pixel_sort_threshold", "Sort brightness threshold", 0, 100, 100.0),
    ("displacement_amount", "Displacement amount", -100, 100, 100.0),
    ("displacement_scale", "Displacement map scale", 25, 400, 100.0),
    ("edge_amount", "Edge extraction", 0, 100, 100.0),
    ("dither", "Ordered dithering", 0, 100, 100.0),
    ("feedback_amount", "Feedback amount", 0, 100, 100.0),
    ("feedback_decay", "Feedback decay", 0, 100, 100.0),
    ("feedback_zoom", "Feedback zoom", 50, 200, 100.0),
    ("feedback_rotation", "Feedback rotation", -180, 180, 1.0),
    ("feedback_translate_x", "Feedback X offset", -25, 25, 100.0),
    ("feedback_translate_y", "Feedback Y offset", -25, 25, 100.0),
    ("feedback_color_shift", "Feedback colour shift", 0, 100, 100.0),
    ("feedback_distortion", "Feedback distortion", 0, 100, 100.0),
    ("feedback_motion_warp", "Motion-driven warp", 0, 100, 100.0),
    ("feedback_datamosh", "Datamosh block displacement", 0, 100, 100.0),
    ("feedback_delay_frames", "Temporal delay (frames)", 0, 3, 1.0),
)


class EffectsPanel(QWidget):
    """Master video look controls; all outputs render the same settings."""

    manual_parameter_changed = Signal(str)

    def __init__(self, settings: EffectSettings, source_provider=None, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.source_provider = source_provider
        self._sliders: dict[str, tuple[QSlider, QLabel, float]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("LOOK"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESETS) + ["Custom"])
        preset_row.addWidget(self.preset_combo, 1)
        self.reset_button = QPushButton("RESET LOOK")
        preset_row.addWidget(self.reset_button)
        root.addLayout(preset_row)

        self.enabled_check = QCheckBox("ENABLE MASTER FILTERS")
        self.enabled_check.setChecked(settings.enabled)
        root.addWidget(self.enabled_check)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        group = QGroupBox("MASTER FILTERS + OVERLAYS")
        form = QFormLayout(group)
        for key, title, low, high, scale in _SLIDERS:
            row = QHBoxLayout()
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(low, high)
            value_label = QLabel("0")
            value_label.setMinimumWidth(42)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            slider.valueChanged.connect(
                lambda value, field=key, multiplier=scale, label=value_label:
                self._value_changed(field, value, multiplier, label)
            )
            row.addWidget(slider, 1)
            row.addWidget(value_label)
            form.addRow(title, row)
            self._sliders[key] = (slider, value_label, scale)
        content_layout.addWidget(group)

        geometry_group = QGroupBox("GEOMETRY + DISPLACEMENT")
        geometry_form = QFormLayout(geometry_group)
        self.transform_mode_combo = QComboBox()
        for label, value in (
                ("Off", "none"),
                ("Kaleidoscope", "kaleidoscope"),
                ("Polar coordinates", "polar"),
                ("Mosaic / tile", "mosaic"),
                ("Directional scan displacement (approx.)", "pixel_sort"),
        ):
            self.transform_mode_combo.addItem(label, value)
        geometry_form.addRow("Transform", self.transform_mode_combo)
        for key, title, low, high, scale in _ADVANCED_SLIDERS[:11]:
            row = QHBoxLayout()
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(low, high)
            value_label = QLabel("0")
            value_label.setMinimumWidth(42)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            slider.valueChanged.connect(
                lambda value, field=key, multiplier=scale, label=value_label:
                self._value_changed(field, value, multiplier, label)
            )
            row.addWidget(slider, 1)
            row.addWidget(value_label)
            geometry_form.addRow(title, row)
            self._sliders[key] = (slider, value_label, scale)
        source_row = QHBoxLayout()
        self.displacement_source_combo = QComboBox()
        self.displacement_refresh_button = QPushButton("REFRESH")
        source_row.addWidget(self.displacement_source_combo, 1)
        source_row.addWidget(self.displacement_refresh_button)
        geometry_form.addRow("Displacement source", source_row)
        self.displacement_luma_check = QCheckBox("Use luma as a two-axis map")
        geometry_form.addRow("", self.displacement_luma_check)
        content_layout.addWidget(geometry_group)

        feedback_group = QGroupBox("GPU FEEDBACK ENGINE")
        feedback_form = QFormLayout(feedback_group)
        self.feedback_enabled_check = QCheckBox("ENABLE TEMPORAL FEEDBACK")
        feedback_form.addRow("", self.feedback_enabled_check)
        for key, title, low, high, scale in _ADVANCED_SLIDERS[11:]:
            row = QHBoxLayout()
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(low, high)
            value_label = QLabel("0")
            value_label.setMinimumWidth(42)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            slider.valueChanged.connect(
                lambda value, field=key, multiplier=scale, label=value_label:
                self._value_changed(field, value, multiplier, label)
            )
            row.addWidget(slider, 1)
            row.addWidget(value_label)
            feedback_form.addRow(title, row)
            self._sliders[key] = (slider, value_label, scale)
        self.feedback_blend_combo = QComboBox()
        self.feedback_blend_combo.addItems(["normal", "add", "screen", "multiply", "difference"])
        feedback_form.addRow("Feedback blend", self.feedback_blend_combo)
        self.feedback_frozen_check = QCheckBox("FREEZE FEEDBACK MEMORY")
        feedback_form.addRow("", self.feedback_frozen_check)
        feedback_buttons = QHBoxLayout()
        self.feedback_reset_button = QPushButton("RESET FEEDBACK BUFFER")
        feedback_buttons.addWidget(self.feedback_reset_button)
        feedback_buttons.addStretch(1)
        feedback_form.addRow("", feedback_buttons)
        content_layout.addWidget(feedback_group)
        content_layout.addStretch(1)

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.preset_combo.currentTextChanged.connect(self._preset_changed)
        self.enabled_check.toggled.connect(self._enabled_changed)
        self.reset_button.clicked.connect(self._reset)
        self.transform_mode_combo.currentIndexChanged.connect(self._transform_mode_changed)
        self.displacement_source_combo.currentIndexChanged.connect(
            self._displacement_source_changed
        )
        self.displacement_refresh_button.clicked.connect(self.sync_sources)
        self.displacement_luma_check.toggled.connect(self._displacement_luma_changed)
        self.feedback_enabled_check.toggled.connect(self._feedback_enabled_changed)
        self.feedback_blend_combo.currentTextChanged.connect(self._feedback_blend_changed)
        self.feedback_frozen_check.toggled.connect(self._feedback_frozen_changed)
        self.feedback_reset_button.clicked.connect(self._reset_feedback)
        self.sync_from_settings()

    def sync_sources(self) -> None:
        selected = self.settings.displacement_source_id
        self.displacement_source_combo.blockSignals(True)
        self.displacement_source_combo.clear()
        self.displacement_source_combo.addItem("OFF", "")
        layers = self.source_provider() if callable(self.source_provider) else []
        for layer in layers:
            source_id = str(getattr(layer, "source_id", "") or "")
            if source_id:
                label = str(getattr(layer, "name", "") or source_id)
                self.displacement_source_combo.addItem(f"{label} · {source_id}", source_id)
        if selected and self.displacement_source_combo.findData(selected) < 0:
            self.displacement_source_combo.addItem(f"{selected} · unavailable", selected)
        index = self.displacement_source_combo.findData(selected)
        self.displacement_source_combo.setCurrentIndex(max(0, index))
        self.displacement_source_combo.blockSignals(False)

    def _transform_mode_changed(self, index: int) -> None:
        self.settings.transform_mode = str(self.transform_mode_combo.itemData(index) or "none")
        self.manual_parameter_changed.emit("master.transform_mode")

    def _displacement_source_changed(self, index: int) -> None:
        self.settings.displacement_source_id = str(
            self.displacement_source_combo.itemData(index) or ""
        )
        self.manual_parameter_changed.emit("master.displacement_source_id")

    def _displacement_luma_changed(self, enabled: bool) -> None:
        self.settings.displacement_luma = bool(enabled)
        self.manual_parameter_changed.emit("master.displacement_luma")

    def _feedback_enabled_changed(self, enabled: bool) -> None:
        self.settings.feedback_enabled = bool(enabled)
        self.manual_parameter_changed.emit("master.feedback_enabled")

    def _feedback_blend_changed(self, mode: str) -> None:
        self.settings.feedback_blend_mode = str(mode).casefold()
        self.manual_parameter_changed.emit("master.feedback_blend_mode")

    def _feedback_frozen_changed(self, frozen: bool) -> None:
        self.settings.feedback_frozen = bool(frozen)
        self.manual_parameter_changed.emit("master.feedback_frozen")

    def _reset_feedback(self) -> None:
        self.settings.feedback_reset_generation += 1
        self.manual_parameter_changed.emit("master.feedback_reset")

    def _preset_changed(self, name: str) -> None:
        if name == "Custom":
            return
        self.settings.apply_preset(name)
        self.sync_from_settings()
        self.manual_parameter_changed.emit("master.*")

    def _enabled_changed(self, enabled: bool) -> None:
        self.settings.enabled = bool(enabled)

    def _value_changed(
            self,
            field: str,
            value: int,
            scale: float,
            label: QLabel,
    ) -> None:
        numeric_value = value / scale
        if field in {"kaleidoscope_slices", "mosaic_tiles", "feedback_delay_frames"}:
            numeric_value = int(round(numeric_value))
        setattr(self.settings, field, numeric_value)
        self.manual_parameter_changed.emit(f"master.{field}")
        if not self.settings.enabled:
            self.settings.enabled = True
            self.enabled_check.blockSignals(True)
            self.enabled_check.setChecked(True)
            self.enabled_check.blockSignals(False)
        label.setText(f"{value / scale:.2f}".rstrip("0").rstrip("."))
        if self.preset_combo.currentText() != "Custom":
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentText("Custom")
            self.preset_combo.blockSignals(False)
            self.settings.preset_name = "Custom"

    def _reset(self) -> None:
        self.settings.reset()
        self.sync_from_settings()
        self.manual_parameter_changed.emit("master.*")

    def sync_from_settings(self) -> None:
        self.preset_combo.blockSignals(True)
        name = self.settings.preset_name
        self.preset_combo.setCurrentText(name if name in PRESETS else "Custom")
        self.preset_combo.blockSignals(False)
        self.sync_sources()
        self.transform_mode_combo.blockSignals(True)
        transform_index = self.transform_mode_combo.findData(self.settings.transform_mode)
        self.transform_mode_combo.setCurrentIndex(max(0, transform_index))
        self.transform_mode_combo.blockSignals(False)
        self.displacement_luma_check.blockSignals(True)
        self.displacement_luma_check.setChecked(self.settings.displacement_luma)
        self.displacement_luma_check.blockSignals(False)
        self.feedback_enabled_check.blockSignals(True)
        self.feedback_enabled_check.setChecked(self.settings.feedback_enabled)
        self.feedback_enabled_check.blockSignals(False)
        self.feedback_blend_combo.blockSignals(True)
        self.feedback_blend_combo.setCurrentText(self.settings.feedback_blend_mode)
        self.feedback_blend_combo.blockSignals(False)
        self.feedback_frozen_check.blockSignals(True)
        self.feedback_frozen_check.setChecked(self.settings.feedback_frozen)
        self.feedback_frozen_check.blockSignals(False)
        self.enabled_check.blockSignals(True)
        self.enabled_check.setChecked(self.settings.enabled)
        self.enabled_check.blockSignals(False)
        for key, (slider, label, scale) in self._sliders.items():
            slider.blockSignals(True)
            value = round(float(getattr(self.settings, key)) * scale)
            slider.setValue(value)
            slider.blockSignals(False)
            label.setText(f"{value / scale:.2f}".rstrip("0").rstrip("."))
