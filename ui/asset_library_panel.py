from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from media.asset_index import VisualAsset, VisualAssetIndex
from ui.i18n import set_ui_text, ui_text


class _AssetScanSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class _AssetScanWorker(QRunnable):
    """Scan the immutable root snapshot away from the UI thread."""

    def __init__(self, roots: list[Path]) -> None:
        super().__init__()
        self.roots = roots
        self.signals = _AssetScanSignals()

    def run(self) -> None:
        try:
            assets = VisualAssetIndex(self.roots).scan()
            self.signals.finished.emit(assets)
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class AssetLibraryPanel(QWidget):
    """Browse indexed visual assets by semantic purpose and add them to a composition."""

    composition_changed = Signal()

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self._index_loaded = False
        self._scan_in_progress = False
        self._scan_worker: _AssetScanWorker | None = None
        self._thread_pool = QThreadPool.globalInstance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search textures, materials, masks…")
        layout.addWidget(self.search_edit)
        self.add_folder_button = QPushButton("ADD ASSET FOLDER…")
        layout.addWidget(self.add_folder_button)
        self.purpose_combo = QComboBox()
        self.purpose_combo.addItem("All purposes", "")
        for purpose in (
            "overlay",
            "texture",
            "background",
            "postproduction",
            "surface",
            "distress",
            "mask",
            "track matte",
            "material",
            "geometry",
            "particles",
            "atmosphere",
            "environment",
            "normal map",
            "roughness map",
            "displacement map",
            "ambient occlusion",
            "specular map",
        ):
            self.purpose_combo.addItem(purpose.title(), purpose)
        layout.addWidget(self.purpose_combo)
        self.kind_combo = QComboBox()
        self.kind_combo.addItem("All media", "")
        self.kind_combo.addItem("Images", "image")
        self.kind_combo.addItem("Videos", "video")
        layout.addWidget(self.kind_combo)
        self.asset_list = QListWidget()
        layout.addWidget(self.asset_list, 1)
        self.detail_label = QLabel("—")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        self.add_button = QPushButton("ADD AS OVERLAY")
        self.add_button.setEnabled(False)
        layout.addWidget(self.add_button)
        self.search_edit.textChanged.connect(self.refresh)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.purpose_combo.currentIndexChanged.connect(self.refresh)
        self.kind_combo.currentIndexChanged.connect(self.refresh)
        self.asset_list.currentItemChanged.connect(self._selection_changed)
        self.add_button.clicked.connect(self.add_selected)
        self.refresh()

    def add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, ui_text("Add visual asset folder"))
        if not folder:
            return
        try:
            self.application.add_visual_asset_root(folder)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(
                self,
                ui_text("Asset folder could not be indexed"),
                ui_text(str(exc)),
            )
            return
        self._index_loaded = False
        self._start_index_scan()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._index_loaded and not self._scan_in_progress:
            self._start_index_scan()

    def _start_index_scan(self) -> None:
        if self._scan_in_progress:
            return
        self._scan_in_progress = True
        set_ui_text(self.detail_label, "Indexing bundled and user visual assets…")
        self.add_button.setEnabled(False)
        worker = _AssetScanWorker(list(self.application.visual_asset_index.roots))
        worker.signals.finished.connect(self._on_scan_finished)
        worker.signals.failed.connect(self._on_scan_failed)
        self._scan_worker = worker
        self._thread_pool.start(worker)

    def _on_scan_finished(self, assets: list[VisualAsset]) -> None:
        worker = self._scan_worker
        scanned_roots = set(worker.roots) if worker is not None else set()
        current_roots = set(self.application.visual_asset_index.roots)
        self._scan_in_progress = False
        self._scan_worker = None
        if scanned_roots != current_roots:
            # A root was added while scanning. Discard the stale result and
            # rescan the current root snapshot rather than losing that folder.
            self._index_loaded = False
            self._start_index_scan()
            return
        self.application.visual_asset_index.assets = assets
        self._index_loaded = True
        self.refresh()
        set_ui_text(
            self.detail_label,
            f"Indexed {len(assets)} visual assets across "
            f"{len(self.application.visual_asset_index.roots)} folders.",
        )

    def _on_scan_failed(self, error: str) -> None:
        self._scan_in_progress = False
        self._scan_worker = None
        set_ui_text(self.detail_label, f"Asset indexing failed: {error}")
        self.add_button.setEnabled(False)

    def refresh(self, *_args) -> None:
        selected_id = None
        current = self.asset_list.currentItem()
        if current is not None:
            selected_id = current.data(256)
        assets = self.application.search_visual_assets(
            self.search_edit.text(),
            purpose=self.purpose_combo.currentData() or None,
            kind=self.kind_combo.currentData() or None,
        )
        self.asset_list.clear()
        for asset in assets:
            item = QListWidgetItem(
                f"{asset.name}  ·  {asset.category}  ·  {asset.kind}"
            )
            item.setData(256, asset.id)
            self.asset_list.addItem(item)
            if asset.id == selected_id:
                self.asset_list.setCurrentItem(item)
        if self.asset_list.count() == 0:
            set_ui_text(self.detail_label, "No indexed assets match this search.")
        elif self.asset_list.currentItem() is None:
            self.asset_list.setCurrentRow(0)

    def _selection_changed(self, current, _previous=None) -> None:
        asset_id = current.data(256) if current is not None else None
        asset = next(
            (
                item
                for item in self.application.visual_asset_index.assets
                if item.id == asset_id
            ),
            None,
        )
        self.add_button.setEnabled(asset is not None)
        if asset is not None:
            set_ui_text(
                self.detail_label,
                f"{asset.path}\nTags: {', '.join(asset.tags)}\n"
                f"Purposes: {', '.join(asset.purposes)}",
            )

    def add_selected(self) -> None:
        item = self.asset_list.currentItem()
        if item is None:
            return
        try:
            layer = self.application.add_library_asset_overlay(item.data(256))
        except Exception as exc:
            QMessageBox.warning(self, ui_text("Asset could not be added"), ui_text(str(exc)))
            return
        self.composition_changed.emit()
        set_ui_text(self.detail_label, f"Added {layer.name} as a composition overlay.")
