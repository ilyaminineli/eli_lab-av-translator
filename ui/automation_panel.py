from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.automation import AutomationSettings
from media.library import MediaLibrary


class AutomationPanel(QWidget):
    start_requested = Signal(object, object, object)
    stop_requested = Signal()

    def __init__(self, library: MediaLibrary, parent=None) -> None:
        super().__init__(parent)
        self.library = library
        self._running = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(8, 8, 8, 8)
        form = QFormLayout()

        self.collection_combo = QComboBox()
        form.addRow("FOOTAGE POOL", self.collection_combo)

        self.duration_combo = QComboBox()
        for label, seconds in (
                ("30 minutes", 1800),
                ("45 minutes", 2700),
                ("1 hour", 3600),
                ("90 minutes", 5400),
                ("2 hours", 7200),
                ("Until stopped", None),
        ):
            self.duration_combo.addItem(label, seconds)
        self.duration_combo.setCurrentIndex(self.duration_combo.count() - 1)
        form.addRow("SESSION LENGTH", self.duration_combo)

        self.performance_style_combo = QComboBox()
        self.performance_style_combo.addItem("Unified · Chaotic / Generative / Structured", "generative")
        self.performance_style_combo.addItem("More exploratory", "random")
        self.performance_style_combo.addItem("More composed", "structured")
        self.performance_style_combo.setCurrentIndex(0)
        form.addRow("DIRECTOR CHARACTER", self.performance_style_combo)

        self.musical_sync_combo = QComboBox()
        self.musical_sync_combo.addItem("Time-based", "time")
        self.musical_sync_combo.addItem("Bar-synchronised", "bar")
        self.musical_sync_combo.addItem("Phrase-synchronised", "phrase")
        self.musical_sync_combo.addItem("Hybrid", "hybrid")
        self.musical_sync_combo.setCurrentIndex(2)
        form.addRow("MUSICAL SYNC", self.musical_sync_combo)

        self.cut_combo = QComboBox()
        self.cut_combo.addItem("Slow cuts · 18–38 sec", "slow")
        self.cut_combo.addItem("Balanced · 8–24 sec", "balanced")
        self.cut_combo.addItem("Fast cuts · 3–10 sec", "fast")
        self.cut_combo.setCurrentIndex(1)
        form.addRow("CUT RHYTHM", self.cut_combo)

        self.segment_combo = QComboBox()
        self.segment_combo.addItem("Short fragments · 2–6 sec", "short")
        self.segment_combo.addItem("Mixed fragments · 4–16 sec", "mixed")
        self.segment_combo.addItem("Long fragments · 12–30 sec", "long")
        self.segment_combo.setCurrentIndex(1)
        form.addRow("IN / OUT LENGTH", self.segment_combo)

        self.loop_combo = QComboBox()
        self.loop_combo.addItem("Occasional loops · 25%", 0.25)
        self.loop_combo.addItem("Mixed loops · 58%", 0.58)
        self.loop_combo.addItem("Frequent loops · 85%", 0.85)
        self.loop_combo.setCurrentIndex(1)
        form.addRow("SEGMENT LOOP CHANCE", self.loop_combo)

        layout.addLayout(form)
        self.layout_check = QCheckBox("Periodically change collage layout")
        self.layout_check.setChecked(True)
        self.effects_check = QCheckBox("Periodically change overlay / filter look")
        self.effects_check.setChecked(True)
        self.generator_check = QCheckBox("Periodically vary generators + text")
        self.generator_check.setChecked(True)
        self.layer_fx_check = QCheckBox("Vary enabled per-layer FX")
        self.layer_fx_check.setChecked(True)
        self.overlay_check = QCheckBox("Vary overlay transforms + blend")
        self.overlay_check.setChecked(True)
        self.palette_check = QCheckBox("Vary colours · Japanese palette looks")
        self.palette_check.setChecked(True)
        layout.addWidget(self.layout_check)
        layout.addWidget(self.effects_check)
        layout.addWidget(self.generator_check)
        layout.addWidget(self.layer_fx_check)
        layout.addWidget(self.overlay_check)
        layout.addWidget(self.palette_check)

        self.director_group = QGroupBox("UNIFIED MUSICAL / GENERATIVE DIRECTOR")
        director_form = QFormLayout(self.director_group)
        self.director_active_label = QLabel(
            "UNIFIED DIRECTOR ACTIVE · CHAOTIC / GENERATIVE / STRUCTURED"
        )
        self.director_active_label.setWordWrap(True)
        self.director_active_label.setObjectName("mutedLabel")
        self.variation_scope_label = QLabel(
            "Adaptive scope · the director can select every visible, unlocked layer. "
            "Musical energy and CHAOS / DENSITY / FRAGMENT expand or focus each variation."
        )
        self.variation_scope_label.setWordWrap(True)
        self.variation_scope_label.setObjectName("mutedLabel")
        self.keep_anchor_check = QCheckBox("Prefer a recognizable visual anchor")
        self.keep_anchor_check.setChecked(False)
        self.preserve_background_check = QCheckBox(
            "Protect background source from clip switching"
        )
        self.preserve_background_check.setChecked(False)
        self.effect_after_transition_check = QCheckBox(
            "Introduce master / layer FX only after a transition"
        )
        self.effect_after_transition_check.setChecked(True)
        self.palette_memory_spin = QSpinBox()
        self.palette_memory_spin.setRange(0, 16)
        self.palette_memory_spin.setValue(4)
        self.peak_particle_boost_spin = QDoubleSpinBox()
        self.peak_particle_boost_spin.setRange(0.0, 1.0)
        self.peak_particle_boost_spin.setDecimals(2)
        self.peak_particle_boost_spin.setSingleStep(0.05)
        self.peak_particle_boost_spin.setValue(0.35)
        self.slow_breakdown_check = QCheckBox(
            "Use slower layout transitions during breakdowns"
        )
        self.slow_breakdown_check.setChecked(True)
        self.breakdown_min_spin = QDoubleSpinBox()
        self.breakdown_min_spin.setRange(2.0, 20.0)
        self.breakdown_min_spin.setSingleStep(0.5)
        self.breakdown_min_spin.setDecimals(1)
        self.breakdown_min_spin.setSuffix(" s")
        self.breakdown_min_spin.setValue(5.0)
        self.breakdown_max_spin = QDoubleSpinBox()
        self.breakdown_max_spin.setRange(2.0, 30.0)
        self.breakdown_max_spin.setSingleStep(0.5)
        self.breakdown_max_spin.setDecimals(1)
        self.breakdown_max_spin.setSuffix(" s")
        self.breakdown_max_spin.setValue(9.0)
        director_form.addRow(self.director_active_label)
        director_form.addRow("VARIATION SCOPE", self.variation_scope_label)
        director_form.addRow(self.keep_anchor_check)
        director_form.addRow(self.preserve_background_check)
        director_form.addRow(self.effect_after_transition_check)
        director_form.addRow("PALETTE MEMORY · PHRASES", self.palette_memory_spin)
        director_form.addRow("PEAK PARTICLE BOOST · 0–1", self.peak_particle_boost_spin)
        director_form.addRow(self.slow_breakdown_check)
        director_form.addRow("BREAKDOWN TRANSITION MIN", self.breakdown_min_spin)
        director_form.addRow("BREAKDOWN TRANSITION MAX", self.breakdown_max_spin)
        layout.addWidget(self.director_group)

        reactive_hint = QLabel(
            "Performance Mode installs shared audio/Sonic Pi routes and per-layer curves "
            "automatically. Run SONATA after arming; phrase/scene events drive AUTO "
            "PERFORMANCE while energy, cutoff and optional loopback audio drive the visuals."
        )
        reactive_hint.setWordWrap(True)
        reactive_hint.setObjectName("mutedLabel")
        layout.addWidget(reactive_hint)

        self.start_button = QPushButton("START AUTOMATIC SESSION")
        self.stop_button = QPushButton("STOP AUTOMATION")
        self.stop_button.setEnabled(False)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.status_label = QLabel("Ready · import a footage folder to begin.")
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("mutedLabel")
        layout.addWidget(self.status_label)
        layout.addStretch(1)
        self.scroll.setWidget(body)
        outer.addWidget(self.scroll, 1)

        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self.stop_requested)
        self.refresh_collections()

    def refresh_collections(self) -> None:
        selected = self.collection_combo.currentData()
        self.collection_combo.blockSignals(True)
        self.collection_combo.clear()
        assets = self.library.list_assets()
        playable = [
            asset for asset in assets
            if asset.status not in {"error", "unsupported"} and Path(asset.path).is_file()
        ]
        self.collection_combo.addItem(
            f"All playable footage · {len(playable)} clip(s)",
            None,
        )
        groups: dict[str, list[str]] = {}
        for asset in playable:
            groups.setdefault(asset.collection_id, []).append(asset.path)
        for collection_id, paths in sorted(groups.items()):
            folder_name = Path(paths[0]).parent.name or "Video folder"
            self.collection_combo.addItem(
                f"{folder_name} · {len(paths)} playable",
                collection_id,
            )
        index = self.collection_combo.findData(selected)
        self.collection_combo.setCurrentIndex(index if index >= 0 else 0)
        self.collection_combo.blockSignals(False)
        self.start_button.setEnabled(bool(playable) and not self._running)
        if not playable and not self._running:
            self.status_label.setText(
                "No playable video files. Import a video folder or choose a pool "
                "with readable clips."
            )
        elif playable and self.status_label.text().startswith("No playable video files"):
            self.status_label.setText(f"Ready · {len(playable)} playable video clip(s) available.")

    def _build_settings(self) -> AutomationSettings:
        cut_ranges = {
            "slow": (18.0, 38.0),
            "balanced": (8.0, 24.0),
            "fast": (3.0, 10.0),
        }
        segment_ranges = {
            "short": (2.0, 6.0),
            "mixed": (4.0, 16.0),
            "long": (12.0, 30.0),
        }
        cut_min, cut_max = cut_ranges[self.cut_combo.currentData()]
        segment_min, segment_max = segment_ranges[self.segment_combo.currentData()]
        return AutomationSettings(
            min_segment_seconds=segment_min,
            max_segment_seconds=segment_max,
            min_cut_interval=cut_min,
            max_cut_interval=cut_max,
            loop_probability=float(self.loop_combo.currentData()),
            clip_switch_probability=0.42,
            randomize_layout=self.layout_check.isChecked(),
            randomize_effects=self.effects_check.isChecked(),
            min_layout_interval=max(8.0, cut_min * 1.25),
            max_layout_interval=max(16.0, cut_max * 1.8),
            min_effect_interval=max(7.0, cut_min * 1.1),
            max_effect_interval=max(14.0, cut_max * 1.5),
            randomize_generators=self.generator_check.isChecked(),
            randomize_text=self.generator_check.isChecked(),
            randomize_layer_effects=self.layer_fx_check.isChecked(),
            randomize_overlays=self.overlay_check.isChecked(),
            randomize_palette=self.palette_check.isChecked(),
            min_generator_interval=max(12.0, cut_min * 1.5),
            max_generator_interval=max(24.0, cut_max * 2.0),
            performance_style=str(self.performance_style_combo.currentData()),
            musical_sync=str(self.musical_sync_combo.currentData()),
            constrained_generative=True,
            max_layers_per_variation=0,
            keep_visual_anchor=self.keep_anchor_check.isChecked(),
            preserve_background_source=self.preserve_background_check.isChecked(),
            effect_after_transition=self.effect_after_transition_check.isChecked(),
            palette_memory_phrases=self.palette_memory_spin.value(),
            peak_particle_boost=self.peak_particle_boost_spin.value(),
            slow_breakdown_transitions=self.slow_breakdown_check.isChecked(),
            breakdown_transition_min_seconds=self.breakdown_min_spin.value(),
            breakdown_transition_max_seconds=self.breakdown_max_spin.value(),
        )

    def sync_performance_plan(self, plan) -> None:
        settings = getattr(plan, "automation_settings", {}) or {}
        for combo, key, fallback in (
                (self.performance_style_combo, "performance_style", "generative"),
                (self.musical_sync_combo, "musical_sync", "phrase"),
        ):
            index = combo.findData(settings.get(key, fallback))
            if index >= 0:
                combo.setCurrentIndex(index)
        duration_index = self.duration_combo.findData(
            getattr(plan, "automation_duration_seconds", None)
        )
        if duration_index >= 0:
            self.duration_combo.setCurrentIndex(duration_index)
        for control, key in (
                (self.layout_check, "randomize_layout"),
                (self.effects_check, "randomize_effects"),
                (self.generator_check, "randomize_generators"),
                (self.layer_fx_check, "randomize_layer_effects"),
                (self.overlay_check, "randomize_overlays"),
                (self.palette_check, "randomize_palette"),
                (self.keep_anchor_check, "keep_visual_anchor"),
                (self.preserve_background_check, "preserve_background_source"),
                (self.effect_after_transition_check, "effect_after_transition"),
                (self.slow_breakdown_check, "slow_breakdown_transitions"),
        ):
            if key in settings:
                control.setChecked(bool(settings[key]))
        for control, key in (
                (self.palette_memory_spin, "palette_memory_phrases"),
                (self.peak_particle_boost_spin, "peak_particle_boost"),
                (self.breakdown_min_spin, "breakdown_transition_min_seconds"),
                (self.breakdown_max_spin, "breakdown_transition_max_seconds"),
        ):
            if key in settings:
                control.setValue(settings[key])

    def _start(self) -> None:
        self.start_requested.emit(
            self.collection_combo.currentData(),
            self.duration_combo.currentData(),
            self._build_settings(),
        )

    def set_running(self, running: bool, message: str | None = None) -> None:
        self._running = bool(running)
        playable = any(
            asset.status not in {"error", "unsupported"} and Path(asset.path).is_file()
            for asset in self.library.list_assets(
                collection_id=self.collection_combo.currentData()
            )
        )
        self.start_button.setEnabled(not running and playable)
        self.stop_button.setEnabled(running)
        if message:
            self.status_label.setText(message)

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)
