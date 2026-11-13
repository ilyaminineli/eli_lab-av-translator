from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from core.performance_timeline import (
    TIMELINE_EVENT_LABELS,
    TIMELINE_EVENT_TYPES,
    PerformanceTimelineEvent,
)


_PAYLOAD_TEMPLATES = {
    "scene_marker": "{}",
    "phrase_marker": "{}",
    "scene_recall": '{"scene_id": "scene-id", "morph_seconds": 0.0}',
    "clip_trigger": '{"deck_id": "deck_a", "action": "play"}',
    "effect_change": '{"preset_name": "Digital Damage", "settings": {"feedback_enabled": true}}',
    "text_regenerate": '{"layer_id": "optional-text-layer-id", "seed": 20261113}',
    "palette_change": '{"palette": "Fuji · 藤"}',
    "modulation": '{"macro_id": "chaos", "value": 0.8, "duration_bars": 4}',
    "transition_cue": '{"scene_id": "scene-id", "morph_seconds": 4.0}',
}

_PAYLOAD_HINTS = {
    "scene_marker": "A named section marker. It records INTRO / PEAK / BREAKDOWN etc. and does not recall a scene by itself.",
    "phrase_marker": "A descriptive musical phrase marker. Use the same bar/beat grid as the transport.",
    "scene_recall": "Recall a saved VJ Scene Bank scene. Use morph_seconds 0 for an immediate cut.",
    "clip_trigger": "Trigger a loaded deck, or include asset_id to load a media-library asset. Actions: load, play, pause, hold, release, restart, stop, seek.",
    "effect_change": "Apply a master look preset and/or override selected EffectSettings fields. Preset names come from the EFFECTS dock.",
    "text_regenerate": "Regenerate a Text Art layer using its saved language/theme/dictionary settings. Omit layer_id to use the first unlocked Text Art layer.",
    "palette_change": "Apply a named palette to unlocked generator layers. Choose a palette from the current palette library.",
    "modulation": "Set a normalized Performance Macro (0–1). The manual value takes priority for duration_bars, then its assigned live source resumes.",
    "transition_cue": "Recall a saved VJ Scene with a numeric morph. Discrete media/text changes retain the scene bank's cut policy.",
}


