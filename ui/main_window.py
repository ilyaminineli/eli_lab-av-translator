from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from config import (
    APP_AUTHOR,
    APP_COPYRIGHT,
    APP_NAME,
    APP_REPOSITORY_URL,
    APP_STUDIO,
    APP_VERSION,
)
from core.application import Application
from core.performance_service import PerformanceModePlan
from ui.asset_library_panel import AssetLibraryPanel
from ui.automation_panel import AutomationPanel
from ui.deck_panel import DeckPanel
from ui.effects_panel import EffectsPanel
from ui.generators_panel import GeneratorsPanel
from ui.layer_panel import LayerPanel
from ui.media_browser import MediaBrowser
from ui.modulator_bank_panel import ModulatorBankPanel
from ui.output_window import OutputWindowManager
from ui.performance_control_panel import PerformanceControlPanel
from ui.performance_timeline_panel import PerformanceTimelinePanel
from ui.performance_view import AspectRatioPreview, PerformanceView
from ui.transport_bar import TransportBar

_LOG = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, application: Application) -> None:
        super().__init__()
        self.application = application
        self.output_manager = OutputWindowManager(application, self)
        self.setWindowTitle(f"eli_lab AV Translator {APP_VERSION}")
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        if available is not None:
            initial_width = min(1600, max(720, round(available.width() * 0.95)))
            initial_height = min(980, max(480, round(available.height() * 0.92)))
            self.resize(initial_width, initial_height)
            minimum_width = min(860, max(720, available.width() - 32))
            minimum_height = min(600, max(480, available.height() - 32))
            self.setMinimumSize(minimum_width, minimum_height)
        else:
            self.resize(1600, 980)
            self.setMinimumSize(860, 600)
        # Leave enough room for a compact 4:3 workspace on older projectors.
        self._responsive_layout_managed = False
        self._responsive_layout_ready = False
        self._responsive_compact: bool | None = None
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.AllowNestedDocks
        )
        self._ui_settings = QSettings()
        self._restore_local_preview_on_close = False

        self.performance_view = PerformanceView(application, self)

        self.media_browser = MediaBrowser(application.media_library, self)
        self.media_dock = self._make_dock("MEDIA LIBRARY", self.media_browser)
        self.media_dock.setMinimumWidth(240)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.media_dock)

        self.asset_library_panel = AssetLibraryPanel(application, self)
        self.asset_library_dock = self._make_dock("VISUAL ASSET LIBRARY", self.asset_library_panel)
        self.asset_library_dock.setMinimumWidth(240)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.asset_library_dock)
        self.tabifyDockWidget(self.media_dock, self.asset_library_dock)

        self.deck_panel = DeckPanel(application, self)
        self.deck_dock = self._make_dock("VIDEO DECKS", self.deck_panel)
        self.deck_dock.setMinimumHeight(150)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.deck_dock)

        self.layer_panel = LayerPanel(application, self)
        self.layer_dock = self._make_dock("LAYERS", self.layer_panel)
        self.layer_dock.setMinimumWidth(280)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)

        self.effects_panel = EffectsPanel(
            application.effects,
            source_provider=lambda: application.composition.layers,
            parent=self,
        )
        self.effects_dock = self._make_dock("EFFECTS + OVERLAYS", self.effects_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.effects_dock)
        self.tabifyDockWidget(self.layer_dock, self.effects_dock)

        self.automation_panel = AutomationPanel(application.media_library, self)
        self.automation_dock = self._make_dock("AUTO PERFORMANCE", self.automation_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.automation_dock)
        self.tabifyDockWidget(self.effects_dock, self.automation_dock)

        self.generators_panel = GeneratorsPanel(application, self)
        self.preview_dock = self._make_dock("LOCAL PREVIEW", self.performance_view)
        self.preview_dock.setMinimumSize(260, 180)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.preview_dock)
        self.tabifyDockWidget(self.automation_dock, self.preview_dock)

        self.performance_control_panel = PerformanceControlPanel(application, self)
        self._performance_macro_shortcuts: list[QShortcut] = []
        self.performance_control_panel.macros_changed.connect(
            self._sync_performance_macro_shortcuts
        )
        self.performance_control_dock = self._make_dock(
            "AUDIO / CONTROL",
            self.performance_control_panel,
        )
        self.performance_control_dock.setMinimumWidth(300)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.performance_control_dock)
        self.tabifyDockWidget(self.preview_dock, self.performance_control_dock)

        self.modulator_bank_panel = ModulatorBankPanel(application, self)
        self.modulator_bank_dock = self._make_dock(
            "MODULATOR BANK",
            self.modulator_bank_panel,
        )
        self.modulator_bank_dock.setMinimumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.modulator_bank_dock)
        self.tabifyDockWidget(self.performance_control_dock, self.modulator_bank_dock)

        self.performance_timeline_panel = PerformanceTimelinePanel(application, self)
        self.performance_timeline_dock = self._make_dock(
            "LIVE PERFORMANCE TIMELINE",
            self.performance_timeline_panel,
        )
        self.performance_timeline_dock.setMinimumWidth(320)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.performance_timeline_dock,
        )
        self.tabifyDockWidget(self.modulator_bank_dock, self.performance_timeline_dock)
        self.layer_dock.raise_()
        self.setCentralWidget(self._build_workspace())

        self.transport_bar = TransportBar(self)
        toolbar = QToolBar("Performance")
        toolbar.setObjectName("performance_toolbar")
        toolbar.setMovable(False)
        toolbar.addWidget(self.transport_bar)
        self.performance_mode_button = QPushButton("▶ PERFORMANCE MODE")
        self.performance_mode_button.setCheckable(True)
        self.performance_mode_button.setToolTip(
            "Arm Sonic Pi OSC, system-loopback audio, AUTO PERFORMANCE and "
            "the saved modulation curves. Then run SONATA Expanded in Sonic Pi."
        )
        self.performance_mode_button.toggled.connect(self._toggle_performance_mode)
        toolbar.addWidget(self.performance_mode_button)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.control_status_label = QLabel(
            self.application.performance_control.status_text()
        )
        self._last_control_revision = self.application.performance_control.revision
        self._last_timeline_state_revision = int(
            self.application.performance_timeline.snapshot()["state_revision"]
        )
        self.control_status_label.setToolTip(
            "M3 control state · normalized transport, scene and macro events"
        )
        self.statusBar().addPermanentWidget(self.control_status_label)
        self.status_label = QLabel(
            "LOCAL PREVIEW IDLE · select PERFORM to initialise OpenGL"
        )
        self.statusBar().addPermanentWidget(self.status_label)
        self.performance_view.render_status_changed.connect(self.status_label.setText)

        self.media_browser.assign_requested.connect(self.assign_media)
        self.media_browser.library_updated.connect(self.automation_panel.refresh_collections)
        self.media_browser.library_updated.connect(self.refresh_automation_media_pool)
        self.deck_panel.action_requested.connect(self.deck_action)
        self.deck_panel.loop_changed.connect(self.set_deck_loop)
        self.transport_bar.random_set_requested.connect(self.randomize_decks)
        self.transport_bar.random_layout_requested.connect(self.randomize_layout)
        self.transport_bar.lock_all_requested.connect(self.lock_all)
        self.automation_panel.start_requested.connect(self.start_automation)
        self.automation_panel.stop_requested.connect(self.stop_automation)
        self.generators_panel.composition_changed.connect(self.layer_panel.refresh)
        self.layer_panel.layers_changed.connect(self.generators_panel.refresh)
        self.generators_panel.selected_layer_changed.connect(self.layer_panel.select_layer)
        self.layer_panel.selected_layer_changed.connect(self.generators_panel.select_layer)
        self.generators_panel.selected_layer_changed.connect(self.application.set_selected_layer_id)
        self.layer_panel.selected_layer_changed.connect(self.application.set_selected_layer_id)
        self.layer_panel.selected_layer_changed.connect(
            self.modulator_bank_panel.refresh_assignment_targets
        )
        self.modulator_bank_panel.bank_changed.connect(
            self.layer_panel.sync_performance_modifier_sources
        )
        self.modulator_bank_panel.bank_changed.connect(
            self.layer_panel.refresh_performance_modifiers
        )
        self.modulator_bank_panel.bank_changed.connect(
            self.performance_control_panel.sync_modulator_sources
        )
        self.modulator_bank_panel.bank_changed.connect(
            self.performance_control_panel.refresh_routes
        )
        self.modulator_bank_panel.assignment_created.connect(
            self.layer_panel.refresh_performance_modifiers
        )
        self.generators_panel.layer_properties_changed.connect(self.layer_panel.sync_layer_row)
        self.layer_panel.layer_properties_changed.connect(
            self.generators_panel.sync_layer_appearance
        )
        self.layer_panel.layer_properties_changed.connect(
            self.application.notify_layer_manual_override
        )
        self.generators_panel.manual_target_changed.connect(
            self.application.notify_manual_override
        )
        self.effects_panel.manual_parameter_changed.connect(
            self.application.notify_manual_override
        )
        self.asset_library_panel.composition_changed.connect(self.layer_panel.refresh)
        self.asset_library_panel.composition_changed.connect(self.generators_panel.refresh)

        self._create_actions()
        self._sync_performance_macro_shortcuts()
        # Keep a pristine Qt dock-state snapshot for the View → Restore Default Layout action.
        self._default_dock_state = self.saveState(4)
        saved_geometry = self._ui_settings.value("ui/main_window_geometry_v2")
        saved_state = self._ui_settings.value("ui/main_window_state_v5")
        restored = False
        if saved_geometry and saved_state:
            restored = (
                    self.restoreGeometry(saved_geometry)
                    and self.restoreState(saved_state, 4)
            )
        self._responsive_layout_managed = not restored
        self._responsive_layout_ready = True
        self._sync_responsive_dock_constraints()
        # Saved pre-M7 dock states may contain the old preview/media tabs.
        # Those widgets now live in central workspaces and their placeholder docks
        # must remain hidden after a legacy state restore.
        self.media_dock.hide()
        self.asset_library_dock.hide()
        self.preview_dock.hide()
        if not restored:
            QTimer.singleShot(0, self._apply_default_dock_sizes)

        self._runtime_timer = QTimer(self)
        # Refresh queues and automation at the configured render cadence.
        self._runtime_timer.setInterval(33)
        self._runtime_timer.timeout.connect(self._runtime_tick)
        self._runtime_timer.start()

        # Deck meters are presentation-only and need not follow the 30 FPS
        # renderer cadence. Keep their progress/status updates lightweight.
        self._deck_status_timer = QTimer(self)
        self._deck_status_timer.setInterval(100)
        self._deck_status_timer.timeout.connect(self.deck_panel.refresh)
        self._deck_status_timer.start()

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(500)
        self._status_timer.timeout.connect(self._refresh_automation_status)
        self._status_timer.timeout.connect(self.performance_control_panel.refresh_monitor)
        self._status_timer.timeout.connect(self.performance_timeline_panel.refresh)
        self._status_timer.start()

        # Rhythm pulses are shorter than the status refresh interval. Keep
        # modifier meters and the selected generator controls visually live.
        self._modifier_feedback_timer = QTimer(self)
        self._modifier_feedback_timer.setInterval(50)
        self._modifier_feedback_timer.timeout.connect(
            self.layer_panel.refresh_performance_modifiers
        )
        self._modifier_feedback_timer.timeout.connect(
            self.generators_panel.sync_live_modulation
        )
        self._modifier_feedback_timer.timeout.connect(
            self.modulator_bank_panel.refresh_live
        )
        self._modifier_feedback_timer.start()

    def _build_workspace(self) -> QWidget:
        """Build the primary Perform / Compose / Prepare operator workspaces."""
        tabs = QTabWidget(self)
        tabs.setObjectName("primaryWorkspaceTabs")
        tabs.setDocumentMode(True)
        tabs.setMovable(False)
        tabs.setUsesScrollButtons(True)

        perform_page = QWidget(tabs)
        perform_layout = QVBoxLayout(perform_page)
        perform_layout.setContentsMargins(10, 8, 10, 8)
        perform_layout.setSpacing(8)
        perform_header = QHBoxLayout()
        perform_title = QLabel("LIVE PERFORMANCE")
        perform_title.setObjectName("sectionHeading")
        perform_header.addWidget(perform_title)
        perform_header.addStretch(1)
        self.workspace_output_label = QLabel("OUTPUT  ·  LOCAL WORKSPACE")
        self.workspace_output_label.setObjectName("mutedLabel")
        perform_header.addWidget(self.workspace_output_label)
        perform_layout.addLayout(perform_header)

        # Put the six existing Performance Macros on the operator surface. The
        # widget is detached from the advanced control dock rather than copied,
        # so values, source mappings and shortcuts keep a single owner.
        self.live_macro_strip = self.performance_control_panel.take_performance_macro_group(
            perform_page
        )

        # Reuse the existing renderer instead of creating a second OpenGL view.
        # The projector and local preview retain their existing independent contexts.
        self.performance_view.setParent(None)
        self.preview_dock.setWidget(
            QLabel("LOCAL PREVIEW is now displayed in the central PERFORM workspace.")
        )
        self.preview_dock.hide()
        self.performance_aspect_preview = AspectRatioPreview(
            self.performance_view,
            parent=perform_page,
        )
        perform_layout.addWidget(self.performance_aspect_preview, 1)
        perform_layout.addWidget(self.live_macro_strip, 0)

        compose_page = QWidget(tabs)
        compose_layout = QVBoxLayout(compose_page)
        compose_layout.setContentsMargins(10, 8, 10, 8)
        compose_layout.setSpacing(8)
        compose_header = QHBoxLayout()
        compose_title = QLabel("COMPOSITION EDITOR")
        compose_title.setObjectName("sectionHeading")
        compose_header.addWidget(compose_title)
        compose_header.addStretch(1)
        self.show_preview_button = QPushButton("OPEN PERFORM WORKSPACE")
        self.show_preview_button.clicked.connect(self.show_local_preview)
        compose_header.addWidget(self.show_preview_button)
        compose_layout.addLayout(compose_header)
        self.generators_panel.setParent(compose_page)
        compose_layout.addWidget(self.generators_panel, 1)

        prepare_page = QWidget(tabs)
        prepare_layout = QVBoxLayout(prepare_page)
        prepare_layout.setContentsMargins(10, 8, 10, 8)
        prepare_layout.setSpacing(8)
        prepare_header = QLabel("MEDIA PREPARATION")
        prepare_header.setObjectName("sectionHeading")
        prepare_layout.addWidget(prepare_header)
        prepare_tabs = QTabWidget(prepare_page)
        prepare_tabs.setObjectName("prepareAssetTabs")
        prepare_tabs.setDocumentMode(True)
        self.media_browser.setParent(None)
        self.asset_library_panel.setParent(None)
        self.media_dock.setWidget(
            QLabel("MEDIA LIBRARY is available in the central PREPARE workspace.")
        )
        self.asset_library_dock.setWidget(
            QLabel("VISUAL ASSET LIBRARY is available in the central PREPARE workspace.")
        )
        self.media_dock.hide()
        self.asset_library_dock.hide()
        prepare_tabs.addTab(self.media_browser, "MEDIA LIBRARY")
        prepare_tabs.addTab(self.asset_library_panel, "VISUAL ASSETS")
        prepare_layout.addWidget(prepare_tabs, 1)

        tabs.addTab(perform_page, "01  PERFORM")
        tabs.addTab(compose_page, "02  COMPOSE")
        tabs.addTab(prepare_page, "03  PREPARE")
        saved_workspace = self._ui_settings.value(
            "ui/active_workspace_v1",
            0,
            type=int,
        )
        tabs.setCurrentIndex(max(0, min(tabs.count() - 1, saved_workspace)))
        tabs.currentChanged.connect(self._on_workspace_changed)
        self.workspace_tabs = tabs
        return tabs

    def _on_workspace_changed(self, index: int) -> None:
        self._ui_settings.setValue("ui/active_workspace_v1", int(index))
        self._ui_settings.sync()
        messages = {
            0: "PERFORM · live composition workspace",
            1: "COMPOSE · edit layers, generators and effects",
            2: "PREPARE · organise footage and visual assets",
        }
        self.statusBar().showMessage(messages.get(index, "Workspace changed"), 1800)

    def _is_compact_workspace(self) -> bool:
        width = max(1, self.width())
        height = max(1, self.height())
        return width < 1280 or width / height < 1.50

    def _sync_responsive_dock_constraints(self) -> None:
        """Relax dock minimums for 4:3 and compact projector workspaces."""
        if (
                not getattr(self, "_responsive_layout_ready", False)
                or not hasattr(self, "media_dock")
        ):
            return
        compact = self._is_compact_workspace()
        if compact == self._responsive_compact:
            return
        self._responsive_compact = compact
        side_minimum = 150 if compact else 220
        right_minimum = 170 if compact else 250
        for dock in (self.media_dock, self.asset_library_dock):
            dock.setMinimumWidth(side_minimum)
        for dock in (
                self.layer_dock,
                self.effects_dock,
                self.automation_dock,
                self.preview_dock,
                self.performance_control_dock,
                self.modulator_bank_dock,
                self.performance_timeline_dock,
        ):
            dock.setMinimumWidth(right_minimum)
        self.deck_dock.setMinimumHeight(100 if compact else 120)
        self.preview_dock.setMinimumSize(
            190 if compact else 260,
            130 if compact else 180,
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not getattr(self, "_responsive_layout_ready", False):
            return
        was_compact = self._responsive_compact
        self._sync_responsive_dock_constraints()
        if (
                was_compact is not None
                and was_compact != self._responsive_compact
                and self._responsive_layout_managed
        ):
            QTimer.singleShot(0, self._apply_default_dock_sizes)

    def _apply_default_dock_sizes(self) -> None:
        # Rebalance dock widths against the available editor area. Portrait-ish
        # 4:3 displays use narrower side docks and retain a usable center canvas.
        compact = self._is_compact_workspace()
        self._sync_responsive_dock_constraints()
        width = max(self.width(), self.minimumWidth())
        height = max(self.height(), self.minimumHeight())
        if compact:
            left_width = max(150, min(220, round(width * 0.17)))
            right_width = max(170, min(250, round(width * 0.20)))
            deck_height = max(100, min(170, round(height * 0.18)))
        else:
            left_width = max(220, min(340, round(width * 0.19)))
            right_width = max(250, min(400, round(width * 0.23)))
            deck_height = max(120, min(190, round(height * 0.20)))
        self.resizeDocks([self.media_dock], [left_width], Qt.Orientation.Horizontal)
        self.resizeDocks([self.layer_dock], [right_width], Qt.Orientation.Horizontal)
        self.resizeDocks([self.deck_dock], [deck_height], Qt.Orientation.Vertical)

    def restore_default_layout(self) -> None:
        """Restore the built-in dock arrangement without changing the project."""
        if not self.restoreState(self._default_dock_state, 4):
            _LOG.warning("Could not restore the built-in dock-state snapshot; rebuilding sizes.")
        for dock in (
                self.deck_dock,
                self.layer_dock,
                self.effects_dock,
                self.automation_dock,
                self.performance_control_dock,
                self.modulator_bank_dock,
                self.performance_timeline_dock,
        ):
            dock.show()
        self.media_dock.hide()
        self.asset_library_dock.hide()
        self.preview_dock.hide()
        self.workspace_tabs.setCurrentIndex(0)
        self.layer_dock.raise_()
        self._responsive_layout_managed = True
        QTimer.singleShot(0, self._apply_default_dock_sizes)
        self._ui_settings.setValue("ui/main_window_state_v5", self._default_dock_state)
        self._ui_settings.sync()
        self.statusBar().showMessage("Default workspace layout restored.", 4000)

    def show_local_preview(self) -> None:
        """Focus the central live canvas instead of opening a secondary preview dock."""
        self.workspace_tabs.setCurrentIndex(0)

    def _make_dock(self, title: str, widget) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(title.lower().replace(" ", "_").replace("+", "plus").replace(" ", "_"))
        dock.setWidget(widget)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
        )
        return dock

    def _sync_performance_macro_shortcuts(self) -> None:
        for shortcut in self._performance_macro_shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self._performance_macro_shortcuts.clear()
        for macro in self.application.performance_macro_engine.list_macros():
            if not macro.keyboard_shortcut:
                continue
            shortcut = QShortcut(QKeySequence(macro.keyboard_shortcut), self)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(
                lambda macro_id=macro.macro_id: self._toggle_performance_macro(macro_id)
            )
            self._performance_macro_shortcuts.append(shortcut)

    def _toggle_performance_macro(self, macro_id: str) -> None:
        current = self.application.performance_macro_values().get(macro_id, 0.0)
        value = 0.0 if current >= 0.5 else 1.0
        try:
            self.application.set_performance_macro_value(
                macro_id,
                value,
                hold_seconds=1.5,
            )
            self.application.apply_modulation()
            self.performance_control_panel.sync_performance_macros()
            self.statusBar().showMessage(
                f"{macro_id.upper()} · {value:.2f}",
                1400,
            )
        except (KeyError, TypeError, ValueError) as exc:
            _LOG.warning("Could not toggle Performance Macro %s: %s", macro_id, exc)

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project…", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Project &As…", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)

        set_save_action = QAction("Save Performance Set…", self)
        set_save_action.triggered.connect(self.save_performance_set)
        file_menu.addAction(set_save_action)
        set_load_action = QAction("Load Performance Set…", self)
        set_load_action.triggered.connect(self.load_performance_set)
        file_menu.addAction(set_load_action)

        file_menu.addSeparator()
        import_action = QAction("Add Media &Folder…", self)
        import_action.triggered.connect(self._choose_media_folder)
        file_menu.addAction(import_action)

        overlay_action = QAction("Add Image / Video Overlay…", self)
        overlay_action.triggered.connect(self.add_overlay_media)
        file_menu.addAction(overlay_action)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = self.menuBar().addMenu("&View")
        restore_layout_action = QAction("Restore Default Layout", self)
        restore_layout_action.setShortcut(QKeySequence("Ctrl+Shift+0"))
        restore_layout_action.triggered.connect(self.restore_default_layout)
        view_menu.addAction(restore_layout_action)
        workspace_menu = view_menu.addMenu("WORKSPACE")
        for index, label, shortcut in (
            (0, "01 · PERFORM", "Ctrl+1"),
            (1, "02 · COMPOSE", "Ctrl+2"),
            (2, "03 · PREPARE", "Ctrl+3"),
        ):
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(
                lambda checked=False, target=index: self.workspace_tabs.setCurrentIndex(target)
            )
            workspace_menu.addAction(action)
        view_menu.addSeparator()
        for dock in (
                self.deck_dock,
                self.layer_dock,
                self.effects_dock,
                self.automation_dock,
                self.performance_control_dock,
                self.modulator_bank_dock,
                self.performance_timeline_dock,
        ):
            view_menu.addAction(dock.toggleViewAction())

        output_menu = view_menu.addMenu("PROJECTOR OUTPUT")
        output_menu.aboutToShow.connect(
            lambda menu=output_menu: self._populate_projector_menu(menu)
        )
        gui_application = QGuiApplication.instance()
        if gui_application is not None:
            gui_application.screenAdded.connect(self._display_configuration_changed)
            gui_application.screenRemoved.connect(self._display_configuration_changed)

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _toggle_performance_mode(self, enabled: bool) -> None:
        if not enabled:
            try:
                self.application.stop_performance_mode()
            except Exception as exc:
                _LOG.exception("Could not stop Performance Mode")
                QMessageBox.warning(self, "Performance Mode", str(exc))
            self.performance_mode_button.setText("▶ PERFORMANCE MODE")
            self.performance_control_panel.refresh_monitor()
            self.statusBar().showMessage("Performance Mode stopped.", 5000)
            return

        try:
            audio_source = self.performance_control_panel.audio_device_combo.currentData()
            audio_test_signal = audio_source == "test"
            audio_device_id = (
                str(audio_source)
                if audio_source not in {None, "test"}
                else ""
            )
            settings = self.automation_panel._build_settings()
            duration = self.automation_panel.duration_combo.currentData()
            plan = PerformanceModePlan(
                osc_bind_address=(
                        self.performance_control_panel.osc_bind_edit.text().strip()
                        or "127.0.0.1"
                ),
                osc_port=self.performance_control_panel.osc_port_spin.value(),
                audio_device_id=audio_device_id,
                audio_test_signal=audio_test_signal,
                prefer_loopback=False,
                start_automation=True,
                automation_duration_seconds=duration,
                automation_settings=settings.to_dict(),
                stop_automation_on_patch_stop=True,
                install_default_mappings=True,
            )
            state = self.application.start_performance_mode(plan)
            receiver = self.application.osc_receiver.snapshot()
            if receiver["running"]:
                self.performance_control_panel.osc_port_spin.setValue(
                    int(receiver["port"])
                )
            self.performance_mode_button.setText("■ STOP PERFORMANCE MODE")
            self.performance_control_panel.refresh_monitor()
            self.statusBar().showMessage(
                "Performance Mode armed · run SONATA Expanded in Sonic Pi. "
                "AUTO PERFORMANCE starts on transport/start or the first clock/bar.",
                9000,
            )
            if state["phase"] == "degraded":
                self.statusBar().showMessage(
                    f"Performance Mode degraded · {state['error']}",
                    10000,
                )
        except Exception as exc:
            _LOG.exception("Could not start Performance Mode")
            self.application.stop_performance_mode()
            self.performance_mode_button.blockSignals(True)
            self.performance_mode_button.setChecked(False)
            self.performance_mode_button.blockSignals(False)
            self.performance_mode_button.setText("▶ PERFORMANCE MODE")
            QMessageBox.critical(self, "Performance Mode could not start", str(exc))

    def _sync_performance_mode_button(self) -> None:
        enabled = self.application.performance_mode_snapshot()["enabled"]
        self.performance_mode_button.blockSignals(True)
        self.performance_mode_button.setChecked(enabled)
        self.performance_mode_button.blockSignals(False)
        self.performance_mode_button.setText(
            "■ STOP PERFORMANCE MODE" if enabled else "▶ PERFORMANCE MODE"
        )

    def save_performance_set(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Performance Set", "performance.eliset",
            "eli_lab Performance Set (*.eliset)",
        )
        if not path:
            return
        if not path.lower().endswith(".eliset"):
            path += ".eliset"
        try:
            saved = self.application.save_performance_set(path)
        except Exception as exc:
            QMessageBox.critical(self, "Could Not Save Performance Set", str(exc))
            return
        self.statusBar().showMessage(f"Performance set saved · {saved}", 5000)

    def load_performance_set(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Performance Set", "",
            "eli_lab Performance Set (*.eliset)",
        )
        if not path:
            return
        try:
            self.application.load_performance_set(path)
            self._sync_performance_mode_button()
            self.performance_control_panel.sync_from_application()
            self.automation_panel.sync_performance_plan(self.application.performance_mode.plan)
        except Exception as exc:
            QMessageBox.critical(self, "Could Not Load Performance Set", str(exc))
            return
        self.layer_panel.refresh()
        self.generators_panel.refresh()
        self.performance_control_panel.sync_from_application()
        self.performance_control_panel.sync_modulator_sources()
        self.performance_control_panel.refresh_routes()
        self.modulator_bank_panel.refresh()
        self.performance_timeline_panel.refresh(force=True)
        self.statusBar().showMessage(f"Performance set loaded · {Path(path).name}", 5000)

    def _populate_projector_menu(self, menu) -> None:
        menu.clear()
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()
        if not screens:
            unavailable = QAction("No displays detected", menu)
            unavailable.setEnabled(False)
            menu.addAction(unavailable)
        for index, screen in enumerate(screens, start=1):
            geometry = screen.geometry()
            primary_label = " · PRIMARY" if screen == primary else ""
            label = (
                f"Display {index} · {screen.name()} "
                f"({geometry.width()}×{geometry.height()}){primary_label}"
            )
            action = QAction(label, menu)
            action.triggered.connect(
                lambda checked=False, target=screen: self.open_projector_output(target)
            )
            menu.addAction(action)
        menu.addSeparator()
        close_output_action = QAction("Close Projector Output", menu)
        close_output_action.setEnabled(self.output_manager.window is not None)
        close_output_action.triggered.connect(self.output_manager.close)
        menu.addAction(close_output_action)

    def _display_configuration_changed(self, *_args) -> None:
        self.statusBar().showMessage(
            f"Display configuration changed · {len(QGuiApplication.screens())} display(s) detected",
            5000,
        )

    def open_projector_output(self, screen) -> None:
        try:
            if self.output_manager.window is not None:
                self.output_manager.close()
            self._restore_local_preview_on_close = self.workspace_tabs.currentIndex() == 0
            window = self.output_manager.open_on_screen(screen)
            if self._restore_local_preview_on_close:
                # Release the local preview surface while the projector is active.
                self.workspace_tabs.setCurrentIndex(1)
            window.performance_view.render_status_changed.connect(
                self.status_label.setText
            )
            if window.performance_view.engine.initialized:
                self.status_label.setText(
                    f"PROJECTOR READY · {window.performance_view.engine.renderer_name}"
                )
            elif window.performance_view._initialization_error:
                self.status_label.setText(
                    f"PROJECTOR ERROR · {window.performance_view._initialization_error}"
                )
            else:
                self.status_label.setText("PROJECTOR OPEN · waiting for its OpenGL context")
            window.closed.connect(self._projector_output_closed)
            self.workspace_output_label.setText(
                f"OUTPUT  ·  PROJECTOR  ·  {screen.name()}"
            )
            self.statusBar().showMessage(
                (
                    f"Projector output opened on {screen.name()}. "
                    "Press Escape on the output to close it."
                ),
                6000,
            )
        except Exception as exc:
            _LOG.exception("Could not open projector output")
            QMessageBox.critical(self, "Projector output failed", str(exc))

    def _projector_output_closed(self) -> None:
        self.workspace_output_label.setText("OUTPUT  ·  LOCAL WORKSPACE")
        if self.performance_view.engine.initialized:
            self.status_label.setText(
                f"LOCAL PREVIEW READY · {self.performance_view.engine.renderer_name}"
            )
        elif self.performance_view._initialization_error:
            self.status_label.setText(
                f"LOCAL PREVIEW ERROR · {self.performance_view._initialization_error}"
            )
        else:
            self.status_label.setText(
                "LOCAL PREVIEW IDLE · select PERFORM to initialise OpenGL"
            )
        if self._restore_local_preview_on_close:
            self.workspace_tabs.setCurrentIndex(0)
        self._restore_local_preview_on_close = False

    def refresh_automation_media_pool(self) -> None:
        if self.application.refresh_automation_media_pool():
            self._refresh_automation_status()

    def add_overlay_media(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Add image or video overlay",
            "",
            (
                "Overlay media (*.png *.apng *.gif *.webp *.jpg *.jpeg *.bmp "
                "*.mp4 *.mov *.mkv *.avi *.webm *.m4v)"
            ),
        )
        if not path:
            return
        try:
            layer = self.application.add_media_overlay(path)
            self.layer_panel.refresh()
            self.generators_panel.refresh(select_id=layer.id)
            self.statusBar().showMessage(f"Added overlay {layer.name}", 4000)
        except Exception as exc:
            _LOG.exception("Could not add overlay media")
            QMessageBox.warning(self, "Overlay load failed", str(exc))

    def _choose_media_folder(self) -> None:
        self.workspace_tabs.setCurrentIndex(2)
        self.media_browser.choose_folder()

    def assign_media(self, asset: object, deck_id: str) -> None:
        try:
            self.application.assign_media_to_deck(asset, deck_id)
            self.deck_panel.refresh()
            self.statusBar().showMessage(
                f"Loaded {getattr(asset, 'name', 'video')} into {deck_id.upper()}",
                4000,
            )
        except Exception as exc:
            _LOG.exception("Could not assign media to deck")
            QMessageBox.critical(self, "Video load failed", str(exc))

    def deck_action(self, deck_id: str, action: str) -> None:
        deck = self.application.decks[deck_id]
        try:
            if action == "load":
                deck_index = self.media_browser.deck_combo.findData(deck_id)
                if deck_index >= 0:
                    self.media_browser.deck_combo.setCurrentIndex(deck_index)
                self.workspace_tabs.setCurrentIndex(2)
                self.media_browser.asset_list.setFocus()
                self.statusBar().showMessage(
                    f"Choose a clip to load into {deck_id.upper()}. "
                    "The current source remains active until you choose one.",
                    5000,
                )
            elif action == "play":
                deck.play()
            elif action == "pause":
                deck.pause()
            elif action == "hold":
                if not deck.hold():
                    self.statusBar().showMessage(
                        "Wait for the first decoded frame before holding this deck.",
                        3000,
                    )
            elif action == "release_hold":
                deck.release_hold()
            elif action == "restart":
                deck.restart()
            elif action == "stop":
                deck.stop()
            self.deck_panel.refresh()
        except Exception as exc:
            _LOG.exception("Deck action failed: %s · %s", deck_id, action)
            QMessageBox.warning(self, "Deck error", str(exc))

    def set_deck_loop(self, deck_id: str, enabled: bool) -> None:
        self.application.decks[deck_id].set_loop(enabled)

    def randomize_decks(self) -> None:
        assets = self.application.media_library.list_assets()
        count = self.application.performance_manager.randomize_decks(
            assets,
            self.application.decks.values(),
        )
        self.deck_panel.refresh()
        self.statusBar().showMessage(f"Assigned {count} video deck(s).", 3000)

    def randomize_layout(self) -> None:
        count = self.application.performance_manager.randomize_layout(
            self.application.composition.layers
        )
        self.layer_panel.refresh()
        self.statusBar().showMessage(f"Randomized {count} layer(s).", 3000)

    def lock_all(self, locked: bool) -> None:
        for deck in self.application.decks.values():
            deck.locked = locked
        for layer in tuple(self.application.composition.layers):
            self.application.set_layer_locked(layer.id, locked)
        self.deck_panel.refresh()
        self.layer_panel.refresh()

    def start_automation(
            self,
            collection_id: str | None,
            duration_seconds: float | None,
            settings,
    ) -> None:
        try:
            count = self.application.start_automation(
                collection_id=collection_id,
                settings=settings,
                duration_seconds=duration_seconds,
            )
            self.deck_panel.refresh()
            self.layer_panel.refresh()
            self.effects_panel.sync_from_settings()
            self.automation_panel.set_running(
                True,
                (
                    f"Running · {count} deck(s) automated. Layouts, generator text "
                    "and layer FX will evolve automatically."
                ),
            )
            self._refresh_automation_status()
        except ValueError as exc:
            # Empty or unavailable footage pools are expected operator errors,
            # not application faults; keep the log useful without a traceback.
            _LOG.warning("Auto Performance unavailable: %s", exc)
            message = str(exc)
            if "No playable video files" in message:
                message = (
                    "No playable video files are available in this footage pool. "
                    "Import a video folder in MEDIA LIBRARY, wait for scanning to finish, "
                    "then retry."
                )
            self.automation_panel.set_running(False, message)
            self.statusBar().showMessage(message, 8000)
            QMessageBox.information(self, "Auto Performance not started", message)
        except Exception as exc:
            _LOG.exception("Could not start automation")
            self.automation_panel.set_running(False, f"Could not start · {exc}")
            QMessageBox.warning(self, "Automation could not start", str(exc))

    def stop_automation(self) -> None:
        self.application.stop_automation()
        self.automation_panel.set_running(
            False,
            "Stopped · video decks keep their current playback.",
        )

    def _runtime_tick(self) -> None:
        self.application.refresh_frames()
        was_running = self.application.automation.running
        previous_auto_action = self.application.automation.last_action
        previous_scene = self.application.performance_control.scene_id
        self.application.tick_performance_control()
        timeline_snapshot = self.application.performance_timeline.snapshot()
        timeline_revision = int(timeline_snapshot["state_revision"])
        if timeline_revision != self._last_timeline_state_revision:
            self._last_timeline_state_revision = timeline_revision
            self.performance_timeline_panel.refresh(force=True)
            event_type = str(timeline_snapshot["last_event_type"])
            if event_type in {"scene_recall", "transition_cue"}:
                self.deck_panel.refresh()
                self.layer_panel.refresh()
                self.modulator_bank_panel.refresh()
                self.effects_panel.sync_from_settings()
                self.generators_panel.refresh()
            elif event_type == "clip_trigger":
                self.deck_panel.refresh()
            elif event_type == "effect_change":
                self.effects_panel.sync_from_settings()
            elif event_type in {"text_regenerate", "palette_change"}:
                self.generators_panel.refresh()
            elif event_type == "modulation":
                self.performance_control_panel.sync_performance_macros()
            if timeline_snapshot["last_event_result"]:
                self.statusBar().showMessage(
                    str(timeline_snapshot["last_event_result"]),
                    2600,
                )
        control_revision = self.application.performance_control.revision
        if control_revision != self._last_control_revision:
            self.control_status_label.setText(
                self.application.performance_control.status_text()
            )
            self._last_control_revision = control_revision
        if self.application.performance_control.scene_id != previous_scene:
            self.effects_panel.sync_from_settings()
            self.generators_panel.refresh()
            self.performance_control_panel.sync_scene_selection(
                self.application.performance_control.scene_id
            )

        changed = self.application.tick_automation()
        musical_change = (
                self.application.automation.last_action != previous_auto_action
        )
        running = self.application.automation.running
        if not was_running and running:
            self.automation_panel.set_running(
                True,
                "Running · Sonic Pi has started the autonomous performance.",
            )
        elif was_running and not running:
            self.automation_panel.set_running(
                False,
                self.application.automation.last_action,
            )
        if changed or musical_change:
            self.deck_panel.refresh()
            self.layer_panel.refresh()
            self.effects_panel.sync_from_settings()
            self.generators_panel.refresh()
        if running and musical_change:
            self.automation_panel.set_status(
                f"SONIC PI · {self.application.automation.last_action}"
            )

        mode = self.application.performance_mode_snapshot()
        if mode["enabled"] != self.performance_mode_button.isChecked():
            self._sync_performance_mode_button()
        if mode["enabled"]:
            phase = mode["phase"].upper()
            self.performance_mode_button.setText(f"■ STOP PERFORMANCE MODE · {phase}")
            automation_state = (
                "running" if mode["automation_running"]
                else "armed" if mode["automation_armed"]
                else "idle"
            )
            self.performance_mode_button.setToolTip(
                f"Phase: {mode['phase']}\n"
                f"Automation: {automation_state}\n"
                f"Audio: {mode['audio_status']}\n"
                f"Last event: {mode['last_event']}\n"
                f"Error: {mode['error'] or 'none'}"
            )

    def _refresh_automation_status(self) -> None:
        director = self.application.automation
        if not director.running:
            return
        remaining = director.remaining_seconds()
        if remaining is None:
            time_label = "until stopped"
        else:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            time_label = f"{minutes:02d}:{seconds:02d} remaining"
        self.automation_panel.set_status(f"RUNNING · {director.last_action} · {time_label}")

    def new_project(self) -> None:
        answer = QMessageBox.question(
            self,
            "New project",
            "Create a new composition? Unsaved project changes will be lost.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.application.reset_project()
        self._sync_performance_mode_button()
        self.performance_control_panel.sync_from_application()
        self.automation_panel.sync_performance_plan(self.application.performance_mode.plan)
        self.deck_panel.refresh()
        self.layer_panel.refresh()
        self.modulator_bank_panel.refresh()
        self.layer_panel.sync_performance_modifier_sources()
        self.performance_control_panel.sync_modulator_sources()
        self.performance_control_panel.refresh_routes()
        self.performance_control_panel.sync_from_application()
        self.performance_timeline_panel.refresh(force=True)
        self.effects_panel.sync_from_settings()
        self.generators_panel.refresh()
        self.automation_panel.set_running(False, "Ready · import footage to begin.")
        self.statusBar().showMessage("New composition created.", 3000)

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open AV Translator project",
            "",
            "ELI AV Project (*.eliav);;JSON files (*.json)",
        )
        if not path:
            return
        try:
            self.application.load_project(path)
            self._sync_performance_mode_button()
            self.performance_control_panel.sync_from_application()
            self.automation_panel.sync_performance_plan(self.application.performance_mode.plan)
            self.deck_panel.refresh()
            self.layer_panel.refresh()
            self.modulator_bank_panel.refresh()
            self.layer_panel.sync_performance_modifier_sources()
            self.performance_control_panel.sync_modulator_sources()
            self.performance_control_panel.refresh_routes()
            self.performance_control_panel.sync_from_application()
            self.performance_timeline_panel.refresh(force=True)
            self.effects_panel.sync_from_settings()
            self.generators_panel.refresh()
            self.statusBar().showMessage(f"Opened {Path(path).name}", 4000)
        except Exception as exc:
            _LOG.exception("Could not open project %s", path)
            QMessageBox.critical(self, "Project open failed", str(exc))

    def save_project(self) -> None:
        if self.application.current_project_path is None:
            self.save_project_as()
            return
        try:
            path = self.application.save_project(self.application.current_project_path)
            self.statusBar().showMessage(f"Saved {path.name}", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "Project save failed", str(exc))

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save AV Translator project",
            "Untitled.eliav",
            "ELI AV Project (*.eliav)",
        )
        if not path:
            return
        if not path.lower().endswith(".eliav"):
            path += ".eliav"
        try:
            saved = self.application.save_project(path)
            self.statusBar().showMessage(f"Saved {saved.name}", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "Project save failed", str(exc))

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            (
                f"<h2>{APP_NAME} {APP_VERSION}</h2>"
                "<p>Live audiovisual performance environment.</p>"
                "<p>Video collage · procedural geometry · text art · particles<br>"
                "GPU effects · audio reactivity · Sonic Pi OSC · projector output</p>"
                "<p><b>Built with</b><br>"
                "Python · PySide6 / Qt · ModernGL / OpenGL · PyAV / FFmpeg<br>"
                "NumPy · SoundCard · python-osc · MIDI</p>"
                f"<p><b>Created by</b><br>{APP_AUTHOR}<br>"
                f"{APP_STUDIO} · 2026</p>"
                f"<p>{APP_COPYRIGHT}<br>"
                f'<a href="{APP_REPOSITORY_URL}">Project source</a></p>'
            ),
        )

    def closeEvent(self, event) -> None:
        self._ui_settings.setValue("ui/main_window_geometry_v2", self.saveGeometry())
        self._ui_settings.setValue("ui/main_window_state_v5", self.saveState(4))
        self._ui_settings.setValue(
            "ui/active_workspace_v1",
            self.workspace_tabs.currentIndex(),
        )
        self._runtime_timer.stop()
        self._status_timer.stop()
        self._modifier_feedback_timer.stop()
        self.media_browser.shutdown_workers()
        self.output_manager.close()
        self.performance_view.shutdown_renderer()
        self.application.shutdown()
        super().closeEvent(event)
