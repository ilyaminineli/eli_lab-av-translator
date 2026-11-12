from __future__ import annotations

import random
import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from generators.catalog import normalize_settings
from generators.palettes import import_aco_palette, palette_look, palette_names
from generators.text_pools import random_text_sample


class GeneratorsPanel(QWidget):
    """Create and edit transparent procedural and typographic composition layers."""

    composition_changed = Signal()
    selected_layer_changed = Signal(str)
    layer_properties_changed = Signal(str)
    manual_target_changed = Signal(str)

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self._loading = False
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setObjectName("generatorSettingsScroll")
        body = QWidget()
        body.setMinimumWidth(0)
        root = QVBoxLayout(body)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(7)

        add_group = QGroupBox("ADD GENERATOR / OVERLAY")
        add_layout = QVBoxLayout(add_group)
        row_one = QHBoxLayout()
        self.add_geometry_button = QPushButton("+ GEOMETRY")
        self.add_text_button = QPushButton("+ TEXT ART")
        row_one.addWidget(self.add_geometry_button)
        row_one.addWidget(self.add_text_button)
        row_two = QHBoxLayout()
        self.add_waveform_button = QPushButton("+ WAVEFORM")
        self.add_particles_button = QPushButton("+ PARTICLES")
        row_two.addWidget(self.add_waveform_button)
        row_two.addWidget(self.add_particles_button)
        row_three = QHBoxLayout()
        self.add_overlay_button = QPushButton("+ IMAGE / VIDEO OVERLAY")
        self.remove_button = QPushButton("REMOVE SELECTED LAYER")
        row_three.addWidget(self.add_overlay_button)
        row_three.addWidget(self.remove_button)
        add_layout.addLayout(row_one)
        add_layout.addLayout(row_two)
        add_layout.addLayout(row_three)
        root.addWidget(add_group)

        selected_heading = QLabel("SELECTED GENERATOR / OVERLAY")
        selected_heading.setObjectName("sectionHeading")
        root.addWidget(selected_heading)
        self.layer_combo = QComboBox()
        root.addWidget(self.layer_combo)

        self.text_group = QGroupBox("TEXT ART")
        text_form = QFormLayout(self.text_group)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setMaximumBlockCount(32)
        self.text_edit.setPlaceholderText(
            "Enter multiline text or regenerate from the bilingual pool…"
        )
        self.text_edit.setMinimumHeight(84)
        self.text_edit.setMaximumHeight(120)
        text_form.addRow("CONTENT · EDIT BUFFER", self.text_edit)

        raster_group = QGroupBox("TEXT RASTER PERFORMANCE")
        raster_form = QFormLayout(raster_group)
        self.text_live_preview_check = QCheckBox("Live preview")
        self.text_live_preview_check.setChecked(True)
        self.text_live_preview_check.setToolTip(
            "When off, edits still commit to the composition but raster updates wait "
            "until Live Preview is enabled or Apply Immediately is pressed."
        )
        raster_form.addRow("PREVIEW", self.text_live_preview_check)
        self.text_commit_pause_check = QCheckBox("Commit after typing pause")
        self.text_commit_pause_check.setChecked(True)
        self.text_commit_pause_check.setToolTip(
            "Automatically commit the editor buffer after the short typing debounce."
        )
        raster_form.addRow("COMMIT", self.text_commit_pause_check)
        self.text_preview_quality_combo = QComboBox()
        for label, scale in (
                ("Draft · 25%", 0.25),
                ("Balanced · 50%", 0.5),
                ("High · 75%", 0.75),
                ("Maximum · 100%", 1.0),
        ):
            self.text_preview_quality_combo.addItem(label, scale)
        self.text_preview_quality_combo.setCurrentIndex(1)
        raster_form.addRow("PREVIEW QUALITY", self.text_preview_quality_combo)
        self.text_final_resolution_check = QCheckBox(
            "Use full resolution for Apply Immediately"
        )
        self.text_final_resolution_check.setChecked(True)
        raster_form.addRow("FINAL RENDER", self.text_final_resolution_check)
        self.text_update_rate_spin = QSpinBox()
        self.text_update_rate_spin.setRange(1, 20)
        self.text_update_rate_spin.setValue(4)
        self.text_update_rate_spin.setSuffix(" Hz")
        self.text_update_rate_spin.setToolTip(
            "Maximum start rate for CPU text raster jobs. "
            "Newer pending snapshots replace older ones."
        )
        raster_form.addRow("MAX RASTER RATE", self.text_update_rate_spin)
        self.text_freeze_check = QCheckBox("Freeze current text texture")
        self.text_freeze_check.setToolTip(
            "Hold the last uploaded text texture. Edits are coalesced and rasterized when unfrozen."
        )
        raster_form.addRow("TEXTURE", self.text_freeze_check)
        self.text_fallback_check = QCheckBox(
            "Keep last valid texture if rasterization fails"
        )
        self.text_fallback_check.setChecked(True)
        self.text_fallback_check.setToolTip(
            "When enabled, renderers retain their last successful texture after a raster error."
        )
        raster_form.addRow("RECOVERY", self.text_fallback_check)
        self.text_raster_status = QLabel("TEXT PIPELINE · READY")
        self.text_raster_status.setObjectName("mutedLabel")
        self.text_raster_status.setToolTip(
            "EDITING → RASTERIZING → READY. "
            "A failed render preserves the last valid texture when recovery is enabled."
        )
        raster_form.addRow("STATUS", self.text_raster_status)
        self.apply_text_now_button = QPushButton("APPLY IMMEDIATELY")
        self.apply_text_now_button.setToolTip(
            "Commit current text and typography now, bypassing the pause debounce "
            "and using final resolution when enabled."
        )
        raster_form.addRow(self.apply_text_now_button)
        text_form.addRow(raster_group)

        static_raster_heading = QLabel("STATIC TYPOGRAPHY · CPU RASTER")
        static_raster_heading.setObjectName("sectionHeading")
        text_form.addRow(static_raster_heading)

        self.text_layout_combo = QComboBox()
        self.text_layout_combo.addItem("Single text block", "single")
        self.text_layout_combo.addItem("Typographic word collage", "collage")
        text_form.addRow("LAYOUT", self.text_layout_combo)

        self.font_combo = QComboBox()
        self.font_combo.setEditable(True)
        families = sorted(set(QFontDatabase.families()), key=str.casefold)
        self.font_combo.addItems(families[:250])
        text_form.addRow("TYPEFACE", self.font_combo)

        self.weight_combo = QComboBox()
        for label, value in (
                ("Regular", 400),
                ("Medium", 500),
                ("Bold", 700),
                ("Black", 900),
        ):
            self.weight_combo.addItem(label, value)
        text_form.addRow("WEIGHT", self.weight_combo)

        self.text_color_mode_combo = QComboBox()
        self.text_color_mode_combo.addItem("Single colour", "single")
        self.text_color_mode_combo.addItem("Alternate line colours", "alternate")
        text_form.addRow("COLOUR MODE", self.text_color_mode_combo)

        self.text_size_slider, self.text_size_value = self._slider(
            text_form, "FONT SIZE", 12, 420, 148
        )
        self.tracking_slider, self.tracking_value = self._slider(
            text_form, "LETTER TRACKING", -8, 48, 10
        )
        self.line_spacing_slider, self.line_spacing_value = self._slider(
            text_form, "LINE SPACING", 50, 250, 100
        )

        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["left", "center", "right"])
        text_form.addRow("ALIGNMENT", self.alignment_combo)

        self.vertical_alignment_combo = QComboBox()
        self.vertical_alignment_combo.addItems(["top", "middle", "bottom"])
        text_form.addRow("VERTICAL ALIGNMENT", self.vertical_alignment_combo)

        self.stroke_color = QLineEdit("#211B2A")
        text_form.addRow("OUTLINE COLOUR", self.stroke_color)
        self.text_outline_slider, self.text_outline_value = self._slider(
            text_form, "OUTLINE WIDTH", 0, 48, 4
        )
        self.shadow_check = QCheckBox("Soft offset shadow")
        self.shadow_check.setChecked(True)
        text_form.addRow("SHADOW", self.shadow_check)

        self.collage_variation_slider, self.collage_variation_value = self._slider(
            text_form, "COLLAGE VARIATION", 0, 100, 65
        )
        self.text_motion_group = QGroupBox("ANIMATED TYPOGRAPHY · GPU SHADER")
        motion_form = QFormLayout(self.text_motion_group)
        self.text_animation_combo = QComboBox()
        self.text_animation_combo.addItem("None", "none")
        self.text_animation_combo.addItem("Type-on", "type_on")
        self.text_animation_combo.addItem("Word / column reveal", "word_reveal")
        self.text_animation_combo.addItem("Line wave", "line_wave")
        self.text_animation_combo.addItem("Glyph jitter", "jitter")
        self.text_animation_combo.addItem("Text scrolling", "crawl")
        self.text_animation_combo.addItem("Signal glitch", "glitch")
        motion_form.addRow("MOTION", self.text_animation_combo)
        self.text_animation_speed_slider, self.text_animation_speed_value = self._slider(
            motion_form, "MOTION SPEED", 0, 800, 100
        )
        self.text_animation_amount_slider, self.text_animation_amount_value = self._slider(
            motion_form, "MOTION AMOUNT", 0, 180, 25
        )
        self.text_animation_columns_slider, self.text_animation_columns_value = self._slider(
            motion_form, "REVEAL STEPS", 2, 80, 18
        )
        text_form.addRow(self.text_motion_group)

        random_group = QGroupBox("RANDOM TEXT POOL · ENGLISH / 日本語")
        random_form = QFormLayout(random_group)
        self.random_language_combo = QComboBox()
        self.random_language_combo.addItem("Bilingual", "bilingual")
        self.random_language_combo.addItem("English", "english")
        self.random_language_combo.addItem("日本語", "japanese")
        random_form.addRow("LANGUAGE", self.random_language_combo)
        self.random_theme_combo = QComboBox()
        for label, value in (
                ("Random mix", "random"),
                ("Memory / 記憶", "memory"),
                ("Body / 身体", "body"),
                ("Signal / 信号", "signal"),
                ("Ritual / 儀式", "ritual"),
                ("Identity / 自己", "identity"),
        ):
            self.random_theme_combo.addItem(label, value)
        random_form.addRow("THEME", self.random_theme_combo)
        self.random_count_combo = QComboBox()
        for count in (8, 12, 16, 20, 24, 32):
            self.random_count_combo.addItem(str(count), count)
        self.random_count_combo.setCurrentText("16")
        random_form.addRow("FRAGMENTS", self.random_count_combo)
        self.dictionary_check = QCheckBox("Use repository dictionaries")
        self.dictionary_check.setChecked(True)
        random_form.addRow("DICTIONARY", self.dictionary_check)
        self.auto_text_check = QCheckBox("Auto-regenerate during Auto Performance")
        self.auto_text_check.setToolTip(
            "Allow Auto Performance to regenerate this text layer on its generator cycle."
        )
        self.auto_text_check.setChecked(True)
        random_form.addRow("AUTO TEXT", self.auto_text_check)
        self.random_text_button = QPushButton("REGENERATE TEXT")
        random_form.addRow(self.random_text_button)
        text_form.addRow(random_group)
        root.addWidget(self.text_group)

        self.geometry_group = QGroupBox("GEOMETRY PATTERN")
        geometry_form = QFormLayout(self.geometry_group)
        self.geometry_pattern_combo = QComboBox()
        self.geometry_pattern_combo.addItems(
            ["rings", "grid", "radial", "crosshatch", "polygon", "spiral", "moire", "hexgrid"]
        )
        geometry_form.addRow("PATTERN", self.geometry_pattern_combo)
        self.geometry_density_slider, self.geometry_density_value = self._slider(
            geometry_form, "DENSITY", 2, 80, 12
        )
        self.geometry_width_slider, self.geometry_width_value = self._slider(
            geometry_form, "LINE WIDTH", 1, 48, 4
        )
        root.addWidget(self.geometry_group)

        self.waveform_group = QGroupBox("WAVEFORM")
        waveform_form = QFormLayout(self.waveform_group)
        self.waveform_pattern_combo = QComboBox()
        self.waveform_pattern_combo.addItems(
            ["sine", "lissajous", "orbit", "radial", "rose"]
        )
        waveform_form.addRow("PATTERN", self.waveform_pattern_combo)
        self.waveform_density_slider, self.waveform_density_value = self._slider(
            waveform_form, "TRACES", 1, 12, 5
        )
        self.waveform_width_slider, self.waveform_width_value = self._slider(
            waveform_form, "LINE WIDTH", 1, 40, 6
        )
        self.amplitude_slider, self.amplitude_value = self._slider(
            waveform_form, "AMPLITUDE", 1, 48, 22
        )
        self.frequency_slider, self.frequency_value = self._slider(
            waveform_form, "FREQUENCY", 1, 240, 25
        )
        root.addWidget(self.waveform_group)

        self.particles_group = QGroupBox("GPU PARTICLE FIELD")
        particles_form = QFormLayout(self.particles_group)
        self.particle_density_slider, self.particle_density_value = self._slider(
            particles_form, "PARTICLE COUNT", 4, 120, 42
        )
        self.particle_speed_slider, self.particle_speed_value = self._slider(
            particles_form, "SPEED", 0, 200, 22
        )
        self.particle_size_slider, self.particle_size_value = self._slider(
            particles_form, "SIZE", 2, 80, 18
        )
        self.particle_spread_slider, self.particle_spread_value = self._slider(
            particles_form, "DRIFT / SPREAD", 0, 100, 42
        )
        self.particle_trail_slider, self.particle_trail_value = self._slider(
            particles_form, "TRAIL", 0, 100, 18
        )
        self.particle_mode_combo = QComboBox()
        self.particle_mode_combo.addItems(["drift", "rise", "fall", "orbit"])
        particles_form.addRow("EMITTER MODE", self.particle_mode_combo)
        root.addWidget(self.particles_group)

        self.style_group = QGroupBox("COLOUR AND ANIMATION")
        style_form = QFormLayout(self.style_group)
        self.primary_color = QLineEdit("#E8E4DA")
        self.secondary_color = QLineEdit("#8678A8")
        self.background_color = QLineEdit("#00000000")
        style_form.addRow("PRIMARY COLOUR", self.primary_color)
        style_form.addRow("ACCENT COLOUR", self.secondary_color)
        style_form.addRow("BACKGROUND COLOUR", self.background_color)
        self.palette_combo = QComboBox()
        self.palette_combo.addItem("Manual colours", "")
        self.palette_combo.addItems(palette_names())
        style_form.addRow("JAPANESE PALETTE LOOK", self.palette_combo)
        self.import_palette_button = QPushButton("IMPORT ACO PALETTE…")
        style_form.addRow(self.import_palette_button)

        self.animation_combo = QComboBox()
        self.animation_combo.addItems(["none", "pulse", "rotate", "drift", "flicker", "warp"])
        style_form.addRow("ANIMATION", self.animation_combo)
        self.speed_slider, self.speed_value = self._slider(
            style_form, "ANIMATION SPEED", 0, 800, 18
        )
        self.amount_slider, self.amount_value = self._slider(
            style_form, "ANIMATION AMOUNT", 0, 100, 30
        )
        root.addWidget(self.style_group)

        self.layer_appearance_group = QGroupBox("SELECTED LAYER APPEARANCE")
        appearance_form = QFormLayout(self.layer_appearance_group)
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems(
            ["normal", "add", "screen", "multiply", "difference"]
        )
        appearance_form.addRow("BLEND MODE", self.blend_mode_combo)
        self.opacity_slider, self.opacity_value = self._slider(
            appearance_form, "OPACITY", 0, 100, 100
        )
        root.addWidget(self.layer_appearance_group)

        self.overlay_group = QGroupBox("IMAGE / VIDEO OVERLAY")
        overlay_form = QFormLayout(self.overlay_group)
        self.overlay_in_spin = QDoubleSpinBox()
        self.overlay_in_spin.setRange(0.0, 86400.0)
        self.overlay_in_spin.setDecimals(2)
        self.overlay_in_spin.setSuffix(" s")
        self.overlay_out_spin = QDoubleSpinBox()
        self.overlay_out_spin.setRange(0.0, 86400.0)
        self.overlay_out_spin.setDecimals(2)
        self.overlay_out_spin.setSpecialValueText("No end")
        self.overlay_out_spin.setSuffix(" s")
        self.overlay_speed_spin = QDoubleSpinBox()
        self.overlay_speed_spin.setRange(0.1, 4.0)
        self.overlay_speed_spin.setSingleStep(0.1)
        self.overlay_speed_spin.setDecimals(1)
        self.overlay_frame_hold_spin = QSpinBox()
        self.overlay_frame_hold_spin.setRange(1, 24)
        self.overlay_loop_check = QCheckBox("Loop playback")
        self.overlay_scene_sync_check = QCheckBox("Sync to scene changes")
        self.overlay_scene_sync_check.setEnabled(False)
        self.overlay_scene_sync_check.setToolTip(
            "Scene-clock synchronization is not connected in the Video Mixer milestone."
        )
        self.overlay_mask_mode = QComboBox()
        self.overlay_mask_mode.addItem("No matte", "none")
        self.overlay_mask_mode.addItem("Alpha matte", "alpha")
        self.overlay_mask_mode.addItem("Luma matte", "luma")
        self.overlay_mask_source = QComboBox()
        overlay_form.addRow("IN POINT", self.overlay_in_spin)
        overlay_form.addRow("OUT POINT", self.overlay_out_spin)
        overlay_form.addRow("PLAYBACK SPEED", self.overlay_speed_spin)
        overlay_form.addRow("FRAME HOLD", self.overlay_frame_hold_spin)
        overlay_form.addRow("PLAYBACK", self.overlay_loop_check)
        overlay_form.addRow("MASK MODE", self.overlay_mask_mode)
        overlay_form.addRow("MASK SOURCE", self.overlay_mask_source)
        overlay_form.addRow(self.overlay_scene_sync_check)
        self.overlay_hint = QLabel(
            "Overlay playback settings apply to the selected image or video layer."
        )
        self.overlay_hint.setWordWrap(True)
        self.overlay_hint.setObjectName("mutedLabel")
        overlay_form.addRow(self.overlay_hint)
        root.addWidget(self.overlay_group)
        self.overlay_group.setVisible(False)

        self.apply_button = QPushButton("APPLY GENERATOR SETTINGS")
        self.apply_button.setDefault(True)
        root.addWidget(self.apply_button)
        self.hint_label = QLabel(
            "Select a generator or overlay above. Its settings are saved with the composition."
        )
        self.hint_label.setWordWrap(True)
        self.hint_label.setObjectName("mutedLabel")
        root.addWidget(self.hint_label)
        root.addStretch(1)

        self.scroll.setWidget(body)
        outer.addWidget(self.scroll)

        self.add_geometry_button.clicked.connect(lambda: self.add_generator("geometry"))
        self.add_text_button.clicked.connect(lambda: self.add_generator("text"))
        self.add_waveform_button.clicked.connect(lambda: self.add_generator("waveform"))
        self.add_particles_button.clicked.connect(lambda: self.add_generator("particles"))
        self.add_overlay_button.clicked.connect(self.add_overlay_media)
        self.remove_button.clicked.connect(self.remove_selected)
        self.layer_combo.currentIndexChanged.connect(self.load_selected)
        self.palette_combo.currentTextChanged.connect(self._palette_changed)
        self.blend_mode_combo.currentTextChanged.connect(self._apply_layer_appearance)
        self.opacity_slider.valueChanged.connect(self._apply_layer_appearance)
        for control in (
                self.overlay_in_spin,
                self.overlay_out_spin,
                self.overlay_speed_spin,
                self.overlay_frame_hold_spin,
        ):
            control.valueChanged.connect(self._apply_overlay_settings)
        self.overlay_loop_check.toggled.connect(self._apply_overlay_settings)
        self.overlay_scene_sync_check.toggled.connect(self._apply_overlay_settings)
        self.overlay_mask_mode.currentIndexChanged.connect(self._apply_overlay_settings)
        self.overlay_mask_source.currentIndexChanged.connect(self._apply_overlay_settings)
        self.import_palette_button.clicked.connect(self.import_palette)
        self.apply_button.clicked.connect(self.apply_settings)
        self.random_text_button.clicked.connect(self.randomize_text)
        self.apply_text_now_button.clicked.connect(self.apply_text_immediately)
        self.text_live_preview_check.toggled.connect(self._text_live_preview_toggled)
        self.text_commit_pause_check.toggled.connect(self._commit_on_pause_toggled)
        self.text_preview_quality_combo.currentIndexChanged.connect(
            self._text_preview_quality_changed
        )
        self.text_update_rate_spin.valueChanged.connect(
            self.application.generator_raster_service.set_max_text_update_hz
        )
        self.text_freeze_check.toggled.connect(self._text_freeze_toggled)
        self.text_fallback_check.toggled.connect(
            self.application.generator_raster_service.set_keep_last_valid_texture
        )
        service = self.application.generator_raster_service
        service.raster_started.connect(self._on_text_raster_started)
        service.raster_ready.connect(self._on_text_raster_ready)
        service.raster_failed.connect(self._on_text_raster_failed)
        service.set_max_text_update_hz(self.text_update_rate_spin.value())
        service.set_keep_last_valid_texture(self.text_fallback_check.isChecked())
        self._collage_seed = 211
        self._apply_timer = QTimer(self)
        self._apply_timer.setSingleShot(True)
        self._apply_timer.setInterval(150)
        self._apply_timer.timeout.connect(self._flush_generator_settings)
        self._text_commit_timer = QTimer(self)
        self._text_commit_timer.setSingleShot(True)
        self._text_commit_timer.setInterval(280)
        self._text_commit_timer.timeout.connect(self.commit_text)
        self._text_motion_timer = QTimer(self)
        self._text_motion_timer.setSingleShot(True)
        self._text_motion_timer.setInterval(24)
        self._text_motion_timer.timeout.connect(self._flush_text_motion_settings)
        self._editing_text_buffer = ""
        self._committed_text = ""
        self._pending_text_layer_id: str | None = None
        self._pending_text_motion_layer_id: str | None = None
        self._pending_settings_layer_id: str | None = None
        self._connect_live_updates()
        self.refresh()

    @staticmethod
    def _slider(
            form: QFormLayout,
            title: str,
            minimum: int,
            maximum: int,
            default: int,
    ) -> tuple[QSlider, QLabel]:
        row = QHBoxLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(default)
        value_label = QLabel(str(default))
        value_label.setMinimumWidth(34)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        slider.valueChanged.connect(lambda value: value_label.setText(str(value)))
        row.addWidget(slider, 1)
        row.addWidget(value_label)
        form.addRow(title, row)
        return slider, value_label

    def _connect_live_updates(self) -> None:
        for widget in (
                self.font_combo,
                self.weight_combo,
                self.text_color_mode_combo,
                self.text_layout_combo,
                self.alignment_combo,
                self.vertical_alignment_combo,
                self.stroke_color,
                self.primary_color,
                self.secondary_color,
                self.background_color,
                self.animation_combo,
                self.geometry_pattern_combo,
                self.waveform_pattern_combo,
                self.particle_mode_combo,
        ):
            signal = getattr(widget, "textChanged", None)
            if signal is None:
                signal = getattr(widget, "currentTextChanged", None)
            if signal is not None:
                signal.connect(self._schedule_apply)
        self.text_edit.textChanged.connect(self._text_buffer_changed)
        for slider in (
                self.text_size_slider,
                self.tracking_slider,
                self.line_spacing_slider,
                self.text_outline_slider,
                self.collage_variation_slider,
                self.geometry_density_slider,
                self.geometry_width_slider,
                self.waveform_density_slider,
                self.waveform_width_slider,
                self.amplitude_slider,
                self.frequency_slider,
                self.particle_density_slider,
                self.particle_speed_slider,
                self.particle_size_slider,
                self.particle_spread_slider,
                self.particle_trail_slider,
                self.speed_slider,
                self.amount_slider,
        ):
            slider.valueChanged.connect(self._schedule_apply)
        self.text_animation_combo.currentIndexChanged.connect(
            self._schedule_text_motion_apply
        )
        for slider in (
                self.text_animation_speed_slider,
                self.text_animation_amount_slider,
                self.text_animation_columns_slider,
        ):
            slider.valueChanged.connect(self._schedule_text_motion_apply)
        self.shadow_check.toggled.connect(self._schedule_apply)

    def _schedule_apply(self, *_args) -> None:
        layer = self._selected_layer()
        if self._loading or layer is None:
            return
        self._pending_settings_layer_id = layer.id
        self._apply_timer.start()

    def _schedule_text_motion_apply(self, *_args) -> None:
        layer = self._selected_layer()
        if (
                self._loading
                or layer is None
                or layer.source_type != "generator"
                or layer.generator_type != "text"
                or layer.locked
        ):
            return
        self._pending_text_motion_layer_id = layer.id
        self._text_motion_timer.start()

    def _flush_text_motion_settings(self) -> None:
        """Update shader uniforms on the layer without requesting a new raster."""
        self._text_motion_timer.stop()
        target_id = self._pending_text_motion_layer_id
        self._pending_text_motion_layer_id = None
        if target_id is None:
            return
        layer = self.application.composition.get_layer(target_id)
        if (
                layer is None
                or layer.source_type != "generator"
                or layer.generator_type != "text"
                or layer.locked
        ):
            return
        settings = dict(layer.generator_settings)
        settings.update({
            "text_animation": str(self.text_animation_combo.currentData() or "none"),
            "text_animation_speed": self.text_animation_speed_slider.value() / 100.0,
            "text_animation_amount": (
                self.text_animation_amount_slider.value() / 1000.0
            ),
            "text_animation_columns": self.text_animation_columns_slider.value(),
        })
        normalized = normalize_settings("text", settings)
        if normalized == layer.generator_settings:
            return
        self.application.layer_manager.update_layer(
            layer.id,
            generator_settings=normalized,
        )
        # The compositor reads these fields as per-frame uniforms. No
        # GeneratorRasterService request is made by this path. Only pause
        # automation on shader parameters that actually changed.
        for key in ("text_animation_speed", "text_animation_amount"):
            if settings.get(key) != normalized.get(key):
                self.manual_target_changed.emit(f"generator.{key}")
        self.composition_changed.emit()

    def _text_buffer_changed(self) -> None:
        if self._loading:
            return
        self._editing_text_buffer = self.text_edit.toPlainText()
        layer = self._selected_layer()
        if layer is not None and layer.generator_type == "text":
            self._pending_text_layer_id = layer.id
            self._set_text_raster_status("editing")
        if self.text_commit_pause_check.isChecked():
            self._text_commit_timer.start()
        else:
            self._text_commit_timer.stop()

    def _flush_generator_settings(self) -> None:
        target_id = self._pending_settings_layer_id
        self._pending_settings_layer_id = None
        layer = (
            self.application.composition.get_layer(target_id)
            if target_id else self._selected_layer()
        )
        if layer is None:
            return
        if (
                self._pending_text_layer_id == layer.id
                and self.text_commit_pause_check.isChecked()
        ):
            self.commit_text()
        self._apply_non_text_settings(target_layer=layer)

    def _set_text_raster_status(self, phase: str, detail: str = "") -> None:
        labels = {
            "editing": "EDITING",
            "rasterizing": "RASTERIZING",
            "ready": "READY",
            "failed": "FAILED",
            "frozen": "FROZEN · LAST VALID TEXTURE",
        }
        label = labels.get(phase, "READY")
        suffix = f" · {detail}" if detail else ""
        self.text_raster_status.setText(f"TEXT PIPELINE · {label}{suffix}")

    def _sync_text_raster_status(self) -> None:
        layer = self._selected_layer()
        if layer is None or layer.generator_type != "text":
            self._set_text_raster_status("ready")
        elif self._pending_text_layer_id == layer.id:
            self._set_text_raster_status("editing")
        else:
            self._set_text_raster_status(
                self.application.generator_raster_service.status(layer.id)
            )

    def _on_text_raster_started(self, layer_id: str, _revision: int) -> None:
        if layer_id == self.layer_combo.currentData():
            phase = (
                "editing"
                if self._pending_text_layer_id == layer_id
                else "rasterizing"
            )
            self._set_text_raster_status(phase)

    def _on_text_raster_ready(
            self, layer_id: str, _revision: int, _fingerprint: str, _pixels: object
    ) -> None:
        if layer_id == self.layer_combo.currentData():
            phase = (
                "editing"
                if self._pending_text_layer_id == layer_id
                else "ready"
            )
            self._set_text_raster_status(phase)

    def _on_text_raster_failed(
            self, layer_id: str, _revision: int, _fingerprint: str, message: str
    ) -> None:
        if layer_id == self.layer_combo.currentData():
            phase = (
                "editing"
                if self._pending_text_layer_id == layer_id
                else "failed"
            )
            self._set_text_raster_status(phase, message[:72])

    def _text_live_preview_toggled(self, enabled: bool) -> None:
        service = self.application.generator_raster_service
        service.set_live_preview_enabled(enabled)
        if enabled:
            layer = self._selected_layer()
            if layer is not None and layer.generator_type == "text":
                service.request(layer.id, "text", dict(layer.generator_settings))
        self._sync_text_raster_status()

    def _commit_on_pause_toggled(self, enabled: bool) -> None:
        if not enabled:
            self._text_commit_timer.stop()

    def _text_preview_quality_changed(self, _index: int) -> None:
        service = self.application.generator_raster_service
        service.set_text_preview_scale(
            float(self.text_preview_quality_combo.currentData() or 0.5)
        )
        layer = self._selected_layer()
        if layer is not None and layer.generator_type == "text":
            service.request(
                layer.id,
                "text",
                dict(layer.generator_settings),
                full_resolution=False,
            )
        self._sync_text_raster_status()

    def _text_freeze_toggled(self, frozen: bool) -> None:
        layer = self._selected_layer()
        if layer is None or layer.generator_type != "text":
            return
        self.application.generator_raster_service.set_frozen(layer.id, frozen)
        self._sync_text_raster_status()

    def commit_text(
            self,
            *,
            request_raster: bool = True,
            force_render: bool = False,
            full_resolution: bool = False,
    ) -> None:
        """Commit the current editor buffer without rebuilding other controls."""
        self._text_commit_timer.stop()
        target_id = self._pending_text_layer_id
        has_pending_buffer = target_id is not None
        self._pending_text_layer_id = None
        layer = (
            self.application.composition.get_layer(target_id)
            if target_id else self._selected_layer()
        )
        if (
                layer is None
                or layer.source_type != "generator"
                or layer.generator_type != "text"
                or layer.locked
        ):
            return
        text_snapshot = (
            self._editing_text_buffer
            if has_pending_buffer or layer.id == self.layer_combo.currentData()
            else str(layer.generator_settings.get("text", ""))
        )
        snapshot = dict(layer.generator_settings)
        snapshot["text"] = text_snapshot
        normalized = normalize_settings("text", snapshot)
        if normalized == layer.generator_settings:
            return
        self.application.layer_manager.update_layer(
            layer.id,
            generator_settings=normalized,
        )
        # Advance the shared revision now, not on the next renderer paint. A
        # slow older text render must become stale as soon as this commit lands.
        if request_raster:
            self.application.generator_raster_service.request(
                layer.id,
                "text",
                normalized,
                force=force_render,
                full_resolution=full_resolution,
            )
        self._committed_text = str(normalized["text"])
        if layer.id == self.layer_combo.currentData():
            self.hint_label.setText(
                f"Text committed · {len(self._committed_text)} characters. "
                "Rasterization continues in the background."
            )
        self.manual_target_changed.emit("generator.*")
        self.composition_changed.emit()
        self._sync_text_raster_status()

    def randomize_text(self) -> None:
        self._apply_timer.stop()
        self._pending_settings_layer_id = None
        layer = self._selected_layer()
        if layer is None or layer.generator_type != "text" or layer.locked:
            return
        language = str(self.random_language_combo.currentData())
        theme = str(self.random_theme_combo.currentData())
        count = int(self.random_count_combo.currentData())
        self._collage_seed = random.randrange(0, 2 ** 31 - 1)
        self.text_edit.setPlainText(
            random_text_sample(language, theme, count, self._collage_seed,
                               use_dictionary=self.dictionary_check.isChecked())
        )
        self.text_layout_combo.setCurrentIndex(
            max(0, self.text_layout_combo.findData("collage"))
        )
        self.text_color_mode_combo.setCurrentIndex(
            max(0, self.text_color_mode_combo.findData("alternate"))
        )
        self._editing_text_buffer = self.text_edit.toPlainText()
        self._pending_text_layer_id = layer.id
        self.commit_text()
        self._apply_non_text_settings()

    def add_overlay_media(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Add image or video overlay",
            "",
            (
                "Overlay media (*.png *.apng *.gif *.webp *.jpg *.jpeg *.bmp "
                "*.mp4 *.mov *.mkv *.avi *.webm *.m4v);;"
                "Images (*.png *.apng *.gif *.webp *.jpg *.jpeg *.bmp);;"
                "Videos (*.mp4 *.mov *.mkv *.avi *.webm *.m4v)"
            ),
        )
        if not path:
            return
        try:
            layer = self.application.add_media_overlay(path)
            self.refresh(select_id=layer.id)
            self.hint_label.setText(
                f"Added {layer.name}. Edit opacity, blend mode and playback below."
            )
            self.composition_changed.emit()
        except Exception as exc:
            self.hint_label.setText(f"Could not add overlay: {exc}")

    def _selected_layer(self):
        layer_id = self.layer_combo.currentData()
        if not layer_id:
            return None
        layer = self.application.composition.get_layer(str(layer_id))
        if layer is None or layer.source_type not in {"generator", "overlay"}:
            return None
        return layer

    def add_generator(self, generator_type: str) -> None:
        layer = self.application.add_generator_layer(generator_type)
        self.refresh(select_id=layer.id)
        self.composition_changed.emit()

    def refresh(self, select_id: str | None = None) -> None:
        previous = select_id or self.layer_combo.currentData()
        layers = [
            layer for layer in self.application.composition.layers
            if layer.source_type in {"generator", "overlay"}
        ]
        labels = {
            "geometry": "GEOMETRY",
            "text": "TEXT ART",
            "waveform": "WAVEFORM",
            "particles": "PARTICLES",
        }
        self._loading = True
        self.layer_combo.blockSignals(True)
        self.layer_combo.clear()
        for layer in layers:
            if layer.source_type == "overlay":
                media_kind = (layer.overlay_kind or "media").upper()
                label = f"OVERLAY · {media_kind} · {layer.name}"
            else:
                label = f"{labels.get(layer.generator_type, 'GENERATOR')} · {layer.name}"
            self.layer_combo.addItem(label, layer.id)
        selected = self.layer_combo.findData(previous)
        self.layer_combo.setCurrentIndex(selected if selected >= 0 else 0)
        self.layer_combo.blockSignals(False)
        self._loading = False
        self.load_selected()

    def select_layer(self, layer_id: str) -> None:
        index = self.layer_combo.findData(layer_id) if layer_id else -1
        if index < 0:
            if self.layer_combo.currentIndex() >= 0:
                self.layer_combo.blockSignals(True)
                self.layer_combo.setCurrentIndex(-1)
                self.layer_combo.blockSignals(False)
                self.load_selected()
            return
        if index == self.layer_combo.currentIndex():
            return
        self.layer_combo.setCurrentIndex(index)

    def load_selected(self, *_args) -> None:
        self._flush_text_motion_settings()
        if self._pending_text_layer_id is not None:
            self.commit_text()
        if self._apply_timer.isActive() and self._pending_settings_layer_id is not None:
            pending_layer = self.application.composition.get_layer(
                self._pending_settings_layer_id
            )
            if pending_layer is not None:
                self._apply_non_text_settings(target_layer=pending_layer)
        self._apply_timer.stop()
        self._pending_settings_layer_id = None
        layer = self._selected_layer()
        enabled = layer is not None
        is_overlay = bool(layer and layer.source_type == "overlay")
        generator_type = layer.generator_type if layer and not is_overlay else None

        self.text_group.setVisible(generator_type == "text")
        self.apply_text_now_button.setVisible(generator_type == "text")
        self.geometry_group.setVisible(generator_type == "geometry")
        self.waveform_group.setVisible(generator_type == "waveform")
        self.particles_group.setVisible(generator_type == "particles")
        self.style_group.setVisible(bool(layer and not is_overlay))
        self.layer_appearance_group.setVisible(enabled)
        self.overlay_group.setVisible(is_overlay)
        self.apply_button.setVisible(enabled)
        self.apply_button.setText(
            "APPLY OVERLAY SETTINGS" if is_overlay else "APPLY GENERATOR SETTINGS"
        )
        self.apply_button.setEnabled(bool(layer and not layer.locked))
        self.remove_button.setEnabled(enabled)
        self.layer_appearance_group.setEnabled(bool(layer and not layer.locked))
        self.overlay_group.setEnabled(bool(layer and is_overlay and not layer.locked))
        if not enabled:
            self.hint_label.setText("Add or select a generator or overlay layer.")
            return
        if self._loading:
            return

        self._loading = True
        self.blend_mode_combo.blockSignals(True)
        self.opacity_slider.blockSignals(True)
        self.blend_mode_combo.setCurrentText(layer.blend_mode)
        self.opacity_slider.setValue(round(layer.opacity * 100))
        self.blend_mode_combo.blockSignals(False)
        self.opacity_slider.blockSignals(False)

        if is_overlay:
            self.overlay_in_spin.blockSignals(True)
            self.overlay_out_spin.blockSignals(True)
            self.overlay_speed_spin.blockSignals(True)
            self.overlay_frame_hold_spin.blockSignals(True)
            self.overlay_loop_check.blockSignals(True)
            self.overlay_scene_sync_check.blockSignals(True)
            self.overlay_mask_mode.blockSignals(True)
            self.overlay_mask_source.blockSignals(True)
            self.overlay_in_spin.setValue(layer.overlay_in)
            self.overlay_out_spin.setValue(layer.overlay_out or 0.0)
            self.overlay_speed_spin.setValue(layer.overlay_speed)
            self.overlay_frame_hold_spin.setValue(layer.overlay_frame_hold)
            self.overlay_loop_check.setChecked(layer.overlay_loop)
            self.overlay_scene_sync_check.setChecked(layer.overlay_scene_sync)
            self.overlay_mask_mode.setCurrentIndex(
                max(0, self.overlay_mask_mode.findData(layer.overlay_mask_mode))
            )
            self.overlay_mask_source.clear()
            self.overlay_mask_source.addItem("No source", "")
            for candidate in self.application.composition.layers:
                if candidate.id != layer.id and candidate.source_id:
                    self.overlay_mask_source.addItem(candidate.name, candidate.source_id)
            self.overlay_mask_source.setCurrentIndex(
                max(0, self.overlay_mask_source.findData(layer.overlay_mask_source))
            )
            for control in (
                    self.overlay_in_spin,
                    self.overlay_out_spin,
                    self.overlay_speed_spin,
                    self.overlay_frame_hold_spin,
                    self.overlay_loop_check,
                    self.overlay_scene_sync_check,
                    self.overlay_mask_mode,
                    self.overlay_mask_source,
            ):
                control.blockSignals(False)

            is_video = layer.overlay_kind == "video"
            image_player = self.application._overlay_images.get(layer.id)
            is_animated_image = bool(image_player and image_player.animated)
            self.overlay_speed_spin.setEnabled(is_animated_image)
            self.overlay_frame_hold_spin.setEnabled(is_animated_image)
            self.overlay_loop_check.setEnabled(is_video or is_animated_image)
            if is_video:
                self.overlay_hint.setText(
                    "Video overlays support looping and local in/out timing. "
                    "Playback speed and frame hold are not available for video sources yet."
                )
            elif is_animated_image:
                self.overlay_hint.setText(
                    "Animated images support playback speed, frame hold and looping."
                )
            else:
                self.overlay_hint.setText(
                    "Still images use local in/out timing, opacity, blend and matte. "
                    "Playback speed, frame hold and looping do not apply."
                )
            self.hint_label.setText(
                f"Editing {layer.name} · opacity and blend mode update live."
            )
            self._loading = False
            self.selected_layer_changed.emit(layer.id)
            return

        values = normalize_settings(generator_type or "geometry", layer.generator_settings)

        if generator_type == "text":
            self._committed_text = str(values["text"])
            self._editing_text_buffer = self._committed_text
            self._pending_text_layer_id = None
            self.text_edit.setPlainText(self._editing_text_buffer)
            self.random_language_combo.setCurrentIndex(
                max(
                    0,
                    self.random_language_combo.findData(
                        values.get("text_pool_language", "bilingual")
                    ),
                )
            )
            self.random_theme_combo.setCurrentIndex(
                max(0, self.random_theme_combo.findData(values.get("text_pool_theme", "random"))))
            self.random_count_combo.setCurrentIndex(
                max(0, self.random_count_combo.findData(int(values.get("text_pool_count", 16)))))
            self.dictionary_check.setChecked(bool(values.get("text_pool_dictionary", True)))
            self.auto_text_check.setChecked(bool(values.get("text_auto_regenerate", True)))
            self.text_layout_combo.setCurrentIndex(
                max(0, self.text_layout_combo.findData(values["text_layout"]))
            )
            self._collage_seed = int(values["collage_seed"])
            self.collage_variation_slider.setValue(
                round(float(values["collage_font_variation"]) * 100)
            )
            self.text_animation_combo.setCurrentIndex(
                max(0, self.text_animation_combo.findData(values["text_animation"]))
            )
            self.text_animation_speed_slider.setValue(
                round(float(values["text_animation_speed"]) * 100)
            )
            self.text_animation_amount_slider.setValue(
                round(float(values["text_animation_amount"]) * 1000)
            )
            self.text_animation_columns_slider.setValue(
                int(values["text_animation_columns"])
            )
            self.text_freeze_check.blockSignals(True)
            self.text_freeze_check.setChecked(
                self.application.generator_raster_service.is_frozen(layer.id)
            )
            self.text_freeze_check.blockSignals(False)
            self.font_combo.setCurrentText(str(values["font_family"]))
            weight_index = self.weight_combo.findData(int(values["font_weight"]))
            self.weight_combo.setCurrentIndex(max(0, weight_index))
            self.text_color_mode_combo.setCurrentIndex(
                max(0, self.text_color_mode_combo.findData(values["text_color_mode"]))
            )
            self.text_size_slider.setValue(int(values["font_size"]))
            self.tracking_slider.setValue(round(float(values["letter_spacing"])))
            self.line_spacing_slider.setValue(round(float(values["line_spacing"]) * 100))
            self.alignment_combo.setCurrentText(str(values["alignment"]))
            self.vertical_alignment_combo.setCurrentText(str(values["vertical_alignment"]))
            self.stroke_color.setText(str(values["stroke_color"]))
            self.text_outline_slider.setValue(round(float(values["stroke_width"]) * 2))
            self.shadow_check.setChecked(bool(values["shadow"]))
        elif generator_type == "geometry":
            self.geometry_pattern_combo.setCurrentText(str(values["pattern"]))
            self.geometry_density_slider.setValue(int(values["density"]))
            self.geometry_width_slider.setValue(round(float(values["line_width"]) * 2))
        elif generator_type == "waveform":
            self.waveform_pattern_combo.setCurrentText(str(values["pattern"]))
            self.waveform_density_slider.setValue(int(values["density"]))
            self.waveform_width_slider.setValue(round(float(values["line_width"]) * 2))
            self.amplitude_slider.setValue(round(float(values["amplitude"]) * 100))
            self.frequency_slider.setValue(round(float(values["frequency"]) * 10))
        elif generator_type == "particles":
            self.particle_density_slider.setValue(int(values["density"]))
            self.particle_speed_slider.setValue(round(float(values["speed"]) * 100))
            self.particle_size_slider.setValue(round(float(values["size"]) * 100))
            self.particle_spread_slider.setValue(round(float(values["spread"]) * 100))
            self.particle_trail_slider.setValue(round(float(values["trail"]) * 100))
            self.particle_mode_combo.setCurrentText(str(values["mode"]))

        self.primary_color.setText(str(values["primary_color"]))
        self.secondary_color.setText(str(values.get("secondary_color", "#C35C75")))
        self.background_color.setText(str(values.get("background_color", "#00000000")))
        self.animation_combo.setCurrentText(str(values["animation"]))
        self.speed_slider.setValue(round(float(values["animation_speed"]) * 100))
        amount = float(values["animation_amount"])
        amount_ranges = {
            "rotate": 180.0,
            "pulse": 0.25,
            "drift": 0.08,
            "warp": 0.45,
            "flicker": 1.0,
            "none": 0.45,
        }
        amount_range = amount_ranges.get(str(values["animation"]), 0.45)
        self.amount_slider.setValue(round(max(0.0, min(100.0, amount / amount_range * 100.0))))
        self._loading = False
        if layer is not None:
            self.selected_layer_changed.emit(layer.id)
            self._sync_text_raster_status()

    def sync_live_modulation(self) -> None:
        """Reflect live per-layer modifier values without rebuilding text or controls."""
        layer = self._selected_layer()
        if layer is None:
            return
        editable_controls = (
            self.opacity_slider,
            self.overlay_speed_spin,
            self.overlay_frame_hold_spin,
            self.text_animation_speed_slider,
            self.text_animation_amount_slider,
            self.text_size_slider,
            self.tracking_slider,
            self.geometry_density_slider,
            self.amplitude_slider,
            self.frequency_slider,
            self.waveform_density_slider,
            self.particle_density_slider,
            self.particle_speed_slider,
            self.particle_size_slider,
            self.particle_spread_slider,
            self.particle_trail_slider,
            self.speed_slider,
            self.amount_slider,
        )
        if any(
                control.hasFocus()
                or (isinstance(control, QSlider) and control.isSliderDown())
                for control in editable_controls
        ):
            return
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(round(layer.opacity * 100))
        self.opacity_slider.blockSignals(False)
        if layer.source_type == "overlay":
            player = self.application._overlay_images.get(layer.id)
            if player is None or not player.animated:
                return
            self.overlay_speed_spin.blockSignals(True)
            self.overlay_frame_hold_spin.blockSignals(True)
            self.overlay_speed_spin.setValue(layer.overlay_speed)
            self.overlay_frame_hold_spin.setValue(layer.overlay_frame_hold)
            self.overlay_speed_spin.blockSignals(False)
            self.overlay_frame_hold_spin.blockSignals(False)
            return
        if layer.source_type != "generator" or not layer.generator_type:
            return

        values = normalize_settings(layer.generator_type, layer.generator_settings)
        updates: list[tuple[QSlider, QLabel, int]] = []
        if layer.generator_type == "text":
            updates.extend((
                (
                    self.text_animation_speed_slider,
                    self.text_animation_speed_value,
                    round(values["text_animation_speed"] * 100),
                ),
                (
                    self.text_animation_amount_slider,
                    self.text_animation_amount_value,
                    round(values["text_animation_amount"] * 1000),
                ),
                (self.text_size_slider, self.text_size_value, int(values["font_size"])),
                (self.tracking_slider, self.tracking_value, round(values["letter_spacing"])),
            ))
        elif layer.generator_type == "geometry":
            updates.append((
                self.geometry_density_slider,
                self.geometry_density_value,
                int(values["density"]),
            ))
        elif layer.generator_type == "waveform":
            updates.extend((
                (self.amplitude_slider, self.amplitude_value, round(values["amplitude"] * 100)),
                (self.frequency_slider, self.frequency_value, round(values["frequency"] * 10)),
                (
                    self.waveform_density_slider,
                    self.waveform_density_value,
                    int(values["density"]),
                ),
            ))
        elif layer.generator_type == "particles":
            updates.extend((
                (
                    self.particle_density_slider,
                    self.particle_density_value,
                    int(values["density"]),
                ),
                (
                    self.particle_speed_slider,
                    self.particle_speed_value,
                    round(values["speed"] * 100),
                ),
                (
                    self.particle_size_slider,
                    self.particle_size_value,
                    round(values["size"] * 100),
                ),
                (
                    self.particle_spread_slider,
                    self.particle_spread_value,
                    round(values["spread"] * 100),
                ),
                (
                    self.particle_trail_slider,
                    self.particle_trail_value,
                    round(values["trail"] * 100),
                ),
            ))

        updates.append((
            self.speed_slider,
            self.speed_value,
            round(values["animation_speed"] * 100),
        ))
        amount_ranges = {
            "rotate": 180.0,
            "pulse": 0.25,
            "drift": 0.08,
            "warp": 0.45,
            "flicker": 1.0,
            "none": 0.45,
        }
        amount_range = amount_ranges.get(str(values["animation"]), 0.45)
        amount_value = round(
            max(0.0, min(100.0, float(values["animation_amount"]) / amount_range * 100.0))
        )
        updates.append((self.amount_slider, self.amount_value, amount_value))

        self._loading = True
        for slider, label, value in updates:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            label.setText(str(value))
        self._loading = False

    def import_palette(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Japanese colour palette", "", "Adobe Colour Swatch (*.aco)"
        )
        if not path:
            return
        try:
            imported = import_aco_palette(path)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Palette import failed", str(exc))
            return
        self.palette_combo.blockSignals(True)
        self.palette_combo.clear()
        self.palette_combo.addItem("Manual colours", "")
        self.palette_combo.addItems(palette_names())
        self.palette_combo.blockSignals(False)
        if imported:
            self.palette_combo.setCurrentText(imported[0])

    def _palette_changed(self, name: str) -> None:
        if not name or name == "Manual colours":
            return
        look = palette_look(name)
        self.primary_color.setText(str(look["primary_color"]))
        self.secondary_color.setText(str(look["secondary_color"]))
        self.background_color.setText(str(look["background_color"]))

    def sync_layer_appearance(self, layer_id: str) -> None:
        layer = self._selected_layer()
        if layer is None or layer.id != layer_id:
            return
        self._loading = True
        self.blend_mode_combo.blockSignals(True)
        self.opacity_slider.blockSignals(True)
        self.blend_mode_combo.setCurrentText(layer.blend_mode)
        self.opacity_slider.setValue(round(layer.opacity * 100))
        self.blend_mode_combo.blockSignals(False)
        self.opacity_slider.blockSignals(False)
        self._loading = False

    def _apply_layer_appearance(self, *_args) -> None:
        layer = self._selected_layer()
        if layer is None or layer.locked or self._loading:
            return
        self.application.layer_manager.update_layer(
            layer.id,
            blend_mode=str(self.blend_mode_combo.currentText()),
            opacity=self.opacity_slider.value() / 100.0,
            overlay_manual_override_until=(
                time.time() + 30.0
                if layer.source_type == "overlay"
                else layer.overlay_manual_override_until
            ),
        )
        self.layer_properties_changed.emit(layer.id)
        self.manual_target_changed.emit("selected_layer.opacity")

    def _apply_overlay_settings(self, *_args) -> None:
        layer = self._selected_layer()
        if (
                layer is None
                or layer.source_type != "overlay"
                or layer.locked
                or self._loading
        ):
            return
        self.application.layer_manager.update_layer(
            layer.id,
            overlay_in=self.overlay_in_spin.value(),
            overlay_out=self.overlay_out_spin.value() or None,
            overlay_speed=self.overlay_speed_spin.value(),
            overlay_frame_hold=self.overlay_frame_hold_spin.value(),
            overlay_loop=self.overlay_loop_check.isChecked(),
            overlay_scene_sync=self.overlay_scene_sync_check.isChecked(),
            overlay_mask_mode=str(self.overlay_mask_mode.currentData()),
            overlay_mask_source=str(self.overlay_mask_source.currentData() or ""),
            overlay_manual_override_until=__import__("time").time() + 30.0,
        )
        self.manual_target_changed.emit("overlay.*")
        video = self.application._overlay_videos.get(layer.id)
        if video is not None:
            video.set_loop(layer.overlay_loop)
        image = self.application._overlay_images.get(layer.id)
        if image is not None:
            image.configure_playback(
                layer.overlay_speed,
                layer.overlay_frame_hold,
                layer.overlay_loop,
            )

    def apply_text_immediately(self) -> None:
        layer = self._selected_layer()
        if (
                layer is None
                or layer.source_type != "generator"
                or layer.generator_type != "text"
                or layer.locked
        ):
            return
        self._text_commit_timer.stop()
        self._apply_timer.stop()
        self._pending_settings_layer_id = None
        self._flush_text_motion_settings()
        self.commit_text(request_raster=False)
        self._apply_non_text_settings(
            target_layer=layer,
            force_text_raster=True,
            full_resolution=self.text_final_resolution_check.isChecked(),
        )
        self._sync_text_raster_status()

    def apply_settings(self) -> None:
        self._apply_timer.stop()
        self._pending_settings_layer_id = None
        self._flush_text_motion_settings()
        layer = self._selected_layer()
        if layer is None or layer.locked:
            return
        if layer.source_type == "generator" and layer.generator_type == "text":
            self.commit_text(request_raster=False)
            self._apply_non_text_settings(
                force_text_raster=True,
                full_resolution=self.text_final_resolution_check.isChecked(),
            )
            return
        self._apply_non_text_settings()

    def _apply_non_text_settings(
            self,
            target_layer=None,
            *,
            force_text_raster: bool = False,
            full_resolution: bool = False,
    ) -> None:
        layer = target_layer or self._selected_layer()
        if layer is None or layer.locked:
            return
        if layer.source_type == "overlay":
            self._apply_overlay_settings()
            self._apply_layer_appearance()
            self.hint_label.setText(
                f"Applied overlay playback and appearance settings to {layer.name}."
            )
            return
        if layer.source_type != "generator":
            return

        generator_type = layer.generator_type or "geometry"
        settings = dict(layer.generator_settings)
        settings.update({
            "primary_color": self.primary_color.text().strip() or "#E8E4DA",
            "secondary_color": self.secondary_color.text().strip() or "#8678A8",
            "background_color": self.background_color.text().strip() or "#00000000",
            "animation": self.animation_combo.currentText(),
            "animation_speed": self.speed_slider.value() / 100.0,
        })
        amount = self.amount_slider.value() / 100.0
        amount_ranges = {
            "rotate": 180.0,
            "pulse": 0.25,
            "drift": 0.08,
            "warp": 0.45,
            "flicker": 1.0,
            "none": 0.45,
        }
        settings["animation_amount"] = amount * amount_ranges.get(
            str(settings["animation"]), 0.45
        )

        if generator_type == "text":
            settings.update({
                "text": self._committed_text,
                "text_pool_language": str(self.random_language_combo.currentData()),
                "text_pool_theme": str(self.random_theme_combo.currentData()),
                "text_pool_count": int(self.random_count_combo.currentData()),
                "text_pool_dictionary": self.dictionary_check.isChecked(),
                "text_auto_regenerate": self.auto_text_check.isChecked(),
                "text_layout": str(self.text_layout_combo.currentData()),
                "collage_seed": self._collage_seed,
                "collage_font_variation": self.collage_variation_slider.value() / 100.0,
                "font_family": self.font_combo.currentText().strip() or "Arial",
                "font_size": self.text_size_slider.value(),
                "font_weight": int(self.weight_combo.currentData()),
                "text_color_mode": str(self.text_color_mode_combo.currentData()),
                "letter_spacing": float(self.tracking_slider.value()),
                "line_spacing": self.line_spacing_slider.value() / 100.0,
                "alignment": self.alignment_combo.currentText(),
                "vertical_alignment": self.vertical_alignment_combo.currentText(),
                "stroke_color": self.stroke_color.text().strip() or "#211B2A",
                "stroke_width": self.text_outline_slider.value() / 2.0,
                "shadow": self.shadow_check.isChecked(),
            })
        elif generator_type == "geometry":
            settings.update({
                "pattern": self.geometry_pattern_combo.currentText(),
                "density": self.geometry_density_slider.value(),
                "line_width": self.geometry_width_slider.value() / 2.0,
            })
        elif generator_type == "waveform":
            settings.update({
                "pattern": self.waveform_pattern_combo.currentText(),
                "density": self.waveform_density_slider.value(),
                "line_width": self.waveform_width_slider.value() / 2.0,
                "amplitude": self.amplitude_slider.value() / 100.0,
                "frequency": self.frequency_slider.value() / 10.0,
            })

        elif generator_type == "particles":
            settings.update({
                "density": self.particle_density_slider.value(),
                "speed": self.particle_speed_slider.value() / 100.0,
                "size": self.particle_size_slider.value() / 100.0,
                "spread": self.particle_spread_slider.value() / 100.0,
                "trail": self.particle_trail_slider.value() / 100.0,
                "mode": self.particle_mode_combo.currentText(),
            })

        normalized = normalize_settings(generator_type, settings)
        self.application.layer_manager.update_layer(
            layer.id,
            generator_settings=normalized,
        )
        if generator_type == "text":
            # Typography/layout settings are part of the same versioned text
            # snapshot as the committed string. Animation-only changes dedupe
            # because the raster fingerprint excludes GPU-evaluated properties.
            self.application.generator_raster_service.request(
                layer.id,
                generator_type,
                normalized,
                force=force_text_raster,
                full_resolution=full_resolution if force_text_raster else None,
            )
        self.manual_target_changed.emit("generator.*")
        self.composition_changed.emit()
        self.hint_label.setText(
            f"Applied {layer.name}. Static content updates once; animation remains GPU-side."
        )

    def remove_selected(self) -> None:
        layer = self._selected_layer()
        if layer is None:
            return
        removed_id = layer.id
        if self._pending_text_motion_layer_id == removed_id:
            self._text_motion_timer.stop()
            self._pending_text_motion_layer_id = None
        if self._pending_text_layer_id == removed_id:
            self._text_commit_timer.stop()
            self._pending_text_layer_id = None
        self._apply_timer.stop()
        self._pending_settings_layer_id = None
        self.application.generator_raster_service.invalidate(removed_id)
        self.application.remove_layer(removed_id)
        self.refresh()
        self.composition_changed.emit()
        self.selected_layer_changed.emit(self.layer_combo.currentData() or "")