class PerformanceTimelinePanel(QWidget):
    """Musical show timeline editor and transport-following playback surface."""

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self._loading = False
        self._definition_revision = -1

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("BAR / BEAT SHOW PLAN")
        title.setObjectName("sectionHeading")
        header.addWidget(title)
        header.addStretch(1)
        self.arm_button = QPushButton("ARM TIMELINE")
        self.arm_button.clicked.connect(self._toggle_arm)
        header.addWidget(self.arm_button)
        self.rewind_button = QPushButton("REWIND")
        self.rewind_button.clicked.connect(self._rewind)
        header.addWidget(self.rewind_button)
        root.addLayout(header)

        self.state_label = QLabel("IDLE · add events, arm the timeline, then start the transport.")
        self.state_label.setWordWrap(True)
        self.state_label.setObjectName("mutedLabel")
        root.addWidget(self.state_label)

        self.event_list = QListWidget()
        self.event_list.setMinimumHeight(150)
        self.event_list.setMaximumHeight(260)
        self.event_list.currentItemChanged.connect(self._event_selected)
        self.event_list.itemChanged.connect(self._event_enabled_changed)
        root.addWidget(self.event_list)

        self.editor_group = QGroupBox("TIMELINE EVENT")
        form = QFormLayout(self.editor_group)
        self.bar_spin = QSpinBox()
        self.bar_spin.setRange(1, 1_000_000)
        self.bar_spin.setValue(1)
        self.beat_spin = QSpinBox()
        self.beat_spin.setRange(1, 16)
        self.beat_spin.setValue(1)
        position_row = QHBoxLayout()
        position_row.addWidget(QLabel("BAR"))
        position_row.addWidget(self.bar_spin, 1)
        position_row.addWidget(QLabel("BEAT"))
        position_row.addWidget(self.beat_spin, 1)
        form.addRow("POSITION", position_row)

        self.type_combo = QComboBox()
        for event_type in TIMELINE_EVENT_TYPES:
            self.type_combo.addItem(
                TIMELINE_EVENT_LABELS[event_type],
                event_type,
            )
        form.addRow("EVENT TYPE", self.type_combo)

        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("INTRO / TEXT APPEARS / FIRST PEAK …")
        form.addRow("LABEL", self.label_edit)

        self.payload_hint = QLabel(_PAYLOAD_HINTS["phrase_marker"])
        self.payload_hint.setWordWrap(True)
        self.payload_hint.setObjectName("mutedLabel")
        form.addRow("ACTION", self.payload_hint)

        self.payload_edit = QPlainTextEdit()
        self.payload_edit.setMaximumHeight(100)
        self.payload_edit.setPlaceholderText("{}")
        form.addRow("PAYLOAD · JSON", self.payload_edit)

        self.event_enabled = QCheckBox("Event enabled")
        self.event_enabled.setChecked(True)
        form.addRow(self.event_enabled)
        root.addWidget(self.editor_group)

        buttons = QHBoxLayout()
        self.add_button = QPushButton("ADD EVENT")
        self.update_button = QPushButton("UPDATE SELECTED")
        self.remove_button = QPushButton("REMOVE")
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.update_button)
        buttons.addWidget(self.remove_button)
        root.addLayout(buttons)

        structure_row = QHBoxLayout()
        self.structure_button = QPushButton("INSERT EXAMPLE STRUCTURE")
        self.clear_button = QPushButton("CLEAR EVENTS")
        structure_row.addWidget(self.structure_button, 1)
        structure_row.addWidget(self.clear_button)
        root.addLayout(structure_row)
        root.addStretch(1)

        self.type_combo.currentIndexChanged.connect(self._type_changed)
        self.add_button.clicked.connect(self._add_event)
        self.update_button.clicked.connect(self._update_event)
        self.remove_button.clicked.connect(self._remove_event)
        self.structure_button.clicked.connect(self._insert_example_structure)
        self.clear_button.clicked.connect(self._clear_events)

        self._type_changed()
        self.refresh(force=True)

    def refresh(self, force: bool = False) -> None:
        timeline = self.application.performance_timeline
        snapshot = timeline.snapshot()
        if force or snapshot["definition_revision"] != self._definition_revision:
            selected = self.event_list.currentItem()
            selected_id = selected.data(Qt.ItemDataRole.UserRole) if selected else None
            self._populate_events(selected_id)
            self._definition_revision = int(snapshot["definition_revision"])

        control = self.application.performance_control
        internal_running = (
            self.application.transport.running
            and not self.application.transport.paused
        )
        external_running = (
            control.source_id == "sonic_pi"
            and control.transport_running
            and not control.transport_paused
        )
        if snapshot["armed"]:
            if internal_running or external_running:
                transport = "SONIC PI" if external_running else "INTERNAL"
                position = (
                    f"BAR {int(snapshot['current_bar']):03d} · "
                    f"BEAT {int(snapshot['current_beat']):02d}"
                )
                status = f"ARMED · {transport} · {position}"
            else:
                status = "ARMED · WAITING FOR TRANSPORT"
        else:
            status = (
                f"DISARMED · BAR {int(snapshot['current_bar']):03d} · "
                f"BEAT {int(snapshot['current_beat']):02d}"
            )
        if snapshot["current_marker"]:
            status += f" · {snapshot['current_marker']}"
        if snapshot["last_event_result"]:
            status += f"\n{snapshot['last_event_result']}"
        if snapshot["last_error"]:
            status += f"\nLAST ERROR · {snapshot['last_error']}"
        self.state_label.setText(status)
        self.arm_button.setText("DISARM TIMELINE" if snapshot["armed"] else "ARM TIMELINE")
        self.update_button.setEnabled(self.event_list.currentItem() is not None)
        self.remove_button.setEnabled(self.event_list.currentItem() is not None)

    def _populate_events(self, selected_id: str | None = None) -> None:
        self._loading = True
        self.event_list.blockSignals(True)
        self.event_list.clear()
        for event in self.application.performance_timeline.list_events():
            marker = "●" if event.event_type in {"scene_marker", "phrase_marker"} else "◆"
            label = event.label or TIMELINE_EVENT_LABELS[event.event_type]
            item = QListWidgetItem(
                f"{marker}  BAR {event.bar:03d} · BEAT {event.beat:02d}   "
                f"{TIMELINE_EVENT_LABELS[event.event_type].upper()}   {label}"
            )
            item.setData(Qt.ItemDataRole.UserRole, event.event_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if event.enabled else Qt.CheckState.Unchecked
            )
            self.event_list.addItem(item)
            if event.event_id == selected_id:
                self.event_list.setCurrentItem(item)
        self.event_list.blockSignals(False)
        self._loading = False
        if self.event_list.currentItem() is None:
            self._clear_editor()
        self.update_button.setEnabled(self.event_list.currentItem() is not None)
        self.remove_button.setEnabled(self.event_list.currentItem() is not None)

    def _selected_event(self) -> PerformanceTimelineEvent | None:
        item = self.event_list.currentItem()
        if item is None:
            return None
        event_id = str(item.data(Qt.ItemDataRole.UserRole))
        return next(
            (
                event for event in self.application.performance_timeline.list_events()
                if event.event_id == event_id
            ),
            None,
        )

    def _event_selected(self, current: QListWidgetItem | None, _previous) -> None:
        event = self._selected_event()
        if event is None:
            self.update_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            return
        self._loading = True
        self.bar_spin.setValue(event.bar)
        self.beat_spin.setValue(event.beat)
        self.type_combo.setCurrentIndex(
            max(0, self.type_combo.findData(event.event_type))
        )
        self.label_edit.setText(event.label)
        self.payload_edit.setPlainText(
            json.dumps(event.payload, ensure_ascii=False, indent=2)
        )
        self.event_enabled.setChecked(event.enabled)
        self._type_changed()
        self._loading = False
        self.update_button.setEnabled(True)
        self.remove_button.setEnabled(True)

    def _clear_editor(self) -> None:
        self._loading = True
        self.bar_spin.setValue(1)
        self.beat_spin.setValue(1)
        self.label_edit.clear()
        self.event_enabled.setChecked(True)
        self.payload_edit.setPlainText(
            _PAYLOAD_TEMPLATES.get(
                str(self.type_combo.currentData()),
                "{}",
            )
        )
        self._loading = False
        self._type_changed()

    def _type_changed(self, *_args) -> None:
        event_type = str(self.type_combo.currentData() or "phrase_marker")
        self.payload_hint.setText(_PAYLOAD_HINTS.get(event_type, "JSON event payload."))
        if not self._loading and not self.payload_edit.toPlainText().strip():
            self.payload_edit.setPlainText(_PAYLOAD_TEMPLATES.get(event_type, "{}"))

    def _read_editor(self) -> dict[str, object]:
        raw_payload = self.payload_edit.toPlainText().strip() or "{}"
        payload = json.loads(raw_payload)
        if not isinstance(payload, dict):
            raise ValueError("Event payload must be a JSON object.")
        event_type = str(self.type_combo.currentData())
        return {
            "bar": self.bar_spin.value(),
            "beat": self.beat_spin.value(),
            "event_type": event_type,
            "label": self.label_edit.text().strip(),
            "payload": payload,
            "enabled": self.event_enabled.isChecked(),
        }

    def _add_event(self) -> None:
        try:
            event = PerformanceTimelineEvent(**self._read_editor())
            event_id = self.application.add_performance_timeline_event(event)
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
            self.state_label.setText(f"EVENT NOT ADDED · {exc}")
            return
        self._populate_events(event_id)
        self.refresh(force=True)
        self.state_label.setText(f"ADDED · BAR {event.bar:03d} · {event.label}")

    def _update_event(self) -> None:
        event = self._selected_event()
        if event is None:
            return
        try:
            values = self._read_editor()
            self.application.update_performance_timeline_event(event.event_id, values)
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
            self.state_label.setText(f"EVENT NOT UPDATED · {exc}")
            return
        self.refresh(force=True)
        self.state_label.setText(f"UPDATED · BAR {self.bar_spin.value():03d}")

    def _remove_event(self) -> None:
        event = self._selected_event()
        if event is None:
            return
        self.application.remove_performance_timeline_event(event.event_id)
        self.refresh(force=True)

    def _event_enabled_changed(self, item: QListWidgetItem) -> None:
        if self._loading:
            return
        event_id = str(item.data(Qt.ItemDataRole.UserRole))
        try:
            self.application.update_performance_timeline_event(
                event_id,
                {"enabled": item.checkState() == Qt.CheckState.Checked},
            )
        except (KeyError, TypeError, ValueError) as exc:
            self.state_label.setText(f"COULD NOT UPDATE EVENT · {exc}")
        self.refresh()

    def _toggle_arm(self) -> None:
        if self.application.performance_timeline.armed:
            self.application.disarm_performance_timeline()
        else:
            self.application.arm_performance_timeline()
        self.refresh(force=True)

    def _rewind(self) -> None:
        self.application.reset_performance_timeline_playback()
        self.refresh(force=True)

    def _insert_example_structure(self) -> None:
        structure = (
            (1, "scene_marker", "INTRO"),
            (17, "phrase_marker", "TEXT APPEARS"),
            (33, "phrase_marker", "VIDEO CUT"),
            (49, "phrase_marker", "FEEDBACK ACTIVATED"),
            (65, "scene_marker", "FIRST PEAK"),
            (81, "phrase_marker", "BREAKDOWN"),
            (97, "phrase_marker", "PARTICLE TRANSFORMATION"),
            (113, "scene_marker", "FINAL RECAPITULATION"),
        )
        try:
            for bar, event_type, label in structure:
                self.application.add_performance_timeline_event({
                    "bar": bar,
                    "beat": 1,
                    "event_type": event_type,
                    "label": label,
                    "payload": {},
                    "enabled": True,
                })
        except (TypeError, ValueError, KeyError) as exc:
            self.state_label.setText(f"STRUCTURE NOT INSERTED · {exc}")
            return
        self.refresh(force=True)
        self.state_label.setText("INSERTED · 8 structure markers · add action events on the same bars")

    def _clear_events(self) -> None:
        if not self.application.performance_timeline.list_events():
            return
        answer = QMessageBox.question(
            self,
            "Clear performance timeline",
            "Remove every event from this timeline?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.application.performance_timeline.clear_events()
        self.refresh(force=True)
