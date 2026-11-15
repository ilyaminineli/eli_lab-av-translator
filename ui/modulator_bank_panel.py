from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from core.modulator_bank import (
    FOLLOWER_SOURCES,
    TRIGGER_SOURCES,
    ModulatorDefinition,
    euclidean_pattern,
)
from core.performance_modifiers import (
    PERF_MODIFIER_TARGETS,
    LayerPerformanceModifier,
)
from ui.i18n import set_ui_text, ui_text
from ui.panel_layout import configure_inspector_form


class ModulatorBankPanel(QWidget):
    """Dedicated editor for reusable envelope, LFO, step and rhythm sources."""

    bank_changed = Signal()
    assignment_created = Signal(str)

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self._loading = False
        self._selected_id: str | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        body.setMinimumWidth(0)
        root = QVBoxLayout(body)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        bank_group = QGroupBox("MOD BANK")
        bank_group.setToolTip("MOD BANK · REUSABLE SOURCES")
        bank_layout = QVBoxLayout(bank_group)
        self.modulator_list = QListWidget()
        self.modulator_list.setMinimumHeight(112)
        self.modulator_list.setMaximumHeight(190)
        bank_layout.addWidget(self.modulator_list)

        create_grid = QGridLayout()
        self.new_lfo_button = QPushButton("+ LFO")
        self.new_envelope_button = QPushButton("+ ENV")
        self.new_steps_button = QPushButton("+ STEPS")
        self.new_rhythm_button = QPushButton("+ RHYTHM")
        self.new_follower_button = QPushButton("+ FOLLOWER")
        self.new_lfo_button.setToolTip("Create a low-frequency oscillator")
        self.new_envelope_button.setToolTip("Create an envelope modulator")
        self.new_steps_button.setToolTip("Create a stepped sequence modulator")
        self.new_rhythm_button.setToolTip("Create a beat / downbeat rhythm modulator")
        self.new_follower_button.setToolTip("Create an audio envelope follower")
        create_grid.setHorizontalSpacing(6)
        create_grid.setVerticalSpacing(6)
        create_grid.addWidget(self.new_lfo_button, 0, 0)
        create_grid.addWidget(self.new_envelope_button, 0, 1)
        create_grid.addWidget(self.new_steps_button, 1, 0)
        create_grid.addWidget(self.new_rhythm_button, 1, 1)
        create_grid.addWidget(self.new_follower_button, 2, 0, 1, 2)
        create_grid.setColumnStretch(0, 1)
        create_grid.setColumnStretch(1, 1)
        bank_layout.addLayout(create_grid)

        edit_row = QHBoxLayout()
        self.duplicate_button = QPushButton("DUPLICATE")
        self.remove_button = QPushButton("REMOVE")
        edit_row.addWidget(self.duplicate_button)
        edit_row.addWidget(self.remove_button)
        bank_layout.addLayout(edit_row)
        root.addWidget(bank_group)

        preset_group = QGroupBox("PRESET LIBRARY")
        preset_layout = QVBoxLayout(preset_group)
        self.preset_combo = QComboBox()
        self.preset_combo.currentIndexChanged.connect(self._update_preset_actions)
        preset_layout.addWidget(self.preset_combo)
        preset_buttons = QHBoxLayout()
        self.load_preset_button = QPushButton("LOAD")
        self.save_preset_button = QPushButton("SAVE AS")
        self.delete_preset_button = QPushButton("DELETE PRESET")
        self.load_preset_button.setToolTip("Load the selected modulator preset")
        self.save_preset_button.setToolTip(
            "Save the current modulator as a user preset"
        )
        self.delete_preset_button.setToolTip("Delete the selected user preset")
        preset_buttons.addWidget(self.load_preset_button)
        preset_buttons.addWidget(self.save_preset_button)
        preset_layout.addLayout(preset_buttons)
        preset_layout.addWidget(self.delete_preset_button)
        preset_io_row = QHBoxLayout()
        self.export_presets_button = QPushButton("EXPORT")
        self.import_presets_button = QPushButton("IMPORT")
        self.export_presets_button.setToolTip("Export user modulator presets")
        self.import_presets_button.setToolTip("Import modulator presets from a file")
        preset_io_row.addWidget(self.export_presets_button)
        preset_io_row.addWidget(self.import_presets_button)
        preset_layout.addLayout(preset_io_row)
        root.addWidget(preset_group)

        editor_group = QGroupBox("MODULATOR EDITOR")
        editor = QVBoxLayout(editor_group)
        common_form = QFormLayout()
        configure_inspector_form(common_form)
        self.name_edit = QLineEdit()
        self.enabled_check = QCheckBox("ENABLED")
        self.sync_combo = QComboBox()
        self.sync_combo.addItem("SYNC TO TRANSPORT", "transport")
        self.sync_combo.addItem("FREE RUN", "free")
        self.reset_combo = QComboBox()
        self.reset_combo.addItem("CONTINUOUS", "transport")
        self.reset_combo.addItem("RESET EVERY BAR", "bar")
        self.reset_combo.addItem("RESET EVERY PHRASE", "phrase")
        common_form.addRow("NAME", self.name_edit)
        common_form.addRow(self.enabled_check)
        common_form.addRow("TIMEBASE", self.sync_combo)
        common_form.addRow("PHASE RESET", self.reset_combo)
        editor.addLayout(common_form)

        self.lfo_group = QGroupBox("LFO")
        self.lfo_group.setToolTip("LFO · CYCLIC WAVEFORM")
        lfo_form = QFormLayout(self.lfo_group)
        configure_inspector_form(lfo_form)
        lfo_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        lfo_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.waveform_combo = QComboBox()
        for value, label in (
            ("sine", "Sine"),
            ("triangle", "Triangle"),
            ("saw_up", "Saw up"),
            ("saw_down", "Saw down"),
            ("square", "Square"),
            ("pulse", "Pulse width"),
            ("sample_hold", "Sample & hold"),
        ):
            self.waveform_combo.addItem(label, value)
        self.lfo_rate_beats = self._double_spin(0.0625, 256.0, 4.0, 4)
        self.lfo_rate_hz = self._double_spin(0.005, 30.0, 0.25, 3)
        self.lfo_phase = self._double_spin(0.0, 1.0, 0.0, 3)
        self.lfo_pulse_width = self._double_spin(0.02, 0.98, 0.5, 2)
        lfo_form.addRow("WAVEFORM", self.waveform_combo)
        lfo_form.addRow("PERIOD · BEATS", self.lfo_rate_beats)
        lfo_form.addRow("RATE · HZ (FREE)", self.lfo_rate_hz)
        lfo_form.addRow("PHASE", self.lfo_phase)
        lfo_form.addRow("PULSE WIDTH", self.lfo_pulse_width)
        editor.addWidget(self.lfo_group)

        self.follower_group = QGroupBox("FOLLOWER")
        self.follower_group.setToolTip("CONTROL FOLLOWER · SONIC PI / AUDIO")
        follower_form = QFormLayout(self.follower_group)
        configure_inspector_form(follower_form)
        follower_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        follower_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.input_source_combo = QComboBox()
        for source_id, label in FOLLOWER_SOURCES.items():
            self.input_source_combo.addItem(label, source_id)
        self.input_min_spin = self._double_spin(0.0, 1.0, 0.0, 3)
        self.input_max_spin = self._double_spin(0.0, 1.0, 1.0, 3)
        self.input_curve_combo = QComboBox()
        self.input_curve_combo.addItem("Linear", "linear")
        self.input_curve_combo.addItem("Smoothstep", "smoothstep")
        self.input_curve_combo.addItem("Exponential", "exponential")
        self.input_invert_check = QCheckBox("INVERT INPUT")
        self.input_attack_spin = self._double_spin(1.0, 5000.0, 80.0, 1)
        self.input_release_spin = self._double_spin(1.0, 10000.0, 600.0, 1)
        follower_form.addRow("INPUT SOURCE", self.input_source_combo)
        follower_form.addRow("INPUT MIN", self.input_min_spin)
        follower_form.addRow("INPUT MAX", self.input_max_spin)
        follower_form.addRow("RESPONSE CURVE", self.input_curve_combo)
        follower_form.addRow(self.input_invert_check)
        follower_form.addRow("ATTACK · ms", self.input_attack_spin)
        follower_form.addRow("RELEASE · ms", self.input_release_spin)
        editor.addWidget(self.follower_group)

        self.envelope_group = QGroupBox("ENVELOPE · ADSR")
        envelope_form = QFormLayout(self.envelope_group)
        configure_inspector_form(envelope_form)
        envelope_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        envelope_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.trigger_combo = QComboBox()
        for source_id, label in TRIGGER_SOURCES.items():
            self.trigger_combo.addItem(label, source_id)
        self.retrigger_combo = QComboBox()
        self.retrigger_combo.addItem("RESTART", "restart")
        self.retrigger_combo.addItem("LEGATO", "legato")
        self.attack_spin = self._double_spin(0.0, 64.0, 0.03, 3)
        self.decay_spin = self._double_spin(0.0, 64.0, 0.16, 3)
        self.sustain_spin = self._double_spin(0.0, 1.0, 0.2, 3)
        self.gate_spin = self._double_spin(0.0, 256.0, 0.2, 3)
        self.release_spin = self._double_spin(0.0, 64.0, 0.5, 3)
        self.trigger_threshold_spin = self._double_spin(0.0, 1.0, 0.5, 3)
        envelope_form.addRow("TRIGGER", self.trigger_combo)
        envelope_form.addRow("TRIGGER THRESHOLD", self.trigger_threshold_spin)
        envelope_form.addRow("RETRIGGER", self.retrigger_combo)
        envelope_form.addRow("ATTACK", self.attack_spin)
        envelope_form.addRow("DECAY", self.decay_spin)
        envelope_form.addRow("SUSTAIN", self.sustain_spin)
        envelope_form.addRow("GATE / HOLD", self.gate_spin)
        envelope_form.addRow("RELEASE", self.release_spin)
        editor.addWidget(self.envelope_group)

        self.sequence_group = QGroupBox("STEP SEQUENCER")
        self.sequence_group.setToolTip("STEP SEQUENCER / RHYTHM GRID")
        sequence_form = QFormLayout(self.sequence_group)
        configure_inspector_form(sequence_form)
        sequence_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        sequence_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.steps_edit = QLineEdit()
        self.steps_edit.setPlaceholderText("1, 0, 0.5, 0")
        self.division_spin = self._double_spin(1.0 / 96.0, 64.0, 0.25, 4)
        self.step_rate_spin = self._double_spin(0.01, 64.0, 4.0, 3)
        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItem("HOLD / QUANTIZED", "hold")
        self.interpolation_combo.addItem("LINEAR", "linear")
        self.interpolation_combo.addItem("SMOOTH", "smooth")
        self.direction_combo = QComboBox()
        self.direction_combo.addItem("FORWARD", "forward")
        self.direction_combo.addItem("REVERSE", "reverse")
        self.direction_combo.addItem("PING-PONG", "pingpong")
        self.direction_combo.addItem("SEEDED RANDOM", "random")
        self.swing_spin = self._double_spin(0.5, 0.75, 0.5, 3)
        self.sequence_pulse_width = self._double_spin(0.02, 0.98, 0.4, 2)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2_147_483_647)
        self.seed_spin.setValue(211)
        self.euclidean_group = QGroupBox("EUCLIDEAN RHYTHM")
        self.euclidean_group.setToolTip("EUCLIDEAN RHYTHM GENERATOR")
        euclidean_form = QFormLayout(self.euclidean_group)
        configure_inspector_form(euclidean_form)
        euclidean_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        euclidean_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.euclidean_pulses = QSpinBox()
        self.euclidean_pulses.setRange(0, 64)
        self.euclidean_pulses.setValue(3)
        self.euclidean_steps = QSpinBox()
        self.euclidean_steps.setRange(1, 64)
        self.euclidean_steps.setValue(8)
        self.euclidean_rotation = QSpinBox()
        self.euclidean_rotation.setRange(0, 63)
        self.euclidean_rotation.setValue(0)
        self.euclidean_generate_button = QPushButton("GENERATE EUCLIDEAN PATTERN")
        euclidean_form.addRow("PULSES", self.euclidean_pulses)
        euclidean_form.addRow("GRID STEPS", self.euclidean_steps)
        euclidean_form.addRow("ROTATION", self.euclidean_rotation)
        euclidean_form.addRow(self.euclidean_generate_button)
        sequence_form.addRow(self.euclidean_group)
        sequence_form.addRow("STEP VALUES · 0–1", self.steps_edit)
        sequence_form.addRow("DIVISION · BEATS", self.division_spin)
        sequence_form.addRow("STEP RATE · HZ (FREE)", self.step_rate_spin)
        sequence_form.addRow("INTERPOLATION", self.interpolation_combo)
        sequence_form.addRow("DIRECTION", self.direction_combo)
        sequence_form.addRow("SWING · 0.50 = STRAIGHT", self.swing_spin)
        sequence_form.addRow("GATE / PULSE WIDTH", self.sequence_pulse_width)
        sequence_form.addRow("RANDOM SEED", self.seed_spin)
        editor.addWidget(self.sequence_group)

        self.apply_button = QPushButton("APPLY MOD CHANGES")
        editor.addWidget(self.apply_button)
        root.addWidget(editor_group)

        assignment_group = QGroupBox("ASSIGNMENT")
        assignment_group.setToolTip("ASSIGN TO SELECTED LAYER")
        assignment_form = QFormLayout(assignment_group)
        configure_inspector_form(assignment_form)
        assignment_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        assignment_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.assignment_layer_label = QLabel("No layer selected")
        self.assignment_layer_label.setWordWrap(True)
        self.assignment_target_combo = QComboBox()
        self.assignment_depth = QSlider(Qt.Orientation.Horizontal)
        self.assignment_depth.setRange(0, 100)
        self.assignment_depth.setValue(20)
        self.assignment_depth_label = QLabel("20%")
        depth_row = QHBoxLayout()
        depth_row.addWidget(self.assignment_depth, 1)
        depth_row.addWidget(self.assignment_depth_label)
        self.assignment_polarity_combo = QComboBox()
        self.assignment_polarity_combo.addItem("AUTO · TYPE DEFAULT", "auto")
        self.assignment_polarity_combo.addItem("BIPOLAR · CENTRED", "bipolar")
        self.assignment_polarity_combo.addItem("POSITIVE · ONE WAY", "positive")
        assignment_form.addRow("LAYER", self.assignment_layer_label)
        assignment_form.addRow("TARGET", self.assignment_target_combo)
        assignment_form.addRow("DEPTH", depth_row)
        assignment_form.addRow("RESPONSE", self.assignment_polarity_combo)
        self.assign_button = QPushButton("ASSIGN MODULATOR TO LAYER")
        assignment_form.addRow(self.assign_button)
        root.addWidget(assignment_group)

        output_group = QGroupBox("LIVE OUTPUT")
        output_layout = QVBoxLayout(output_group)
        self.input_live_label = QLabel("INPUT · —")
        self.input_live_label.setObjectName("mutedLabel")
        self.output_label = QLabel("OUTPUT · 0.50")
        self.output_meter = QProgressBar()
        self.output_meter.setRange(0, 100)
        self.output_meter.setFormat("%p%")
        output_layout.addWidget(self.input_live_label)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_meter)
        root.addWidget(output_group)

        root.addStretch(1)
        self.scroll.setWidget(body)
        outer.addWidget(self.scroll)

        self.new_lfo_button.clicked.connect(lambda: self._create_modulator("lfo"))
        self.new_envelope_button.clicked.connect(
            lambda: self._create_modulator("envelope")
        )
        self.new_steps_button.clicked.connect(lambda: self._create_modulator("steps"))
        self.new_rhythm_button.clicked.connect(lambda: self._create_modulator("rhythm"))
        self.new_follower_button.clicked.connect(
            lambda: self._create_modulator("follower")
        )
        self.duplicate_button.clicked.connect(self._duplicate_selected)
        self.remove_button.clicked.connect(self._remove_selected)
        self.modulator_list.currentItemChanged.connect(self._selection_changed)
        self.apply_button.clicked.connect(self._apply_editor)
        self.load_preset_button.clicked.connect(self._load_preset)
        self.save_preset_button.clicked.connect(self._save_preset)
        self.delete_preset_button.clicked.connect(self._delete_preset)
        self.export_presets_button.clicked.connect(self._export_presets)
        self.import_presets_button.clicked.connect(self._import_presets)
        self.assignment_depth.valueChanged.connect(
            lambda value: self.assignment_depth_label.setText(f"{value}%")
        )
        self.assign_button.clicked.connect(self._assign_selected)
        self.sync_combo.currentIndexChanged.connect(self._sync_timebase_controls)
        self.euclidean_steps.valueChanged.connect(
            lambda value: self.euclidean_pulses.setMaximum(value)
        )
        self.euclidean_generate_button.clicked.connect(self._generate_euclidean_pattern)
        self.refresh()

    @staticmethod
    def _double_spin(
        minimum: float,
        maximum: float,
        value: float,
        decimals: int,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        spin.setSingleStep(0.01 if decimals >= 2 else 0.1)
        spin.setValue(value)
        return spin

    def _selected_definition(self) -> ModulatorDefinition | None:
        if not self._selected_id:
            return None
        return self.application.modulator_bank.get(self._selected_id)

    def refresh(self) -> None:
        selected_id = self._selected_id
        self._loading = True
        self.modulator_list.clear()
        for definition in self.application.modulator_bank.list_modulators():
            item = QListWidgetItem(f"{definition.name}   ·   {definition.kind.upper()}")
            item.setData(Qt.ItemDataRole.UserRole, definition.modulator_id)
            self.modulator_list.addItem(item)
            if definition.modulator_id == selected_id:
                self.modulator_list.setCurrentItem(item)
        if self.modulator_list.count() and self.modulator_list.currentItem() is None:
            self.modulator_list.setCurrentRow(0)
        self._selected_id = (
            str(self.modulator_list.currentItem().data(Qt.ItemDataRole.UserRole))
            if self.modulator_list.currentItem()
            else None
        )
        self._refresh_presets()
        self._loading = False
        self._load_selected_editor()
        self.refresh_assignment_targets()
        self.refresh_live()

    def _refresh_presets(self) -> None:
        current = self.preset_combo.currentData()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        for preset in self.application.modulator_bank.list_presets():
            tag = "BUILT-IN" if preset.builtin else "USER"
            self.preset_combo.addItem(f"{preset.name}   ·   {tag}", preset.preset_id)
        index = self.preset_combo.findData(current)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
        self.preset_combo.blockSignals(False)
        self._update_preset_actions()

    def _update_preset_actions(self, *_args) -> None:
        preset = self.application.modulator_bank.presets.get(
            str(self.preset_combo.currentData() or "")
        )
        self.delete_preset_button.setEnabled(bool(preset and not preset.builtin))

    def _sync_timebase_controls(self, *_args) -> None:
        definition = self._selected_definition()
        is_follower = definition is not None and definition.kind == "follower"
        transport_sync = self.sync_combo.currentData() == "transport"
        self.sync_combo.setEnabled(not is_follower)
        self.reset_combo.setEnabled(transport_sync and not is_follower)
        self.lfo_rate_beats.setEnabled(transport_sync and not is_follower)
        self.lfo_rate_hz.setEnabled(not transport_sync and not is_follower)
        self.division_spin.setEnabled(transport_sync and not is_follower)
        self.step_rate_spin.setEnabled(not transport_sync and not is_follower)

    def _load_selected_editor(self) -> None:
        definition = self._selected_definition()
        active = definition is not None
        for widget in (
            self.name_edit,
            self.enabled_check,
            self.sync_combo,
            self.reset_combo,
            self.lfo_group,
            self.follower_group,
            self.envelope_group,
            self.sequence_group,
            self.apply_button,
            self.duplicate_button,
            self.remove_button,
            self.save_preset_button,
            self.assignment_target_combo,
            self.assignment_depth,
            self.assignment_polarity_combo,
            self.assign_button,
        ):
            widget.setEnabled(active)
        if definition is None:
            self.name_edit.clear()
            set_ui_text(self.output_label, "OUTPUT · —")
            self.output_meter.setValue(0)
            self.lfo_group.hide()
            self.follower_group.hide()
            self.envelope_group.hide()
            self.sequence_group.hide()
            return

        self._loading = True
        self.name_edit.setText(definition.name)
        self.enabled_check.setChecked(definition.enabled)
        self.sync_combo.setCurrentIndex(
            max(0, self.sync_combo.findData(definition.sync_mode))
        )
        self.reset_combo.setCurrentIndex(
            max(0, self.reset_combo.findData(definition.reset_mode))
        )
        self.waveform_combo.setCurrentIndex(
            max(0, self.waveform_combo.findData(definition.waveform))
        )
        self.lfo_rate_beats.setValue(definition.rate_beats)
        self.lfo_rate_hz.setValue(definition.rate_hz)
        self.lfo_phase.setValue(definition.phase)
        self.lfo_pulse_width.setValue(definition.pulse_width)
        self.input_source_combo.setCurrentIndex(
            max(0, self.input_source_combo.findData(definition.input_source))
        )
        self.input_min_spin.setValue(definition.input_min)
        self.input_max_spin.setValue(definition.input_max)
        self.input_curve_combo.setCurrentIndex(
            max(0, self.input_curve_combo.findData(definition.input_curve))
        )
        self.input_invert_check.setChecked(definition.input_invert)
        self.input_attack_spin.setValue(definition.input_attack_ms)
        self.input_release_spin.setValue(definition.input_release_ms)
        self.trigger_combo.setCurrentIndex(
            max(0, self.trigger_combo.findData(definition.trigger_source))
        )
        self.retrigger_combo.setCurrentIndex(
            max(0, self.retrigger_combo.findData(definition.retrigger))
        )
        self.attack_spin.setValue(definition.attack)
        self.decay_spin.setValue(definition.decay)
        self.sustain_spin.setValue(definition.sustain)
        self.gate_spin.setValue(definition.gate)
        self.release_spin.setValue(definition.release)
        self.trigger_threshold_spin.setValue(definition.trigger_threshold)
        self.steps_edit.setText(
            ", ".join(f"{value:g}" for value in definition.step_values)
        )
        self.division_spin.setValue(definition.division_beats)
        self.step_rate_spin.setValue(definition.step_rate_hz)
        self.interpolation_combo.setCurrentIndex(
            max(0, self.interpolation_combo.findData(definition.interpolation))
        )
        self.direction_combo.setCurrentIndex(
            max(0, self.direction_combo.findData(definition.direction))
        )
        self.swing_spin.setValue(definition.swing)
        self.sequence_pulse_width.setValue(definition.pulse_width)
        self.seed_spin.setValue(definition.seed)
        self.euclidean_steps.setValue(len(definition.step_values))
        self.euclidean_pulses.setValue(
            min(
                self.euclidean_steps.value(),
                sum(1 for value in definition.step_values if value >= 0.5),
            )
        )
        self.euclidean_group.setVisible(definition.kind == "rhythm")
        self.lfo_group.setVisible(definition.kind == "lfo")
        self.follower_group.setVisible(definition.kind == "follower")
        self.envelope_group.setVisible(definition.kind == "envelope")
        self.sequence_group.setVisible(definition.kind in {"steps", "rhythm"})
        self._loading = False
        self._sync_timebase_controls()
        self.refresh_assignment_targets()

    def _generate_euclidean_pattern(self) -> None:
        pulses = min(
            self.euclidean_pulses.value(),
            self.euclidean_steps.value(),
        )
        pattern = euclidean_pattern(
            pulses,
            self.euclidean_steps.value(),
            self.euclidean_rotation.value(),
        )
        self.steps_edit.setText(", ".join(f"{value:g}" for value in pattern))

    def _selection_changed(self, current, _previous) -> None:
        if self._loading:
            return
        self._selected_id = (
            str(current.data(Qt.ItemDataRole.UserRole)) if current else None
        )
        self._load_selected_editor()
        self.refresh_live()

    def _create_modulator(self, kind: str) -> None:
        definition = ModulatorDefinition(kind=kind)
        if kind == "follower":
            definition.name = "Sonic Pi Macro Follower"
            definition.input_source = "macro.energy"
            definition.input_attack_ms = 80.0
            definition.input_release_ms = 600.0
        elif kind == "envelope":
            definition.name = "New Envelope"
            definition.trigger_source = "transport.beat_pulse"
            definition.attack = 0.02
            definition.decay = 0.2
            definition.sustain = 0.3
            definition.gate = 0.25
            definition.release = 0.4
        elif kind == "steps":
            definition.name = "New Step Sequence"
            definition.step_values = [0.0, 0.33, 0.66, 1.0]
            definition.division_beats = 0.5
        elif kind == "rhythm":
            definition.name = "New Rhythm Pattern"
            definition.step_values = [1.0, 0.0, 0.0, 0.0]
            definition.division_beats = 0.25
        else:
            definition.name = "New LFO"
        self._selected_id = self.application.add_modulator(definition)
        self.refresh()
        self.bank_changed.emit()

    def _duplicate_selected(self) -> None:
        definition = self._selected_definition()
        if definition is None:
            return
        self._selected_id = self.application.duplicate_modulator(
            definition.modulator_id
        )
        self.refresh()
        self.bank_changed.emit()

    def _remove_selected(self) -> None:
        definition = self._selected_definition()
        if definition is None:
            return
        answer = QMessageBox.question(
            self,
            ui_text("Remove modulator"),
            ui_text(f"Remove '{definition.name}' and its assignments from all layers?"),
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.application.remove_modulator(definition.modulator_id)
        self._selected_id = None
        self.refresh()
        self.bank_changed.emit()

    def _apply_editor(self) -> None:
        definition = self._selected_definition()
        if definition is None:
            return
        try:
            step_values = [
                float(token.strip())
                for token in self.steps_edit.text().replace(";", ",").split(",")
                if token.strip()
            ]
            values = definition.to_dict()
            values.update(
                {
                    "name": self.name_edit.text(),
                    "enabled": self.enabled_check.isChecked(),
                    "sync_mode": self.sync_combo.currentData(),
                    "reset_mode": self.reset_combo.currentData(),
                    "waveform": self.waveform_combo.currentData(),
                    "rate_beats": self.lfo_rate_beats.value(),
                    "rate_hz": self.lfo_rate_hz.value(),
                    "phase": self.lfo_phase.value(),
                    "pulse_width": (
                        self.sequence_pulse_width.value()
                        if definition.kind == "rhythm"
                        else self.lfo_pulse_width.value()
                    ),
                    "input_source": self.input_source_combo.currentData(),
                    "input_min": self.input_min_spin.value(),
                    "input_max": self.input_max_spin.value(),
                    "input_invert": self.input_invert_check.isChecked(),
                    "input_curve": self.input_curve_combo.currentData(),
                    "input_attack_ms": self.input_attack_spin.value(),
                    "input_release_ms": self.input_release_spin.value(),
                    "trigger_source": self.trigger_combo.currentData(),
                    "trigger_threshold": self.trigger_threshold_spin.value(),
                    "retrigger": self.retrigger_combo.currentData(),
                    "attack": self.attack_spin.value(),
                    "decay": self.decay_spin.value(),
                    "sustain": self.sustain_spin.value(),
                    "gate": self.gate_spin.value(),
                    "release": self.release_spin.value(),
                    "step_values": step_values or definition.step_values,
                    "division_beats": self.division_spin.value(),
                    "step_rate_hz": self.step_rate_spin.value(),
                    "interpolation": self.interpolation_combo.currentData(),
                    "direction": self.direction_combo.currentData(),
                    "swing": self.swing_spin.value(),
                    "seed": self.seed_spin.value(),
                }
            )
            updated = ModulatorDefinition.from_dict(values)
        except (TypeError, ValueError) as exc:
            QMessageBox.warning(self, ui_text("Modulator settings"), ui_text(str(exc)))
            return
        self.application.update_modulator(updated)
        self.refresh()
        self.bank_changed.emit()

    def _load_preset(self) -> None:
        preset_id = self.preset_combo.currentData()
        if not preset_id:
            return
        try:
            definition = self.application.modulator_bank.instantiate_preset(
                str(preset_id)
            )
        except (KeyError, TypeError, ValueError) as exc:
            QMessageBox.warning(self, ui_text("Modulator preset"), ui_text(str(exc)))
            return
        self._selected_id = definition.modulator_id
        self.application.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=definition.modulator_id,
        )
        self.refresh()
        self.bank_changed.emit()

    def _save_preset(self) -> None:
        definition = self._selected_definition()
        if definition is None:
            return
        name, accepted = QInputDialog.getText(
            self,
            "Save modulator preset",
            "Preset name:",
            text=definition.name,
        )
        if not accepted or not name.strip():
            return
        self.application.apply_modulator_preset(definition.modulator_id, name.strip())
        self.refresh()
        self.bank_changed.emit()

    def _delete_preset(self) -> None:
        preset_id = self.preset_combo.currentData()
        preset = self.application.modulator_bank.presets.get(str(preset_id or ""))
        if preset is None or preset.builtin:
            return
        answer = QMessageBox.question(
            self,
            ui_text("Delete preset"),
            ui_text(f"Delete user preset '{preset.name}'?"),
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.application.delete_modulator_preset(preset.preset_id)
        self._refresh_presets()
        self.bank_changed.emit()

    def _export_presets(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            ui_text("Export modulator presets"),
            "modulator-presets.json",
            "Modulator Presets (*.json)",
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            destination = self.application.export_modulator_presets(path)
        except OSError as exc:
            QMessageBox.warning(self, ui_text("Export presets"), ui_text(str(exc)))
            return
        self.setToolTip(f"Exported presets to {destination}")

    def _import_presets(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            ui_text("Import modulator presets"),
            "",
            "Modulator Presets (*.json)",
        )
        if not path:
            return
        try:
            imported = self.application.import_modulator_presets(path)
        except (OSError, TypeError, ValueError) as exc:
            QMessageBox.warning(self, ui_text("Import presets"), ui_text(str(exc)))
            return
        self.refresh()
        QMessageBox.information(
            self,
            ui_text("Import presets"),
            ui_text(f"Imported {imported} modulator preset(s)."),
        )
        self.bank_changed.emit()

    def _targets_for_layer(self, layer) -> list[str]:
        targets = [
            target_id
            for target_id, spec in PERF_MODIFIER_TARGETS.items()
            if spec.category == "layer"
        ]
        if layer.source_type == "generator":
            compatible = {
                "geometry": {
                    "generator.animation_speed",
                    "generator.animation_amount",
                    "generator.density",
                    "generator.rotation",
                },
                "text": {
                    "generator.font_size",
                    "generator.letter_spacing",
                },
                "waveform": {
                    "generator.animation_speed",
                    "generator.waveform_amplitude",
                    "generator.waveform_frequency",
                },
                "particles": {
                    "generator.density",
                    "generator.particle_speed",
                    "generator.particle_size",
                    "generator.particle_spread",
                    "generator.particle_trail",
                },
            }
            targets.extend(sorted(compatible.get(layer.generator_type, set())))
            if (
                layer.generator_type == "text"
                and layer.generator_settings.get("text_animation", "none") != "none"
            ):
                targets.extend(
                    (
                        "generator.text_animation_speed",
                        "generator.text_animation_amount",
                    )
                )
        elif layer.source_type == "overlay":
            player = self.application._overlay_images.get(layer.id)
            if player is not None and player.animated:
                targets.extend(
                    (
                        "overlay.playback_speed",
                        "overlay.frame_hold",
                    )
                )
        return targets

    def _default_target(self, layer) -> str:
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
            }.get(layer.generator_type, "layer.scale")
        if (
            layer.source_type == "overlay"
            and self.assignment_target_combo.findData("overlay.playback_speed") >= 0
        ):
            return "overlay.playback_speed"
        return "layer.scale"

    def refresh_assignment_targets(self) -> None:
        layer = self.application.composition.get_layer(
            self.application._selected_layer_id or ""
        )
        definition = self._selected_definition()
        current = self.assignment_target_combo.currentData()
        self.assignment_target_combo.blockSignals(True)
        self.assignment_target_combo.clear()
        if layer is not None:
            for target_id in self._targets_for_layer(layer):
                spec = PERF_MODIFIER_TARGETS[target_id]
                self.assignment_target_combo.addItem(spec.label, target_id)
        target = self.assignment_target_combo.findData(current)
        if target < 0 and layer is not None:
            target = self.assignment_target_combo.findData(self._default_target(layer))
        self.assignment_target_combo.setCurrentIndex(max(0, target))
        self.assignment_target_combo.blockSignals(False)
        if layer is None:
            set_ui_text(self.assignment_layer_label, "No layer selected")
        else:
            set_ui_text(
                self.assignment_layer_label,
                f"{layer.name} · {'LOCKED' if layer.locked else 'READY'}",
            )
        assignable = bool(
            layer
            and not layer.locked
            and definition
            and self.assignment_target_combo.count()
        )
        self.assign_button.setEnabled(assignable)
        self.assignment_target_combo.setEnabled(assignable)
        self.assignment_depth.setEnabled(assignable)
        self.assignment_polarity_combo.setEnabled(assignable)

    def _assign_selected(self) -> None:
        definition = self._selected_definition()
        layer = self.application.composition.get_layer(
            self.application._selected_layer_id or ""
        )
        target_id = self.assignment_target_combo.currentData()
        if definition is None or layer is None or layer.locked or not target_id:
            return
        polarity = self.assignment_polarity_combo.currentData()
        if polarity == "auto":
            polarity = (
                "positive" if definition.kind in {"envelope", "follower"} else "bipolar"
            )
        target_label = PERF_MODIFIER_TARGETS[str(target_id)].label
        modifier = LayerPerformanceModifier(
            name=f"{definition.name} → {target_label}",
            source_id=f"modulator.{definition.modulator_id}",
            target_id=str(target_id),
            depth=self.assignment_depth.value() / 100.0,
            polarity=str(polarity),
            curve="linear" if definition.kind == "steps" else "smoothstep",
        )
        try:
            self.application.add_layer_performance_modifier(layer.id, modifier)
        except (TypeError, ValueError, KeyError) as exc:
            QMessageBox.warning(
                self, ui_text("Modulator assignment"), ui_text(str(exc))
            )
            return
        self.assignment_created.emit(layer.id)

    def refresh_live(self) -> None:
        definition = self._selected_definition()
        if definition is None:
            set_ui_text(self.input_live_label, "INPUT · —")
            set_ui_text(self.output_label, "OUTPUT · —")
            self.output_meter.setValue(0)
            return
        if definition.kind == "follower":
            input_value = self.application._modulation_sources().get(
                definition.input_source
            )
            input_name = FOLLOWER_SOURCES.get(
                definition.input_source, definition.input_source
            )
            if input_value is None:
                set_ui_text(self.input_live_label, f"INPUT · {input_name} · NO SIGNAL")
            else:
                set_ui_text(
                    self.input_live_label,
                    f"INPUT · {input_name} · {float(input_value):.3f}",
                )
        elif definition.kind == "envelope":
            trigger_value = self.application._modulation_sources().get(
                definition.trigger_source
            )
            trigger_name = TRIGGER_SOURCES.get(
                definition.trigger_source, definition.trigger_source
            )
            if trigger_value is None:
                set_ui_text(
                    self.input_live_label, f"TRIGGER · {trigger_name} · NO SIGNAL"
                )
            else:
                set_ui_text(
                    self.input_live_label,
                    f"TRIGGER · {trigger_name} · {float(trigger_value):.3f} "
                    f"/ THR {definition.trigger_threshold:.2f}",
                )
        else:
            timebase = (
                "TRANSPORT CLOCK"
                if definition.sync_mode == "transport"
                else "FREE-RUN CLOCK"
            )
            set_ui_text(self.input_live_label, f"INPUT · {timebase}")
        live_values = self.application.modulator_bank_engine.live_values()
        source_id = f"modulator.{definition.modulator_id}"
        is_bypassed = not definition.enabled
        if source_id not in live_values:
            if definition.kind == "follower" and definition.enabled:
                set_ui_text(self.output_label, "OUTPUT · NO INPUT")
                self.output_meter.setValue(0)
                return
            value = 0.5 if definition.kind != "envelope" else 0.0
        else:
            value = live_values[source_id]
        status = "BYPASSED" if is_bypassed else definition.kind.upper()
        set_ui_text(self.output_label, f"OUTPUT · {value:.3f}  ·  {status}")
        self.output_meter.setValue(round(max(0.0, min(1.0, value)) * 100))
