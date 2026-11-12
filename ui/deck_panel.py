from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from media.models import MediaAsset


def _format_time(seconds: float | None) -> str:
    if seconds is None:
        return "--:--"
    value = max(0.0, float(seconds))
    minutes = int(value // 60)
    whole_seconds = value % 60
    return f"{minutes:02d}:{whole_seconds:04.1f}"


class DeckCard(QGroupBox):
    action_requested = Signal(str, str)
    lock_changed = Signal(str, bool)
    loop_changed = Signal(str, bool)

    def __init__(self, deck_id: str, title: str, parent=None) -> None:
        super().__init__(title, parent)
        self.deck_id = deck_id
        self._thumbnail_source: str | None = None
        self._held = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        identity = QHBoxLayout()
        self.thumbnail_label = QLabel("NO THUMBNAIL")
        self.thumbnail_label.setObjectName("deckThumbnail")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setFixedSize(104, 58)
        identity.addWidget(self.thumbnail_label, 0)

        details = QVBoxLayout()
        details.setSpacing(2)
        self.file_label = QLabel("No video loaded")
        self.file_label.setWordWrap(True)
        self.file_label.setMinimumWidth(100)
        self.file_label.setObjectName("deckClipName")
        self.state_label = QLabel("EMPTY")
        self.state_label.setObjectName("mutedLabel")
        self.detail_label = QLabel("Load a clip from the Media Library")
        self.detail_label.setWordWrap(True)
        self.detail_label.setObjectName("mutedLabel")
        details.addWidget(self.file_label)
        details.addWidget(self.state_label)
        details.addWidget(self.detail_label)
        details.addStretch(1)
        identity.addLayout(details, 1)
        layout.addLayout(identity)

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.position_label = QLabel("--:-- / --:--")
        self.position_label.setObjectName("mutedLabel")
        self.position_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.position_label, 0)
        layout.addLayout(progress_row)

        controls = QHBoxLayout()
        controls.setSpacing(4)
        self.play_button = QPushButton("PLAY")
        self.pause_button = QPushButton("PAUSE")
        self.hold_button = QPushButton("HOLD")
        self.restart_button = QPushButton("RESTART")
        self.stop_button = QPushButton("STOP")
        self.play_button.setToolTip("Start or resume this deck")
        self.pause_button.setToolTip("Pause playback at the current position")
        self.hold_button.setToolTip("Freeze the currently presented frame")
        self.restart_button.setToolTip("Restart playback from the segment in-point")
        self.stop_button.setToolTip("Stop playback and clear the displayed frame")
        self.play_button.clicked.connect(
            lambda: self.action_requested.emit(deck_id, "play")
        )
        self.pause_button.clicked.connect(
            lambda: self.action_requested.emit(deck_id, "pause")
        )
        self.hold_button.clicked.connect(self._toggle_hold)
        self.restart_button.clicked.connect(
            lambda: self.action_requested.emit(deck_id, "restart")
        )
        self.stop_button.clicked.connect(
            lambda: self.action_requested.emit(deck_id, "stop")
        )
        for button in (
                self.play_button,
                self.pause_button,
                self.hold_button,
                self.restart_button,
                self.stop_button,
        ):
            controls.addWidget(button, 1)
        layout.addLayout(controls)

        options = QHBoxLayout()
        self.loop_checkbox = QCheckBox("Loop")
        self.loop_checkbox.setChecked(True)
        self.loop_checkbox.toggled.connect(
            lambda checked: self.loop_changed.emit(deck_id, checked)
        )
        self.lock_checkbox = QCheckBox("Lock")
        self.lock_checkbox.setToolTip(
            "Protect this deck from autonomous source replacement"
        )
        self.lock_checkbox.toggled.connect(
            lambda checked: self.lock_changed.emit(deck_id, checked)
        )
        options.addWidget(self.loop_checkbox)
        options.addWidget(self.lock_checkbox)
        options.addStretch(1)
        layout.addLayout(options)

    def _toggle_hold(self) -> None:
        self.action_requested.emit(
            self.deck_id,
            "release_hold" if self._held else "hold",
        )

    def _set_thumbnail(self, thumbnail_path: str | None) -> None:
        source = str(thumbnail_path) if thumbnail_path else None
        if source == self._thumbnail_source:
            return
        self._thumbnail_source = source
        pixmap = QPixmap(source) if source else QPixmap()
        if pixmap.isNull():
            self.thumbnail_label.setPixmap(QPixmap())
            self.thumbnail_label.setText("NO THUMBNAIL")
            return
        self.thumbnail_label.setText("")
        self.thumbnail_label.setPixmap(
            pixmap.scaled(
                self.thumbnail_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def update_state(
            self,
            path: str | None,
            playing: bool,
            paused: bool,
            held: bool,
            error: str | None,
            loop: bool,
            locked: bool,
            position_seconds: float,
            duration_seconds: float | None,
            asset: MediaAsset | None,
            has_frame: bool,
            layer_name: str | None,
    ) -> None:
        self.file_label.setText(
            asset.name if asset else (Path(path).name if path else "No video loaded")
        )
        self._held = bool(held)
        if error:
            state = f"ERROR · {error}"
        elif held:
            state = "HELD · FRAME FROZEN"
        elif playing:
            state = "PLAYING"
        elif paused:
            state = "PAUSED"
        elif path:
            state = "STOPPED / READY"
        else:
            state = "EMPTY"
        self.state_label.setText(state)

        details = [f"LAYER · {layer_name}"] if layer_name else ["LAYER · NOT ATTACHED"]
        if asset:
            if asset.width and asset.height:
                details.append(f"{asset.width}×{asset.height}")
            if asset.fps:
                details.append(f"{asset.fps:.2f} fps")
            if asset.codec:
                details.append(str(asset.codec).upper())
            self._set_thumbnail(asset.thumbnail_path)
        else:
            if path:
                details.append(str(path))
            else:
                details.append("Load a clip from the Media Library")
            self._set_thumbnail(None)
        self.detail_label.setText(" · ".join(details))

        duration = (
            max(0.0, float(duration_seconds))
            if duration_seconds is not None and float(duration_seconds) > 0
            else None
        )
        position = max(0.0, float(position_seconds))
        if duration is not None:
            maximum = max(1, int(round(duration * 10)))
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(min(maximum, int(round(position * 10))))
            self.progress_bar.setEnabled(True)
        else:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            self.progress_bar.setEnabled(False)
        self.position_label.setText(
            f"{_format_time(position)} / {_format_time(duration)}"
        )

        loaded = bool(path)
        self.play_button.setEnabled(loaded)
        self.pause_button.setEnabled(bool(playing))
        self.hold_button.setEnabled(bool(loaded and has_frame))
        self.hold_button.setText("UNHOLD" if held else "HOLD")
        self.restart_button.setEnabled(loaded)
        self.stop_button.setEnabled(loaded)

        self.loop_checkbox.blockSignals(True)
        self.loop_checkbox.setChecked(loop)
        self.loop_checkbox.blockSignals(False)
        self.lock_checkbox.blockSignals(True)
        self.lock_checkbox.setChecked(locked)
        self.lock_checkbox.blockSignals(False)


class DeckPanel(QWidget):
    action_requested = Signal(str, str)
    lock_changed = Signal(str, bool)
    loop_changed = Signal(str, bool)

    def __init__(self, application: Application, parent=None) -> None:
        super().__init__(parent)
        self.application = application
        self._asset_ids: dict[str, str | None] = {}
        self._asset_cache: dict[str, MediaAsset | None] = {}
        self._asset_cache_refresh_at = 0.0
        layout = QGridLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(6)
        self.cards: dict[str, DeckCard] = {}
        titles = {
            "deck_a": "VIDEO DECK A",
            "deck_b": "VIDEO DECK B",
            "deck_c": "VIDEO DECK C",
            "deck_d": "VIDEO DECK D",
        }
        for index, (deck_id, deck) in enumerate(application.decks.items()):
            card = DeckCard(deck_id, titles.get(deck_id, deck_id.upper()))
            card.action_requested.connect(self.action_requested)
            card.lock_changed.connect(self._on_lock)
            card.loop_changed.connect(self.loop_changed)
            self.cards[deck_id] = card
            layout.addWidget(card, 0, index)
            card.lock_checkbox.setChecked(deck.locked)
            card.loop_checkbox.setChecked(deck.loop)
        self.refresh()

    def _on_lock(self, deck_id: str, locked: bool) -> None:
        self.application.decks[deck_id].locked = locked
        self.lock_changed.emit(deck_id, locked)

    def _asset_for_deck(
            self,
            deck_id: str,
            asset_id: str | None,
            refresh_cache: bool = False,
    ) -> MediaAsset | None:
        if refresh_cache or self._asset_ids.get(deck_id) != asset_id:
            self._asset_ids[deck_id] = asset_id
            self._asset_cache[deck_id] = (
                self.application.media_library.get_asset(asset_id)
                if asset_id else None
            )
        return self._asset_cache.get(deck_id)

    def refresh(self) -> None:
        refresh_assets = time.monotonic() >= self._asset_cache_refresh_at
        if refresh_assets:
            self._asset_cache_refresh_at = time.monotonic() + 2.0
        for deck_id, deck in self.application.decks.items():
            asset = self._asset_for_deck(deck_id, deck.asset_id, refresh_assets)
            frame = deck.current_frame
            position = frame.timestamp if frame is not None else deck.segment_start
            duration = (
                asset.duration if asset and asset.duration
                else deck.segment_end
            )
            source_layer = next(
                (
                    layer for layer in self.application.composition.layers
                    if layer.source_type == "video" and layer.source_id == deck_id
                ),
                None,
            )
            self.cards[deck_id].update_state(
                path=deck.path,
                playing=deck.is_playing,
                paused=deck.is_paused,
                held=deck.is_held,
                error=deck.error,
                loop=deck.loop,
                locked=deck.locked,
                position_seconds=position,
                duration_seconds=duration,
                asset=asset,
                has_frame=frame is not None,
                layer_name=source_layer.name if source_layer else None,
            )
