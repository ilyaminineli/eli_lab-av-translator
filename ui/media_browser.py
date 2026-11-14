from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from media.library import MediaLibrary
from media.models import MediaAsset
from media.thumbnails import generate_thumbnail
from ui.i18n import set_ui_text, ui_text
from ui.icons import app_icon

_LOG = logging.getLogger(__name__)


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    completed = Signal(str, object)


class ScanWorker(QRunnable):
    def __init__(self, library: MediaLibrary, folder: str) -> None:
        super().__init__()
        self.library = library
        self.folder = folder
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.signals.result.emit(self.library.add_folder(self.folder))
        except Exception as exc:
            self.signals.error.emit(str(exc))


class ThumbnailWorker(QRunnable):
    def __init__(self, asset: MediaAsset) -> None:
        super().__init__()
        self.asset = asset
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = generate_thumbnail(self.asset.path, self.asset.id)
            self.signals.completed.emit(
                self.asset.id,
                str(result) if result is not None else None,
            )
        except Exception:
            _LOG.exception("Thumbnail worker failed for %s", self.asset.path)
            self.signals.completed.emit(self.asset.id, None)


class MediaBrowser(QWidget):
    assign_requested = Signal(object, str)
    library_updated = Signal()

    def __init__(self, library: MediaLibrary, parent=None) -> None:
        super().__init__(parent)
        self.library = library
        self.scan_pool = QThreadPool(self)
        self.scan_pool.setMaxThreadCount(1)
        self.thumbnail_pool = QThreadPool(self)
        self.thumbnail_pool.setMaxThreadCount(2)
        self._scan_queue: deque[str] = deque()
        self._scan_queued: set[str] = set()
        self._scan_active = False
        self._scan_worker: ScanWorker | None = None
        self._thumbnail_queue: deque[MediaAsset] = deque()
        self._thumbnail_workers: dict[str, ThumbnailWorker] = {}
        self._thumbnail_pending: set[str] = set()
        self._assets: dict[str, MediaAsset] = {}
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        top = QHBoxLayout()
        self.add_folder_button = QPushButton("ADD FOLDER")
        self.add_folder_button.clicked.connect(self.choose_folder)
        top.addWidget(self.add_folder_button, 1)
        self.library_tools_button = QToolButton()
        self.library_tools_button.setText("LIBRARY")
        self.library_tools_button.setIcon(app_icon("settings"))
        self.library_tools_button.setIconSize(QSize(15, 15))
        self.library_tools_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.library_tools_button.setToolTip("Media library tools")
        self.library_tools_button.setAccessibleName("Media library tools")
        self.library_tools_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )
        tools_menu = QMenu(self.library_tools_button)
        self.remove_collection_action = tools_menu.addAction(
            "Remove selected folder from library…"
        )
        self.remove_collection_action.triggered.connect(self.remove_selected_collection)
        self.prune_action = tools_menu.addAction("Remove missing files…")
        self.prune_action.triggered.connect(self.prune_missing_files)
        tools_menu.addSeparator()
        self.clean_cache_action = tools_menu.addAction("Clean unused thumbnails")
        self.clean_cache_action.triggered.connect(self.clean_thumbnail_cache)
        self.clear_action = tools_menu.addAction("Clear entire media library…")
        self.clear_action.triggered.connect(self.clear_library)
        self.library_tools_button.setMenu(tools_menu)
        top.addWidget(self.library_tools_button)
        layout.addLayout(top)

        collection_row = QHBoxLayout()
        collection_row.addWidget(QLabel("FOLDER"))
        self.collection_combo = QComboBox()
        self.collection_combo.currentIndexChanged.connect(self._refresh_asset_items)
        collection_row.addWidget(self.collection_combo, 1)
        layout.addLayout(collection_row)

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Assign to"))
        self.deck_combo = QComboBox()
        for deck_id, label in (
            ("deck_a", "Deck A"),
            ("deck_b", "Deck B"),
            ("deck_c", "Deck C"),
            ("deck_d", "Deck D"),
        ):
            self.deck_combo.addItem(label, deck_id)
        target_row.addWidget(self.deck_combo, 1)
        layout.addLayout(target_row)

        self.asset_list = QListWidget()
        self.asset_list.setIconSize(QSize(112, 64))
        self.asset_list.itemDoubleClicked.connect(self.assign_item)
        layout.addWidget(self.asset_list, 1)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("mutedLabel")
        layout.addWidget(self.status_label)

        self.refresh()

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, ui_text("Add video folder"))
        if folder:
            self.scan_folder(folder)

    def scan_folder(self, folder: str) -> None:
        path = str(Path(folder).expanduser().resolve())
        key = path.casefold()
        if key in self._scan_queued:
            return
        self._scan_queue.append(path)
        self._scan_queued.add(key)
        self._start_next_scan()

    def _start_next_scan(self) -> None:
        if self._scan_active or not self._scan_queue:
            return
        folder = self._scan_queue.popleft()
        self._scan_active = True
        self.add_folder_button.setEnabled(False)
        self.library_tools_button.setEnabled(False)
        set_ui_text(
            self.status_label,
            f"Scanning {Path(folder).name}… {len(self._scan_queue)} folder(s) queued.",
        )
        worker = ScanWorker(self.library, folder)
        self._scan_worker = worker
        worker.signals.result.connect(self.scan_finished)
        worker.signals.error.connect(self.scan_failed)
        self.scan_pool.start(worker)

    def _finish_scan(self) -> None:
        if self._scan_worker is not None:
            self._scan_queued.discard(
                str(Path(self._scan_worker.folder).resolve()).casefold()
            )
        self._scan_worker = None
        self._scan_active = False
        if self._scan_queue:
            self._start_next_scan()
        else:
            self.add_folder_button.setEnabled(True)
            self.library_tools_button.setEnabled(True)

    def dragEnterEvent(self, event) -> None:
        if any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        folders = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile() and Path(url.toLocalFile()).is_dir()
        ]
        if not folders:
            event.ignore()
            return
        for folder in folders:
            self.scan_folder(folder)
        event.acceptProposedAction()

    def scan_finished(self, assets: list[MediaAsset]) -> None:
        self.refresh()
        set_ui_text(self.status_label, f"Indexed {len(assets)} video file(s).")
        self.library_updated.emit()
        self._queue_thumbnails(assets)
        self._finish_scan()

    def scan_failed(self, message: str) -> None:
        set_ui_text(self.status_label, f"Scan failed: {message}")
        _LOG.error("Media scan failed: %s", message)
        self._finish_scan()

    def _queue_thumbnails(self, assets: list[MediaAsset]) -> None:
        for asset in assets:
            if asset.thumbnail_path or asset.id in self._thumbnail_pending:
                continue
            self._thumbnail_pending.add(asset.id)
            self._thumbnail_queue.append(asset)
        self._pump_thumbnail_queue()

    def _pump_thumbnail_queue(self) -> None:
        while self._thumbnail_queue and len(self._thumbnail_workers) < 2:
            asset = self._thumbnail_queue.popleft()
            if self.library.get_asset(asset.id) is None:
                self._thumbnail_pending.discard(asset.id)
                continue
            worker = ThumbnailWorker(asset)
            self._thumbnail_workers[asset.id] = worker
            worker.signals.completed.connect(self._thumbnail_completed)
            self.thumbnail_pool.start(worker)

    def _thumbnail_completed(self, asset_id: str, thumbnail_path: object) -> None:
        self._thumbnail_workers.pop(asset_id, None)
        self._thumbnail_pending.discard(asset_id)
        if isinstance(thumbnail_path, str) and thumbnail_path:
            # A folder may have been removed while its thumbnail was decoding.
            # Do not leave the late result behind as an unreferenced cache file.
            if self.library.get_asset(asset_id) is None:
                Path(thumbnail_path).unlink(missing_ok=True)
                self._pump_thumbnail_queue()
                return
            self.library.update_thumbnail(asset_id, thumbnail_path)
            for index in range(self.asset_list.count()):
                item = self.asset_list.item(index)
                asset = item.data(Qt.ItemDataRole.UserRole)
                if asset and asset.id == asset_id:
                    item.setIcon(QIcon(thumbnail_path))
                    break
        else:
            for index in range(self.asset_list.count()):
                item = self.asset_list.item(index)
                asset = item.data(Qt.ItemDataRole.UserRole)
                if asset and asset.id == asset_id:
                    item.setToolTip(
                        f"{asset.path}\nThumbnail unavailable; source video remains indexed."
                    )
                    break
        self._pump_thumbnail_queue()

    def refresh(self) -> None:
        selected = self.collection_combo.currentData()
        collections = self.library.list_collections()
        self.collection_combo.blockSignals(True)
        self.collection_combo.clear()
        total = sum(int(item["asset_count"]) for item in collections)
        self.collection_combo.addItem(f"All folders · {total} clips", None)
        for item in collections:
            name = str(item["name"])
            count = int(item["asset_count"])
            self.collection_combo.addItem(
                f"{name} · {count} clips",
                str(item["id"]),
            )
        selected_index = self.collection_combo.findData(selected)
        self.collection_combo.setCurrentIndex(
            selected_index if selected_index >= 0 else 0
        )
        self.collection_combo.blockSignals(False)
        self._refresh_asset_items()
        self.remove_collection_action.setEnabled(
            bool(self.collection_combo.currentData())
        )

    def _refresh_asset_items(self, *_args: object) -> None:
        self.asset_list.clear()
        self._assets.clear()
        collection_id = self.collection_combo.currentData()
        assets = self.library.list_assets(
            collection_id=str(collection_id) if collection_id else None
        )
        for asset in assets:
            self._assets[asset.id] = asset
            item = QListWidgetItem(asset.name)
            item.setData(Qt.ItemDataRole.UserRole, asset)
            if asset.thumbnail_path and Path(asset.thumbnail_path).is_file():
                item.setIcon(QIcon(asset.thumbnail_path))
            item.setToolTip(asset.path)
            self.asset_list.addItem(item)
        if assets:
            set_ui_text(self.status_label, f"{len(assets)} asset(s) in selected view.")
        else:
            set_ui_text(
                self.status_label,
                "No clips in this view. Add a folder or change the filter.",
            )
        self.remove_collection_action.setEnabled(bool(collection_id))

    def remove_selected_collection(self) -> None:
        collection_id = self.collection_combo.currentData()
        if not collection_id:
            return
        name = self.collection_combo.currentText()
        answer = QMessageBox.question(
            self,
            ui_text("Remove folder from media library"),
            (
                f"Remove {name} from the library index?\n\n"
                "This removes its entries and cached thumbnails only. "
                "Your original video files and folders will NOT be deleted. "
                "Clips already loaded into decks continue playing."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        removed = self.library.remove_collection(str(collection_id))
        self.refresh()
        self.library_updated.emit()
        set_ui_text(
            self.status_label,
            f"Removed {removed} indexed clip(s). Source files were kept.",
        )

    def prune_missing_files(self) -> None:
        answer = QMessageBox.question(
            self,
            ui_text("Remove missing files"),
            ui_text("Remove library entries whose source files can no longer be found?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        removed = self.library.remove_missing()
        self.refresh()
        self.library_updated.emit()
        set_ui_text(self.status_label, f"Removed {removed} missing file record(s).")

    def clean_thumbnail_cache(self) -> None:
        removed = self.library.cleanup_thumbnail_cache()
        set_ui_text(self.status_label, f"Removed {removed} unused thumbnail(s).")

    def clear_library(self) -> None:
        answer = QMessageBox.question(
            self,
            ui_text("Clear media library"),
            (
                "Remove every indexed folder and clip from the media library?\n\n"
                "This does NOT delete original source videos. "
                "Clips already loaded into decks continue playing."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        removed = self.library.clear_index()
        self.refresh()
        self.library_updated.emit()
        set_ui_text(
            self.status_label,
            f"Library cleared · removed {removed} index record(s). Source files were kept.",
        )

    def shutdown_workers(self) -> None:
        """Stop queued background work and give active workers a bounded exit window."""
        self._scan_queue.clear()
        self._thumbnail_queue.clear()
        self.scan_pool.clear()
        self.thumbnail_pool.clear()
        scan_stopped = self.scan_pool.waitForDone(2000)
        thumbnails_stopped = self.thumbnail_pool.waitForDone(2000)
        if not scan_stopped or not thumbnails_stopped:
            _LOG.warning(
                "Media workers did not all stop before shutdown "
                "(scan=%s, thumbnails=%s)",
                scan_stopped,
                thumbnails_stopped,
            )

    def assign_item(self, item: QListWidgetItem) -> None:
        asset = item.data(Qt.ItemDataRole.UserRole)
        if asset is not None:
            self.assign_requested.emit(asset, str(self.deck_combo.currentData()))
