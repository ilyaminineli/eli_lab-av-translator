from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from core.performance_modifiers import (
    PERF_MODIFIER_SOURCES,
    PERF_MODIFIER_TARGETS,
    LayerPerformanceModifier,
)
from effects.layer_settings import (
    EFFECT_STAGE_TYPES,
    LY_EFFECT_PSETS,
    apply_effect_chain_preset,
    normalize_layer_effects,
)

_BLEND_MODES = ("normal", "add", "screen", "multiply", "difference")


class LayerPanel(QWidget):
    layers_changed = Signal()
    selected_layer_changed = Signal(str)
    layer_properties_changed = Signal(str)

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Visible", "Layer", "Opacity", "Blend"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 58)
        self.table.setColumnWidth(2, 78)
        self.table.setColumnWidth(3, 82)
        self.table.setMinimumHeight(160)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemChanged.connect(self._visibility_changed)
        self.table.currentCellChanged.connect(self._selection_changed)

        controls_body = QWidget()
        controls_layout = QVBoxLayout(controls_body)
        controls_layout.setContentsMargins(2, 2, 2, 2)

        self.layer_lock_check = QCheckBox("LOCK LAYER")
        controls_layout.addWidget(self.layer_lock_check)

        self.transform_group = QGroupBox("LAYER TRANSFORM")
        transform_layout = QVBoxLayout(self.transform_group)
        self.position_x = self._add_slider(transform_layout, "X POSITION", 0, 100, 50)
        self.position_y = self._add_slider(transform_layout, "Y POSITION", 0, 100, 50)
        self.scale = self._add_slider(transform_layout, "UNIFORM SCALE", 10, 200, 100)
        self.rotation = self._add_slider(transform_layout, "ROTATION", -180, 180, 0)
        blend_row = QHBoxLayout()
        blend_row.addWidget(QLabel("BLEND MODE"))
        self.selected_blend_combo = QComboBox()
        self.selected_blend_combo.addItems(_BLEND_MODES)
        blend_row.addWidget(self.selected_blend_combo, 1)
        transform_layout.addLayout(blend_row)
        controls_layout.addWidget(self.transform_group)

        self.performance_modifiers_group = QGroupBox("PER-LAYER PERFORMANCE MODIFIERS")
        modifier_layout = QVBoxLayout(self.performance_modifiers_group)
        self.modifier_help_label = QLabel(
            "Give this layer its own rhythmic, audio or Sonic Pi movement. "
            "Modifiers are saved with the layer."
        )
        self.modifier_help_label.setWordWrap(True)
        modifier_layout.addWidget(self.modifier_help_label)
        self.modifier_rhythm_status = QLabel("BEAT — · DOWNBEAT — · PHRASE —")
        self.modifier_rhythm_status.setObjectName("mutedLabel")
        modifier_layout.addWidget(self.modifier_rhythm_status)
        self.modifier_list = QListWidget()
        self.modifier_list.setMinimumHeight(82)
        self.modifier_list.setMaximumHeight(170)
        modifier_layout.addWidget(self.modifier_list)

        self.modifier_source_combo = QComboBox()
        for source_id, label in PERF_MODIFIER_SOURCES.items():
            self.modifier_source_combo.addItem(label, source_id)
        self.modifier_target_combo = QComboBox()
        self.modifier_curve_combo = QComboBox()
        self.modifier_curve_combo.addItem("Smoothstep", "smoothstep")
        self.modifier_curve_combo.addItem("Linear", "linear")
        self.modifier_curve_combo.addItem("Exponential", "exponential")
        self.modifier_polarity_combo = QComboBox()
        self.modifier_polarity_combo.addItem("Positive", "positive")
        self.modifier_polarity_combo.addItem("Bipolar", "bipolar")
        modifier_layout.addWidget(QLabel("SOURCE"))
        modifier_layout.addWidget(self.modifier_source_combo)
        modifier_layout.addWidget(QLabel("TARGET"))
        modifier_layout.addWidget(self.modifier_target_combo)
        modifier_layout.addWidget(QLabel("RESPONSE"))
        response_row = QHBoxLayout()
        response_row.addWidget(self.modifier_curve_combo, 1)
        response_row.addWidget(self.modifier_polarity_combo, 1)
        modifier_layout.addLayout(response_row)
        self.modifier_depth = self._add_slider(
            modifier_layout, "DPTH · %", 0, 100, 12
        )
        modifier_buttons = QHBoxLayout()
        self.modifier_add_button = QPushButton("ADD MODIFIER")
        self.modifier_beat_button = QPushButton("BEAT")
        self.modifier_downbeat_button = QPushButton("DOWNBEAT")
        self.modifier_phrase_button = QPushButton("PHRASE")
        for button in (
                self.modifier_add_button,
                self.modifier_beat_button,
                self.modifier_downbeat_button,
                self.modifier_phrase_button,
        ):
            modifier_buttons.addWidget(button)
        modifier_layout.addLayout(modifier_buttons)
        self.modifier_remove_button = QPushButton("REMOVE SELECTED MODIFIER")
        modifier_layout.addWidget(self.modifier_remove_button)
        controls_layout.addWidget(self.performance_modifiers_group)
        self._modifier_signature: tuple = ()
        self._modifier_widgets: dict[str, tuple[QCheckBox, QLabel, QProgressBar]] = {}

        self.layer_fx_group = QGroupBox("LAYER EFFECT STACK")
        layer_fx_layout = QVBoxLayout(self.layer_fx_group)
        self.layer_fx_enabled = QCheckBox("ENABLE LAYER EFFECTS")
        self.layer_fx_layout = layer_fx_layout
        layer_fx_layout.addWidget(self.layer_fx_enabled)
        self.layer_fx_preset = QComboBox()
        self.layer_fx_preset.addItems(list(LY_EFFECT_PSETS) + ["Custom"])
        layer_fx_layout.addWidget(self.layer_fx_preset)
        layer_fx_layout.addWidget(QLabel("STAGE ORDER · TOP TO BOTTOM"))
        self.fx_stage_list = QListWidget()
        self.fx_stage_list.setMaximumHeight(120)
        layer_fx_layout.addWidget(self.fx_stage_list)
        stage_row = QHBoxLayout()
        self.fx_stage_type = QComboBox()
        for key, title in EFFECT_STAGE_TYPES.items():
            self.fx_stage_type.addItem(title, key)
        stage_row.addWidget(self.fx_stage_type, 1)
        self.fx_stage_add = QPushButton("ADD")
        self.fx_stage_remove = QPushButton("REMOVE")
        self.fx_stage_up = QPushButton("↑")
        self.fx_stage_down = QPushButton("↓")
        for button in (
                self.fx_stage_add, self.fx_stage_remove,
                self.fx_stage_up, self.fx_stage_down,
        ):
            stage_row.addWidget(button)
        layer_fx_layout.addLayout(stage_row)
        chain_row = QHBoxLayout()
        self.fx_chain_save = QPushButton("SAVE CHAIN…")
        self.fx_chain_export = QPushButton("EXPORT PRESETS…")
        self.fx_chain_import = QPushButton("IMPORT PRESETS…")
        for button in (self.fx_chain_save, self.fx_chain_export, self.fx_chain_import):
            chain_row.addWidget(button)
        layer_fx_layout.addLayout(chain_row)
        self.layer_fx_sliders = {}
        for key, title, minimum, maximum, default in (
                ("mix", "FX MIX", 0, 100, 100),
                ("monochrome", "MONOCHROME", 0, 100, 0),
                ("invert", "INVERT", 0, 100, 0),
                ("threshold", "THRESHOLD", 0, 100, 0),
                ("posterize", "POSTERIZE", 0, 100, 0),
                ("hue", "HUE", -180, 180, 0),
                ("contrast", "CONTRAST", 0, 250, 100),
                ("saturation", "SATURATION", 0, 250, 100),
                ("brightness", "BRIGHTNESS", -50, 50, 0),
                ("scanlines", "SCANLINES", 0, 100, 0),
                ("chromatic", "RGB SPLIT", 0, 100, 0),
        ):
            label, slider = self._add_fx_slider(
                layer_fx_layout,
                title,
                minimum,
                maximum,
                default,
            )
            self.layer_fx_sliders[key] = (label, slider, title)
        controls_layout.addWidget(self.layer_fx_group)

        self.remove_layer_button = QPushButton("REMOVE LAYER")
        controls_layout.addWidget(self.remove_layer_button)
        controls_layout.addStretch(1)
        self.controls_scroll = QScrollArea()
        self.controls_scroll.setWidgetResizable(True)
        self.controls_scroll.setMinimumHeight(180)
        self.controls_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.controls_scroll.setWidget(controls_body)
        self.panel_splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.panel_splitter.setChildrenCollapsible(False)
        self.panel_splitter.setHandleWidth(6)
        self.panel_splitter.addWidget(self.table)
        self.panel_splitter.addWidget(self.controls_scroll)
        self.panel_splitter.setStretchFactor(0, 2)
        self.panel_splitter.setStretchFactor(1, 3)
        self.panel_splitter.setSizes([260, 360])
        layout.addWidget(self.panel_splitter, 1)

        self.layer_lock_check.toggled.connect(self._selected_layer_lock_changed)
        self.position_x[1].valueChanged.connect(self._position_x_changed)
        self.position_y[1].valueChanged.connect(self._position_y_changed)
        self.scale[1].valueChanged.connect(self._scale_changed)
        self.rotation[1].valueChanged.connect(self._rotation_changed)
        self.selected_blend_combo.currentTextChanged.connect(
            self._selected_blend_changed
        )
        self.modifier_add_button.clicked.connect(self._add_performance_modifier)
        self.modifier_beat_button.clicked.connect(
            lambda: self._add_rhythmic_modifier("transport.beat_pulse", 0.10)
        )
        self.modifier_downbeat_button.clicked.connect(
            lambda: self._add_rhythmic_modifier("transport.downbeat_pulse", 0.22)
        )
        self.modifier_phrase_button.clicked.connect(
            lambda: self._add_rhythmic_modifier("transport.phrase_pulse", 0.34)
        )
        self.modifier_remove_button.clicked.connect(self._remove_performance_modifier)
        self.layer_fx_enabled.toggled.connect(self._layer_fx_enabled_changed)
        self.layer_fx_preset.currentTextChanged.connect(self._layer_fx_preset_changed)
        self.fx_stage_list.itemDoubleClicked.connect(self._edit_fx_stage_amount)
        self.fx_stage_list.itemChanged.connect(lambda _item: self._commit_fx_stages())
        self.fx_stage_add.clicked.connect(self._add_fx_stage)
        self.fx_stage_remove.clicked.connect(self._remove_fx_stage)
        self.fx_stage_up.clicked.connect(lambda: self._move_fx_stage(-1))
        self.fx_stage_down.clicked.connect(lambda: self._move_fx_stage(1))
        self.fx_chain_save.clicked.connect(self._save_fx_chain)
        self.fx_chain_export.clicked.connect(self._export_fx_presets)
        self.fx_chain_import.clicked.connect(self._import_fx_presets)
        for key, (_label, slider, _title) in self.layer_fx_sliders.items():
            slider.valueChanged.connect(
                lambda value, field=key: self._layer_fx_value_changed(field, value)
            )
        self.remove_layer_button.clicked.connect(self.remove_selected_layer)
        self._loading = False
        self.refresh()

    @staticmethod
    def _add_slider(
            parent_layout: QVBoxLayout,
            title: str,
            minimum: int,
            maximum: int,
            value: int,
    ) -> tuple[QLabel, QSlider]:
        row = QHBoxLayout()
        label = QLabel(f"{title}  {value}")
        label.setMinimumWidth(96)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.valueChanged.connect(lambda current: label.setText(f"{title}  {current}"))
        row.addWidget(label)
        row.addWidget(slider, 1)
        parent_layout.addLayout(row)
        return label, slider

    @staticmethod
    def _add_fx_slider(
            parent_layout: QVBoxLayout,
            title: str,
            minimum: int,
            maximum: int,
            value: int,
    ) -> tuple[QLabel, QSlider]:
        row = QHBoxLayout()
        label = QLabel(f"{title}  {value}")
        label.setMinimumWidth(125)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.valueChanged.connect(lambda current: label.setText(f"{title}  {current}"))
        row.addWidget(label)
        row.addWidget(slider, 1)
        parent_layout.addLayout(row)
        return label, slider

    def refresh(self) -> None:
        selected_id = None
        current = self._selected_layer()
        if current is not None:
            selected_id = current.id
        self._loading = True
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for layer in self.application.composition.layers:
            row = self.table.rowCount()
            self.table.insertRow(row)

            visible = QTableWidgetItem()
            visible.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            visible.setCheckState(
                Qt.CheckState.Checked if layer.visible else Qt.CheckState.Unchecked
            )
            visible.setData(Qt.ItemDataRole.UserRole, layer.id)
            self.table.setItem(row, 0, visible)

            name = QTableWidgetItem(layer.name)
            name.setData(Qt.ItemDataRole.UserRole, layer.id)
            self.table.setItem(row, 1, name)

            opacity = QSlider(Qt.Orientation.Horizontal)
            opacity.setRange(0, 100)
            opacity.setValue(round(layer.opacity * 100))
            opacity.valueChanged.connect(
                lambda value, layer_id=layer.id: self._opacity_changed(layer_id, value)
            )
            opacity.setEnabled(not layer.locked)
            self.table.setCellWidget(row, 2, opacity)

            blend = QComboBox()
            blend.addItems(_BLEND_MODES)
            blend.setCurrentText(layer.blend_mode)
            blend.currentTextChanged.connect(
                lambda value, layer_id=layer.id: self._blend_changed(layer_id, value)
            )
            blend.setEnabled(not layer.locked)
            self.table.setCellWidget(row, 3, blend)
        self.table.blockSignals(False)
        if self.table.rowCount():
            selected_row = 0
            if selected_id:
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 1).data(Qt.ItemDataRole.UserRole) == selected_id:
                        selected_row = row
                        break
            self.table.setCurrentCell(selected_row, 1)
            self._selection_changed(selected_row, 1, -1, -1)
        self._loading = False

    def _selected_layer(self):
        row = self.table.currentRow()
        item = self.table.item(row, 1) if row >= 0 else None
        layer_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        return self.application.composition.get_layer(layer_id) if layer_id else None

    def select_layer(self, layer_id: str) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.data(Qt.ItemDataRole.UserRole) == layer_id:
                if self.table.currentRow() != row:
                    self.table.setCurrentCell(row, 1)
                return

    def sync_layer_row(self, layer_id: str) -> None:
        layer = self.application.composition.get_layer(layer_id)
        if layer is None:
            return
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if not item or item.data(Qt.ItemDataRole.UserRole) != layer_id:
                continue
            opacity = self.table.cellWidget(row, 2)
            blend = self.table.cellWidget(row, 3)
            if isinstance(opacity, QSlider):
                opacity.setEnabled(not layer.locked)
                opacity.blockSignals(True)
                opacity.setValue(round(layer.opacity * 100))
                opacity.blockSignals(False)
            if isinstance(blend, QComboBox):
                blend.setEnabled(not layer.locked)
                blend.blockSignals(True)
                blend.setCurrentText(layer.blend_mode)
                blend.blockSignals(False)
            if self._selected_layer() is not None and self._selected_layer().id == layer_id:
                self.selected_blend_combo.blockSignals(True)
                self.selected_blend_combo.setCurrentText(layer.blend_mode)
                self.selected_blend_combo.blockSignals(False)
            return

    def _selection_changed(
            self,
            current_row: int,
            current_column: int,
            previous_row: int,
            previous_column: int,
    ) -> None:
        layer = self._selected_layer()
        sliders = (self.position_x[1], self.position_y[1], self.scale[1], self.rotation[1])
        for slider in sliders:
            slider.blockSignals(True)
        self.remove_layer_button.setEnabled(layer is not None)
        self.layer_lock_check.blockSignals(True)
        self.layer_lock_check.setEnabled(layer is not None)
        self.layer_lock_check.setChecked(bool(layer and layer.locked))
        self.layer_lock_check.blockSignals(False)
        self.selected_blend_combo.blockSignals(True)
        self.selected_blend_combo.setEnabled(layer is not None)
        if layer is None:
            self.selected_blend_combo.setCurrentIndex(0)
        else:
            self.selected_blend_combo.setCurrentText(layer.blend_mode)
        self.selected_blend_combo.blockSignals(False)
        if layer is None:
            self.transform_group.setEnabled(False)
            self.performance_modifiers_group.setEnabled(False)
            self.layer_fx_group.setEnabled(False)
            self.modifier_target_combo.clear()
            self.position_x[1].setEnabled(False)
            self.position_y[1].setEnabled(False)
            self.scale[1].setEnabled(False)
            self.rotation[1].setEnabled(False)
        else:
            self.transform_group.setEnabled(not layer.locked)
            self.performance_modifiers_group.setEnabled(True)
            self._sync_performance_modifier_targets(layer)
            self.layer_fx_group.setEnabled(not layer.locked)
            self.position_x[1].setEnabled(not layer.locked)
            self.position_y[1].setEnabled(not layer.locked)
            self.scale[1].setEnabled(not layer.locked)
            self.rotation[1].setEnabled(not layer.locked)
            self.position_x[1].setValue(round(layer.position[0] * 100))
            self.position_y[1].setValue(round(layer.position[1] * 100))
            self.scale[1].setValue(round(layer.scale[0] * 100))
            self.rotation[1].setValue(round(layer.rotation))
            self._load_layer_effects(layer)
            self.refresh_performance_modifiers()
        for slider in sliders:
            slider.blockSignals(False)
        if layer is not None:
            self.selected_layer_changed.emit(layer.id)

    def _modifier_targets_for_layer(self, layer) -> list[str]:
        targets = [
            target_id for target_id, spec in PERF_MODIFIER_TARGETS.items()
            if spec.category == "layer"
        ]
        if layer.source_type == "generator":
            fields = {
                "geometry": {
                    "generator.animation_speed", "generator.animation_amount",
                    "generator.density", "generator.rotation",
                },
                "text": {
                    "generator.font_size", "generator.letter_spacing",
                },
                "waveform": {
                    "generator.animation_speed",
                    "generator.waveform_amplitude", "generator.waveform_frequency",
                },
                "particles": {
                    "generator.density", "generator.particle_speed",
                    "generator.particle_size", "generator.particle_spread",
                    "generator.particle_trail",
                },
            }
            targets.extend(sorted(fields.get(layer.generator_type, set())))
            if (
                    layer.generator_type == "text"
                    and layer.generator_settings.get("text_animation", "none") != "none"
            ):
                targets.extend((
                    "generator.text_animation_speed",
                    "generator.text_animation_amount",
                ))
        elif layer.source_type == "overlay":
            player = self.application._overlay_images.get(layer.id)
            if player is not None and player.animated:
                targets.extend(
                    target_id for target_id, spec in PERF_MODIFIER_TARGETS.items()
                    if spec.category == "overlay"
                )
        return targets

    def sync_performance_modifier_sources(self) -> None:
        current = self.modifier_source_combo.currentData()
        sources = dict(PERF_MODIFIER_SOURCES)
        for definition in self.application.modulator_bank.list_modulators():
            sources[f"modulator.{definition.modulator_id}"] = (
                f"Bank · {definition.name}"
            )
        self.modifier_source_combo.blockSignals(True)
        self.modifier_source_combo.clear()
        for source_id, label in sources.items():
            self.modifier_source_combo.addItem(label, source_id)
        index = self.modifier_source_combo.findData(current)
        if index >= 0:
            self.modifier_source_combo.setCurrentIndex(index)
        self.modifier_source_combo.blockSignals(False)

    def _sync_performance_modifier_targets(self, layer) -> None:
        self.sync_performance_modifier_sources()
        valid = self._modifier_targets_for_layer(layer)
        current = self.modifier_target_combo.currentData()
        self.modifier_target_combo.blockSignals(True)
        self.modifier_target_combo.clear()
        for target_id in valid:
            self.modifier_target_combo.addItem(
                PERF_MODIFIER_TARGETS[target_id].label,
                target_id,
            )
        index = self.modifier_target_combo.findData(current)
        if index < 0 and self.modifier_target_combo.count():
            target = self._default_modifier_target(layer)
            index = self.modifier_target_combo.findData(target)
        self.modifier_target_combo.setCurrentIndex(max(0, index))
        self.modifier_target_combo.blockSignals(False)
        self.modifier_source_combo.setEnabled(not layer.locked)
        self.modifier_target_combo.setEnabled(not layer.locked)
        self.modifier_curve_combo.setEnabled(not layer.locked)
        self.modifier_polarity_combo.setEnabled(not layer.locked)
        self.modifier_depth[1].setEnabled(not layer.locked)
        self.modifier_add_button.setEnabled(not layer.locked)
        for button in (
                self.modifier_beat_button,
                self.modifier_downbeat_button,
                self.modifier_phrase_button,
        ):
            button.setEnabled(not layer.locked)

    def _default_modifier_target(self, layer) -> str:
        if layer.source_type == "generator":
            return {
                "geometry": "generator.animation_amount",
                "text": (
                    "generator.text_animation_amount"
                    if layer.generator_settings.get("text_animation", "none") != "none"
                    else "generator.letter_spacing"
                ),
                "waveform": "generator.waveform_amplitude",
                "particles": "generator.particle_size",
            }.get(layer.generator_type, "layer.opacity")
        if layer.source_type == "overlay":
            return (
                "overlay.playback_speed"
                if self.modifier_target_combo.findData("overlay.playback_speed") >= 0
                else "layer.scale"
            )
        return "layer.scale"

    def _add_performance_modifier(self) -> None:
        self._create_performance_modifier(
            str(self.modifier_source_combo.currentData() or "transport.beat_pulse"),
            str(self.modifier_target_combo.currentData() or ""),
            self.modifier_depth[1].value() / 100.0,
        )

    def _add_rhythmic_modifier(self, source_id: str, depth: float) -> None:
        layer = self._selected_layer()
        if layer is None or layer.locked:
            return
        target_id = self._default_modifier_target(layer)
        index = self.modifier_target_combo.findData(target_id)
        if index >= 0:
            self.modifier_target_combo.setCurrentIndex(index)
        self._create_performance_modifier(source_id, target_id, depth)

    def _create_performance_modifier(
            self,
            source_id: str,
            target_id: str,
            depth: float,
    ) -> None:
        layer = self._selected_layer()
        if layer is None or layer.locked or not target_id:
            return
        source_label = PERF_MODIFIER_SOURCES.get(source_id)
        if source_label is None and source_id.startswith("modulator."):
            definition = self.application.modulator_bank.get(
                source_id.removeprefix("modulator.")
            )
            source_label = (
                f"Bank · {definition.name}" if definition is not None else source_id
            )
        source_label = source_label or source_id
        target_label = PERF_MODIFIER_TARGETS[target_id].label
        modifier = LayerPerformanceModifier(
            name=f"{source_label.split('·')[-1].strip()} → {target_label}",
            source_id=source_id,
            target_id=target_id,
            depth=depth,
            polarity=str(self.modifier_polarity_combo.currentData() or "positive"),
            curve=str(self.modifier_curve_combo.currentData() or "smoothstep"),
        )
        try:
            self.application.add_layer_performance_modifier(layer.id, modifier)
        except (TypeError, ValueError, KeyError) as exc:
            QMessageBox.warning(self, "Performance modifier", str(exc))
            return
        self._modifier_signature = ()
        self.refresh_performance_modifiers()

    def _remove_performance_modifier(self) -> None:
        layer = self._selected_layer()
        item = self.modifier_list.currentItem()
        modifier_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        if layer is None or not modifier_id:
            return
        self.application.remove_layer_performance_modifier(layer.id, str(modifier_id))
        self._modifier_signature = ()
        self.refresh_performance_modifiers()

    def _toggle_performance_modifier(self, layer_id: str, modifier_id: str, enabled: bool) -> None:
        layer = self.application.composition.get_layer(layer_id)
        if layer is None:
            return
        for raw in layer.performance_modifiers:
            if str(raw.get("modifier_id", "")) == modifier_id:
                raw["enabled"] = bool(enabled)
                break
        self._modifier_signature = ()

    def refresh_performance_modifiers(self, force: bool = False) -> None:
        layer = self._selected_layer()
        sources = self.application._modulation_sources()
        self.modifier_rhythm_status.setText(
            "BT {beat:.2f} · DOWNBT {downbeat:.2f} · PHRASE {phrase:.2f}".format(
                beat=sources.get("transport.beat_pulse", 0.0),
                downbeat=sources.get("transport.downbeat_pulse", 0.0),
                phrase=sources.get("transport.phrase_pulse", 0.0),
            )
        )
        # The layer table shows live opacity for every layer, not only the selected one.
        for row_index in range(self.table.rowCount()):
            name_item = self.table.item(row_index, 1)
            if name_item is None:
                continue
            row_layer = self.application.composition.get_layer(
                str(name_item.data(Qt.ItemDataRole.UserRole) or "")
            )
            opacity_widget = self.table.cellWidget(row_index, 2)
            if row_layer is not None and isinstance(opacity_widget, QSlider):
                opacity_widget.blockSignals(True)
                opacity_widget.setValue(round(row_layer.opacity * 100))
                opacity_widget.blockSignals(False)

        if layer is None:
            self.modifier_list.clear()
            self._modifier_widgets.clear()
            self._modifier_signature = ()
            self.modifier_remove_button.setEnabled(False)
            return
        records = []
        for raw in layer.performance_modifiers:
            if not isinstance(raw, dict):
                continue
            try:
                records.append(LayerPerformanceModifier.from_dict(raw).to_dict())
            except (TypeError, ValueError, KeyError):
                continue
        self.modifier_remove_button.setEnabled(bool(records) and not layer.locked)
        signature = tuple(
            (
                str(raw.get("modifier_id", "")),
                str(raw.get("name", "")),
                str(raw.get("source_id", "")),
                str(raw.get("target_id", "")),
                round(float(raw.get("depth", 0.0)), 4),
                bool(raw.get("enabled", True)),
            )
            for raw in records
        )
        if force or signature != self._modifier_signature:
            self.modifier_list.clear()
            self._modifier_widgets.clear()
            for raw in records:
                modifier_id = str(raw.get("modifier_id", ""))
                source_id = str(raw.get("source_id", ""))
                source_label = PERF_MODIFIER_SOURCES.get(source_id)
                if source_label is None and source_id.startswith("modulator."):
                    definition = self.application.modulator_bank.get(
                        source_id.removeprefix("modulator.")
                    )
                    source_label = (
                        f"Bank · {definition.name}"
                        if definition is not None
                        else source_id
                    )
                source_label = source_label or source_id or "unknown source"
                target_spec = PERF_MODIFIER_TARGETS.get(str(raw.get("target_id", "")))
                target_label = target_spec.label if target_spec else str(raw.get("target_id", ""))
                depth = float(raw.get("depth", 0.0))
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, modifier_id)
                row = QWidget()
                row_layout = QVBoxLayout(row)
                row_layout.setContentsMargins(4, 2, 4, 2)
                header = QHBoxLayout()
                enabled = QCheckBox(str(raw.get("name", "Modifier")))
                enabled.setChecked(bool(raw.get("enabled", True)))
                enabled.setEnabled(not layer.locked)
                header.addWidget(enabled)
                header.addStretch(1)
                header.addWidget(QLabel(f"{depth * 100:.0f}%"))
                row_layout.addLayout(header)
                detail = QLabel(f"{source_label} → {target_label}")
                detail.setObjectName("mutedLabel")
                detail.setWordWrap(True)
                row_layout.addWidget(detail)
                meter = QProgressBar()
                meter.setRange(0, 100)
                meter.setTextVisible(True)
                meter.setFormat("LIVE %p%")
                meter.setMaximumHeight(14)
                row_layout.addWidget(meter)
                row.adjustSize()
                item.setSizeHint(row.sizeHint())
                self.modifier_list.addItem(item)
                enabled.toggled.connect(
                    lambda state, owner=layer.id, mid=modifier_id:
                    self._toggle_performance_modifier(owner, mid, state)
                )
                self.modifier_list.setItemWidget(item, row)
                self._modifier_widgets[modifier_id] = (enabled, detail, meter)
            self._modifier_signature = signature

        # Keep the transform controls honest while a modifier is moving the layer.
        transform_values = (
            (self.position_x, "X POSITION", round(layer.position[0] * 100)),
            (self.position_y, "Y POSITION", round(layer.position[1] * 100)),
            (self.scale, "UNIFORM SCALE", round(layer.scale[0] * 100)),
            (self.rotation, "ROTATION", round(layer.rotation)),
        )
        for (label, slider), title, value in transform_values:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            label.setText(f"{title}  {value}")
        live = self.application.layer_performance_modifier_values(layer.id)
        for modifier_id, (_enabled, _detail, meter) in self._modifier_widgets.items():
            value = live.get(modifier_id)
            meter.setValue(round(max(0.0, min(1.0, value or 0.0)) * 100))
            meter.setFormat(f"LIVE {value:.2f}" if value is not None else "IDLE")

    def _load_layer_effects(self, layer) -> None:
        values = normalize_layer_effects(layer.layer_effects)
        self.layer_fx_enabled.blockSignals(True)
        self.layer_fx_enabled.setChecked(values["enabled"])
        self.layer_fx_enabled.blockSignals(False)
        self._loading = True
        for key, (label, slider, title) in self.layer_fx_sliders.items():
            slider.blockSignals(True)
            scale = 1.0 if key == "hue" else 100.0
            value = round(float(values[key]) * scale)
            slider.setValue(value)
            slider.blockSignals(False)
            label.setText(f"{title}  {value}")
        self.layer_fx_preset.blockSignals(True)
        imported = self.application.composition.metadata.get("layer_fx_presets", {})
        known_names = (
                list(LY_EFFECT_PSETS)
                + ["Xerox Stack", "Negative Print", "Signal Scan"]
                + (
                    list(imported) if isinstance(imported, dict) else []
                )
        )
        self.layer_fx_preset.clear()
        self.layer_fx_preset.addItems(list(dict.fromkeys(known_names)) + ["Custom"])
        self.layer_fx_preset.setCurrentText("Custom")
        for name in LY_EFFECT_PSETS:
            if normalize_layer_effects({
                **LY_EFFECT_PSETS[name],
                "enabled": name != "Clean",
            }) == values:
                self.layer_fx_preset.setCurrentText(name)
                break
        for name in ("Xerox Stack", "Negative Print", "Signal Scan"):
            if apply_effect_chain_preset(name)["stages"] == values["stages"]:
                self.layer_fx_preset.setCurrentText(name)
                break
        if isinstance(imported, dict):
            for name, stages in imported.items():
                if values["stages"] == normalize_layer_effects({"stages": stages})["stages"]:
                    self.layer_fx_preset.setCurrentText(str(name))
                    break
        self.layer_fx_preset.blockSignals(False)
        self.fx_stage_list.clear()
        for stage in values["stages"]:
            title = EFFECT_STAGE_TYPES[stage["type"]]
            item = QListWidgetItem(f'{title} · {stage["amount"]:.2f}')
            item.setData(Qt.ItemDataRole.UserRole, dict(stage))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if stage["enabled"] else Qt.CheckState.Unchecked
            )
            self.fx_stage_list.addItem(item)
        self._loading = False

    def _commit_fx_stages(self) -> None:
        stages = []
        for index in range(self.fx_stage_list.count()):
            item = self.fx_stage_list.item(index)
            stage = dict(item.data(Qt.ItemDataRole.UserRole) or {})
            stage["enabled"] = item.checkState() == Qt.CheckState.Checked
            stages.append(stage)
        self._update_selected_layer_effects({"stages": stages})

    def _edit_fx_stage_amount(self, item) -> None:
        stage = dict(item.data(Qt.ItemDataRole.UserRole) or {})
        value, accepted = QInputDialog.getDouble(
            self, "Effect stage amount", "Amount", float(stage.get("amount", 1.0)),
            0.0, 1.0, 2,
        )
        if not accepted:
            return
        stage["amount"] = value
        item.setData(Qt.ItemDataRole.UserRole, stage)
        item.setText(f'{EFFECT_STAGE_TYPES[stage["type"]]} · {value:.2f}')
        self._commit_fx_stages()

    def _add_fx_stage(self) -> None:
        kind = self.fx_stage_type.currentData()
        amount = {"contrast": 0.0, "saturation": 0.0, "brightness": 0.5}.get(kind, 1.0)
        item = QListWidgetItem(f'{EFFECT_STAGE_TYPES[kind]} · {amount:.2f}')
        item.setData(Qt.ItemDataRole.UserRole, {"type": kind, "amount": amount, "enabled": True})
        item.setCheckState(Qt.CheckState.Checked)
        self.fx_stage_list.addItem(item)
        self._commit_fx_stages()

    def _remove_fx_stage(self) -> None:
        row = self.fx_stage_list.currentRow()
        if row >= 0:
            self.fx_stage_list.takeItem(row)
            self._commit_fx_stages()

    def _move_fx_stage(self, offset: int) -> None:
        row = self.fx_stage_list.currentRow()
        target = row + offset
        if row < 0 or target < 0 or target >= self.fx_stage_list.count():
            return
        item = self.fx_stage_list.takeItem(row)
        self.fx_stage_list.insertItem(target, item)
        self.fx_stage_list.setCurrentRow(target)
        self._commit_fx_stages()

    def _save_fx_chain(self) -> None:
        layer = self._selected_layer()
        if layer is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save layer FX chain", "layer-fx-chain.json", "JSON (*.json)"
        )
        if not path:
            return
        import json
        payload = {
            "format": "eli_lab_layer_fx_chain",
            "version": 1,
            "name": layer.name,
            "chain": normalize_layer_effects(layer.layer_effects)["stages"],
        }
        try:
            from pathlib import Path
            Path(path).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            QMessageBox.warning(self, "FX chain", str(exc))

    def _export_fx_presets(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export project FX presets",
            "layer-fx-presets.json",
            "JSON (*.json)",
        )
        if not path:
            return
        import json
        presets = {
            "Xerox Stack": [{"type": "monochrome", "amount": 1.0, "enabled": True},
                            {"type": "threshold", "amount": 0.45, "enabled": True}],
            "Negative Print": [{"type": "invert", "amount": 1.0, "enabled": True},
                               {"type": "posterize", "amount": 0.55, "enabled": True}],
            "Signal Scan": [{"type": "hue", "amount": 0.22, "enabled": True},
                            {"type": "scanlines", "amount": 0.7, "enabled": True}],
        }
        imported = self.application.composition.metadata.get("layer_fx_presets", {})
        if isinstance(imported, dict):
            presets.update(imported)
        try:
            from pathlib import Path
            Path(path).write_text(
                json.dumps(
                    {
                        "format": "eli_lab_layer_fx_presets",
                        "version": 1,
                        "presets": presets,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError as exc:
            QMessageBox.warning(self, "FX presets", str(exc))

    def _import_fx_presets(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import layer FX chain or presets", "", "JSON (*.json)"
        )
        if not path:
            return
        import json
        from pathlib import Path
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            if payload.get("format") == "eli_lab_layer_fx_chain":
                stages = normalize_layer_effects({"stages": payload.get("chain", [])})["stages"]
                self._update_selected_layer_effects({"stages": stages, "enabled": bool(stages)})
                self._load_layer_effects(self._selected_layer())
            elif payload.get("format") == "eli_lab_layer_fx_presets":
                presets = payload.get("presets", {})
                if not isinstance(presets, dict):
                    raise ValueError("Preset collection must be an object.")
                # Imported project presets are stored in composition metadata.
                safe = {str(name): normalize_layer_effects({"stages": stages})["stages"]
                        for name, stages in presets.items() if isinstance(stages, list)}
                self.application.composition.metadata["layer_fx_presets"] = safe
                QMessageBox.information(
                    self, "FX presets", f"Imported {len(safe)} project preset(s)."
                )
            else:
                raise ValueError("Unsupported FX preset file.")
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.warning(self, "FX presets", str(exc))

    def _update_selected_layer_effects(self, changes: dict[str, object]) -> None:
        layer = self._selected_layer()
        if layer is None or self._loading:
            return
        values = normalize_layer_effects(layer.layer_effects)
        values.update(changes)
        self.application.layer_manager.update_layer(
            layer.id,
            layer_effects=normalize_layer_effects(values),
            fx_manual_override_until=time.time() + 30.0,
        )

    def _layer_fx_enabled_changed(self, enabled: bool) -> None:
        self._update_selected_layer_effects({"enabled": bool(enabled)})

    def _layer_fx_preset_changed(self, name: str) -> None:
        if name == "Custom" or self._loading:
            return
        from effects.layer_settings import apply_layer_effect_preset

        layer = self._selected_layer()
        if layer is None:
            return
        imported = self.application.composition.metadata.get("layer_fx_presets", {})
        if isinstance(imported, dict) and name in imported:
            stages = normalize_layer_effects({"stages": imported[name]})["stages"]
            values = normalize_layer_effects({"enabled": bool(stages), "stages": stages})
        elif name in {"Xerox Stack", "Negative Print", "Signal Scan"}:
            values = apply_effect_chain_preset(name)
        else:
            values = apply_layer_effect_preset(name)
        self.application.layer_manager.update_layer(
            layer.id,
            layer_effects=values,
            fx_manual_override_until=time.time() + 30.0,
        )
        self._loading = True
        self._load_layer_effects(layer)
        self._loading = False

    def _layer_fx_value_changed(self, key: str, value: int) -> None:
        if self._loading:
            return
        scale = 1.0 if key == "hue" else 100.0
        mapped = value / scale
        self._update_selected_layer_effects({key: mapped})
        self.layer_fx_preset.blockSignals(True)
        self.layer_fx_preset.setCurrentText("Custom")
        self.layer_fx_preset.blockSignals(False)

    def remove_selected_layer(self) -> None:
        layer = self._selected_layer()
        if layer is None:
            return
        self.application.remove_layer(layer.id)
        self.refresh()
        self.layers_changed.emit()

    def _visibility_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != 0:
            return
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        if layer_id:
            self.application.layer_manager.update_layer(
                layer_id,
                visible=item.checkState() == Qt.CheckState.Checked,
            )

    def _selected_layer_lock_changed(self, locked: bool) -> None:
        layer = self._selected_layer()
        if layer is None:
            return
        self.application.set_layer_locked(layer.id, locked)
        self._selection_changed(
            self.table.currentRow(),
            self.table.currentColumn(),
            -1,
            -1,
        )
        self.layer_properties_changed.emit(layer.id)

    def _opacity_changed(self, layer_id: str, value: int) -> None:
        layer = self.application.composition.get_layer(layer_id)
        if layer is None or layer.locked:
            return
        self.application.layer_manager.update_layer(layer_id, opacity=value / 100.0)
        self.layer_properties_changed.emit(layer_id)

    def _blend_changed(self, layer_id: str, value: str) -> None:
        layer = self.application.composition.get_layer(layer_id)
        if layer is None or layer.locked:
            return
        changes = {"blend_mode": value}
        if layer is not None and layer.source_type == "overlay":
            changes["overlay_manual_override_until"] = time.time() + 30.0
        self.application.layer_manager.update_layer(layer_id, **changes)
        self.layer_properties_changed.emit(layer_id)
        layer = self._selected_layer()
        if layer is not None and layer.id == layer_id:
            self.selected_blend_combo.blockSignals(True)
            self.selected_blend_combo.setCurrentText(value)
            self.selected_blend_combo.blockSignals(False)

    def _selected_blend_changed(self, value: str) -> None:
        layer = self._selected_layer()
        if layer is None or self._loading:
            return
        changes = {"blend_mode": value}
        if layer.source_type == "overlay":
            changes["overlay_manual_override_until"] = time.time() + 30.0
        self.application.layer_manager.update_layer(layer.id, **changes)
        self.layer_properties_changed.emit(layer.id)
        row = self.table.currentRow()
        blend = self.table.cellWidget(row, 3) if row >= 0 else None
        if isinstance(blend, QComboBox) and blend.currentText() != value:
            blend.blockSignals(True)
            blend.setCurrentText(value)
            blend.blockSignals(False)

    def _position_x_changed(self, value: int) -> None:
        layer = self._selected_layer()
        if layer:
            self.application.layer_manager.update_layer(
                layer.id, position=(value / 100.0, layer.position[1])
            )
            self.layer_properties_changed.emit(layer.id)

    def _position_y_changed(self, value: int) -> None:
        layer = self._selected_layer()
        if layer:
            self.application.layer_manager.update_layer(
                layer.id, position=(layer.position[0], value / 100.0)
            )
            self.layer_properties_changed.emit(layer.id)

    def _scale_changed(self, value: int) -> None:
        layer = self._selected_layer()
        if layer:
            amount = value / 100.0
            self.application.layer_manager.update_layer(
                layer.id, scale=(amount, amount)
            )
            self.layer_properties_changed.emit(layer.id)

    def _rotation_changed(self, value: int) -> None:
        layer = self._selected_layer()
        if layer:
            self.application.layer_manager.update_layer(layer.id, rotation=float(value))
            self.layer_properties_changed.emit(layer.id)
