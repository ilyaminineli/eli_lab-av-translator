from __future__ import annotations

import json
import logging
import random
import tempfile
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from config import RESOURCE_DIR, VIDEO_DECK_IDS
from core.audio_analysis import AudioAnalysisFrame, AudioAnalysisSettings
from core.audio_capture import AudioCaptureService
from core.automation import AutomationDirector, AutomationSettings
from core.composition import Composition, Layer
from core.event_bus import EventBus
from core.layer_manager import LayerManager
from core.modulation import TARGET_SPECS, ModulationMatrix
from core.modulator_bank import (
    ModulatorBank,
    ModulatorBankEngine,
    ModulatorDefinition,
)
from core.osc_protocol import OSCReceiver
from core.performance_control import ControlEvent, ControlEventQueue, PerformanceControlState
from core.performance_environment import (
    MIDIInputService,
    MIDIMapping,
    MIDIMappingEngine,
    PerformanceScene,
    PerformanceSetStore,
    SceneMorph,
)
from core.performance_manager import PerformanceManager
from core.performance_modifiers import (
    LayerPerformanceModifier,
    LayerPerformanceModifierEngine,
)
from core.performance_service import (
    PerformanceModePlan,
    PerformanceModeService,
    install_default_layer_modifiers,
    install_default_matrix_routes,
    install_default_modulators,
    set_default_routing_enabled,
)
from core.performance_transport import InternalTransport, Quantization
from core.project_manager import ProjectManager
from core.scene_profiles import SceneProfile, SceneProfileRegistry
from effects.layer_settings import normalize_layer_effects
from effects.settings import EffectSettings
from generators.catalog import GENERATOR_TYPES, default_generator_settings, normalize_settings
from generators.palettes import palette_look, palette_names
from media.asset_index import VisualAssetIndex
from media.frame_queue import FrameSnapshot
from media.image_overlay import ImageOverlayPlayer
from media.library import MediaLibrary
from media.scanner import SUPPORTED_VIDEO_EXTENSIONS
from media.video_deck import VideoDeck

_LOG = logging.getLogger(__name__)

_SELECTED_LAYER_MODULATION_TARGETS = (
    "selected_layer.opacity",
    "selected_layer.rotation",
    "selected_layer.scale",
    "selected_layer.position_x",
    "selected_layer.position_y",
    "generator.animation_speed",
    "generator.animation_amount",
    "generator.density",
    "generator.rotation",
    "generator.text_animation_speed",
    "generator.text_animation_amount",
    "generator.text_animation_columns",
    "generator.font_size",
    "generator.letter_spacing",
    "generator.waveform_amplitude",
    "generator.waveform_frequency",
    "generator.particle_speed",
    "generator.particle_size",
    "generator.particle_spread",
    "generator.particle_trail",
    "generator.particle_emission_rate",
    "generator.particle_system_size",
    "generator.particle_lifetime",
    "generator.particle_turbulence",
    "generator.particle_force_strength",
    "generator.particle_reform_strength",
    "layer_fx.mix",
    "layer_fx.monochrome",
    "layer_fx.threshold",
    "layer_fx.contrast",
    "layer_fx.brightness",
    "layer_fx.chromatic",
    "layer_fx.scanlines",
    "layer_fx.posterize",
    "layer_fx.invert",
    "layer_fx.hue",
    "layer_fx.saturation",
    "overlay.playback_speed",
    "overlay.frame_hold",
)

_MASTER_MODULATION_FIELDS = frozenset({
    "brightness", "exposure", "contrast", "saturation", "gamma",
    "temperature", "tint", "hue", "vignette", "grain", "scanlines",
    "chromatic", "glitch", "pixelate", "posterize", "invert", "halftone",
    "solarize", "transform_mix", "kaleidoscope_slices",
    "kaleidoscope_rotation", "kaleidoscope_zoom", "mosaic_tiles",
    "pixel_sort_amount", "pixel_sort_threshold", "edge_amount", "dither",
    "displacement_amount", "displacement_scale", "feedback_amount",
    "feedback_decay", "feedback_zoom", "feedback_rotation",
    "feedback_translate_x", "feedback_translate_y", "feedback_color_shift",
    "feedback_distortion", "feedback_motion_warp", "feedback_datamosh",
    "feedback_delay_frames",
})


class Application:
    """Coordinates application services without depending on Qt widgets."""

    def __init__(self) -> None:
        from generators.raster_service import GeneratorRasterService

        self.generator_raster_service = GeneratorRasterService()
        self.events = EventBus()
        self.control_events = ControlEventQueue()
        self.osc_receiver = OSCReceiver(self.submit_control_event)
        self.performance_control = PerformanceControlState()
        self.performance_mode = PerformanceModeService()
        self._performance_automation_settings: AutomationSettings | None = None
        self._performance_automation_duration: float | None = None
        self._performance_automation_armed = False
        self._performance_automation_owned = False
        self.midi_mapping_engine = MIDIMappingEngine()
        self._midi_learn_request: dict[str, Any] | None = None
        self._midi_learn_last_event = ""
        self.performance_scenes: dict[str, PerformanceScene] = {}
        self._pending_scene_morph_seconds: dict[str, float] = {}
        self._pending_external_scene_recall: dict[str, dict[str, float]] = {}
        self._active_scene_morph: SceneMorph | None = None
        self._midi_scene_trigger_state: dict[str, bool] = {}
        self.midi_input = MIDIInputService(self._handle_midi_event)
        self.transport = InternalTransport()
        self._external_clock_bar_at: float | None = None
        self.scene_profiles = SceneProfileRegistry()
        self.active_palette = palette_names()[0]
        self.modulation = ModulationMatrix()
        self.modulator_bank = ModulatorBank()
        self.modulator_bank_engine = ModulatorBankEngine()
        self.performance_modifier_engine = LayerPerformanceModifierEngine()
        self.audio_capture = AudioCaptureService()
        self._audio_sources: dict[str, float] = {}
        self._latest_audio_frame: AudioAnalysisFrame | None = None
        self._audio_last_received_at = 0.0
        self._selected_layer_id: str | None = None
        self._modulation_base_values: dict[str, float] = {}
        self._animation_started_at = time.perf_counter()
        self.project_manager = ProjectManager()
        self.media_library = MediaLibrary()
        texture_root = RESOURCE_DIR / "textures"
        sketch_root = RESOURCE_DIR / "sketches_and_strokes"
        self.visual_asset_index = VisualAssetIndex([texture_root, sketch_root])
        # Built-in and user assets are indexed lazily when the asset-library dock opens.
        self.performance_manager = PerformanceManager()
        self.automation = AutomationDirector()
        self.automation.generator_settings_changed = self._request_generator_raster
        self.effects = EffectSettings()
        self.decks: dict[str, VideoDeck] = {
            deck_id: VideoDeck(deck_id) for deck_id in VIDEO_DECK_IDS
        }
        self._frame_snapshots: dict[str, FrameSnapshot] = {}
        self._overlay_frames: dict[str, FrameSnapshot] = {}
        self._overlay_started_at: dict[str, float] = {}
        self._overlay_images: dict[str, ImageOverlayPlayer] = {}
        self._overlay_videos: dict[str, VideoDeck] = {}
        self._automation_collection_id: str | None = None
        self.composition = Composition()
        self.layer_manager = LayerManager(self.composition, self.events)
        self._create_default_layers()
        self.current_project_path: Path | None = None
        self.window: Any | None = None

    def _request_generator_raster(self, layer: Layer) -> None:
        """Advance the shared render revision after a live generator mutation."""
        if layer.source_type != "generator" or not layer.generator_type:
            return
        if layer.generator_type in {"particles", "particle_system_2"}:
            return
        settings = dict(layer.generator_settings)
        if self.generator_raster_service.has_latest_snapshot(
                layer.id, layer.generator_type, settings
        ):
            return
        self.generator_raster_service.request(
            layer.id,
            layer.generator_type,
            settings,
        )

    def _create_default_layers(self) -> None:
        positions = ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75))
        for index, deck_id in enumerate(VIDEO_DECK_IDS):
            self.composition.add_layer(
                Layer(
                    id=f"layer_{deck_id}",
                    name=f"Video {deck_id[-1].upper()}",
                    source_type="video",
                    source_id=deck_id,
                    visible=True,
                    position=positions[index],
                    scale=(0.5, 0.5),
                    z_index=index,
                )
            )

    def animation_time(self) -> float:
        return max(0.0, time.perf_counter() - self._animation_started_at)

    def set_window(self, window: Any) -> None:
        self.window = window

    def add_generator_layer(self, generator_type: str) -> Layer:
        if generator_type not in GENERATOR_TYPES:
            raise ValueError(f"Unknown generator type: {generator_type}")
        labels = {
            "geometry": "Geometry Generator",
            "text": "Text Art",
            "waveform": "Waveform Generator",
            "particles": "Particle Field",
            "particle_system_2": "Particle System 2.0",
        }
        blend_modes = {
            "geometry": "screen",
            "text": "normal",
            "waveform": "screen",
            "particles": "screen",
            "particle_system_2": "screen",
        }
        layer = self.layer_manager.create_layer(
            name=labels[generator_type],
            source_type="generator",
            generator_type=generator_type,
            generator_settings=default_generator_settings(generator_type),
            blend_mode=blend_modes[generator_type],
            position=(0.5, 0.5),
            scale=(1.0, 1.0),
            z_index=max(
                (item.z_index for item in self.composition.layers),
                default=-1,
            ) + 1,
        )
        layer.source_id = f"generator:{layer.id}"
        self.events.publish("generator.added", layer=layer)
        return layer

    def add_visual_asset_root(self, path: str | Path) -> int:
        root = Path(path).expanduser().resolve()
        if not root.is_dir():
            raise NotADirectoryError(root)
        if root not in self.visual_asset_index.roots:
            self.visual_asset_index.roots.append(root)
        return len(self.visual_asset_index.roots)

    def search_visual_assets(self, query: str = "", purpose: str | None = None,
                             kind: str | None = None, category: str | None = None):
        return self.visual_asset_index.search(query, purpose, kind, category)

    def add_library_asset_overlay(self, asset_id: str) -> Layer:
        asset = next((item for item in self.visual_asset_index.assets if item.id == asset_id), None)
        if asset is None:
            raise KeyError(f"Unknown visual asset: {asset_id}")
        return self.add_media_overlay(asset.path)

    def add_media_overlay(self, path: str | Path) -> Layer:
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        layer_id = uuid4().hex
        suffix = source.suffix.lower()
        kind = "video" if suffix in SUPPORTED_VIDEO_EXTENSIONS else "image"
        layer = self.layer_manager.create_layer(
            id=layer_id,
            name=f"Overlay · {source.stem}",
            source_type="overlay",
            source_id=f"overlay:{layer_id}",
            overlay_path=str(source),
            overlay_kind=kind,
            blend_mode="normal",
            position=(0.5, 0.5),
            scale=(1.0, 1.0),
            z_index=max(
                (item.z_index for item in self.composition.layers),
                default=-1,
            ) + 1,
        )
        try:
            self._attach_overlay_layer(layer)
        except Exception:
            self.layer_manager.remove_layer(layer.id)
            raise
        self.events.publish("overlay.added", layer=layer)
        return layer

    def _attach_overlay_layer(self, layer: Layer) -> None:
        if not layer.overlay_path:
            raise ValueError(f"Overlay layer {layer.name} has no media path.")
        source = Path(layer.overlay_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        kind = layer.overlay_kind or (
            "video" if source.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS else "image"
        )
        layer.overlay_kind = kind
        layer.source_type = "overlay"
        import time
        self._overlay_started_at[layer.id] = time.perf_counter()
        layer.source_id = f"overlay:{layer.id}"
        if kind == "video":
            deck = VideoDeck(
                f"overlay_{layer.id}"
            )
            deck.load(source, loop=layer.overlay_loop)
            self._overlay_videos[layer.id] = deck
            self._overlay_frames.pop(layer.id, None)
        else:
            player = ImageOverlayPlayer(
                source,
                speed=layer.overlay_speed,
                frame_hold=layer.overlay_frame_hold,
                loop=layer.overlay_loop,
            )
            self._overlay_images[layer.id] = player
            self._overlay_frames[layer.id] = FrameSnapshot(
                player.revision,
                player.frame,
            )

    def _remove_overlay_runtime(self, layer_id: str) -> None:
        player = self._overlay_images.pop(layer_id, None)
        if player is not None:
            player.close()
        deck = self._overlay_videos.pop(layer_id, None)
        if deck is not None:
            deck.close()
        self._overlay_frames.pop(layer_id, None)
        self._overlay_started_at.pop(layer_id, None)

    def _clear_overlays(self) -> None:
        for layer_id in tuple(self._overlay_images):
            self._remove_overlay_runtime(layer_id)
        for layer_id in tuple(self._overlay_videos):
            self._remove_overlay_runtime(layer_id)
        self._overlay_frames.clear()

    def remove_layer(self, layer_id: str) -> bool:
        self.generator_raster_service.invalidate(layer_id)
        layer = self.composition.get_layer(layer_id)
        if layer is not None and layer.source_type == "overlay":
            self._remove_overlay_runtime(layer_id)
        modifier_engine = getattr(self, "performance_modifier_engine", None)
        if modifier_engine is not None:
            modifier_engine.clear_layer(layer_id)
        return self.layer_manager.remove_layer(layer_id)

    def reset_project(self) -> None:
        if self.performance_mode.enabled:
            self.stop_performance_mode()
        self.automation.stop()
        self.midi_mapping_engine.load_dict([])
        self._midi_learn_request = None
        self._midi_learn_last_event = ""
        self.performance_scenes.clear()
        self._pending_scene_morph_seconds.clear()
        self._pending_external_scene_recall.clear()
        self._active_scene_morph = None
        self._midi_scene_trigger_state.clear()
        self._clear_overlays()
        for deck in self.decks.values():
            deck.close()
            deck.locked = False
            deck.set_loop(True)
        self._frame_snapshots.clear()
        self.generator_raster_service.invalidate_missing(set())
        self.composition = Composition()
        self.layer_manager = LayerManager(self.composition, self.events)
        self._create_default_layers()
        self.effects.reset()
        self.control_events.clear()
        self.performance_control.reset()
        self.transport.stop()
        self.transport.load_settings({
            "bpm": 120.0,
            "beats_per_bar": 4,
            "phrase_bars": 4,
        })
        self.modulation.load_dict([])
        self.modulator_bank = ModulatorBank()
        self.modulator_bank_engine.reset()
        self.performance_modifier_engine.reset()
        self.scene_profiles = SceneProfileRegistry()
        self.active_palette = palette_names()[0]
        self.audio_capture.stop()
        self.audio_capture.update_settings(AudioAnalysisSettings())
        self._audio_sources.clear()
        self._latest_audio_frame = None
        self._external_clock_bar_at = None
        self._modulation_base_values.clear()
        self._selected_layer_id = None
        self.current_project_path = None
        self.events.publish("project.reset")

    def assign_media_to_deck(self, asset: object, deck_id: str) -> None:
        if deck_id not in self.decks:
            raise KeyError(f"Unknown video deck: {deck_id}")
        deck = self.decks[deck_id]
        deck.load(
            str(getattr(asset, "path")),
            asset_id=str(getattr(asset, "id")),
            collection_id=str(getattr(asset, "collection_id")),
        )
        self._frame_snapshots.pop(deck_id, None)
        self.events.publish("deck.loaded", deck_id=deck_id, asset=asset)

    def refresh_frames(self) -> bool:
        changed = False
        for deck_id, deck in self.decks.items():
            if deck.consume_latest_frame() is not None:
                snapshot = deck.snapshot_frame()
                if snapshot is not None:
                    self._frame_snapshots[deck_id] = snapshot
                changed = True
            elif deck.current_frame is None:
                self._frame_snapshots.pop(deck_id, None)

        for layer_id, deck in self._overlay_videos.items():
            if deck.consume_latest_frame() is not None:
                snapshot = deck.snapshot_frame()
                if snapshot is not None:
                    self._overlay_frames[layer_id] = snapshot
                changed = True
            elif deck.current_frame is None:
                self._overlay_frames.pop(layer_id, None)

        for layer_id, player in self._overlay_images.items():
            layer = self.composition.get_layer(layer_id)
            if layer is not None:
                player.configure_playback(
                    layer.overlay_speed,
                    layer.overlay_frame_hold,
                    layer.overlay_loop,
                )
            frame = player.update()
            if frame is not None:
                self._overlay_frames[layer_id] = FrameSnapshot(
                    player.revision,
                    frame,
                )
                changed = True
        return changed

    def current_frames(self) -> dict[str, FrameSnapshot]:
        # Both outputs consume the same CPU snapshots; each owns separate GL textures.
        frames = dict(self._frame_snapshots)
        import time
        now = time.perf_counter()
        for layer_id, snapshot in self._overlay_frames.items():
            layer = self.composition.get_layer(layer_id)
            started = self._overlay_started_at.get(layer_id, now)
            if layer is None:
                continue
            elapsed = now - started
            if elapsed < layer.overlay_in:
                continue
            if layer.overlay_out is not None and elapsed >= layer.overlay_out:
                continue
            frames[f"overlay:{layer_id}"] = snapshot
        return frames

    def performance_diagnostics(self) -> dict[str, Any]:
        """Unified non-blocking diagnostics for the operator performance surface."""
        osc = self.osc_receiver.snapshot()
        audio_state = self.audio_capture.state.value
        route_outputs = self.modulation.outputs()
        modifiers = [
            raw
            for layer in self.composition.layers
            for raw in layer.performance_modifiers
            if isinstance(raw, dict)
        ]
        return {
            "mode": self.performance_mode.snapshot(),
            "osc": {
                "status": osc.get("status"),
                "last_message_age": osc.get("last_message_age"),
                "received": osc.get("received", 0),
                "accepted": osc.get("accepted", 0),
                "rejected": osc.get("rejected", 0),
                "dropped": osc.get("dropped", 0),
            },
            "audio": {
                "state": audio_state,
                "source": self.audio_capture.source_kind,
                "name": self.audio_capture.selected_device_name,
                "error": self.audio_capture.error,
                "queue_depth": len(self.audio_capture.frames),
                "dropped_frames": self.audio_capture.frames.dropped,
                "last_frame_age": (
                    max(0.0, time.monotonic() - self._audio_last_received_at)
                    if self._audio_last_received_at else None
                ),
            },
            "control": {
                "queue_depth": len(self.control_events),
                "dropped_events": self.control_events.dropped_events,
                "enabled_routes": sum(route.enabled for route in self.modulation.routes),
                "total_routes": len(self.modulation.routes),
                "active_outputs": len(route_outputs),
                "modulators": len(self.modulator_bank.list_modulators()),
                "active_modulators": len(self.modulator_bank_engine.live_values()),
                "layer_modifiers": len(modifiers),
                "enabled_layer_modifiers": sum(
                    bool(item.get("enabled", True)) for item in modifiers
                ),
            },
            "automation": {
                "running": self.automation.running,
                "last_action": self.automation.last_action,
                "style": self.automation.settings.performance_style,
                "musical_sync": self.automation.settings.musical_sync,
                "bar_index": self.automation._performance_bar_index,
                "section": self.automation._performance_section,
                "energy": self.automation._performance_energy,
                "cutoff": self.automation._performance_cutoff,
            },
            "video": self.performance_snapshot(),
        }

    def _monitor_performance_mode(self) -> None:
        if not self.performance_mode.enabled:
            return
        osc = self.osc_receiver.snapshot()
        state = self.performance_mode.snapshot_state
        if not osc.get("running"):
            if state.phase != "degraded":
                self.performance_mode.mark_degraded(
                    "Sonic Pi receiver unavailable",
                    str(osc.get("last_error") or "OSC receiver stopped"),
                )
        elif osc.get("status") == "STALE" and state.phase == "live":
            self.performance_mode.mark_waiting("Sonic Pi signal stale")
        audio_state = self.audio_capture.state.value
        if audio_state in {"device_lost", "error"}:
            state.audio_status = f"{audio_state} · Sonic Pi macros continue"
        elif state.audio_owned and audio_state == "running":
            state.audio_status = self.audio_capture.selected_device_name or "audio input"

    def performance_snapshot(self) -> dict[str, int | float]:
        deck_stats = [deck.performance_stats() for deck in self.decks.values()]
        deck_stats.extend(
            deck.performance_stats() for deck in self._overlay_videos.values()
        )
        return {
            "playing_decks": sum(bool(item["playing"]) for item in deck_stats),
            "queue_depth": sum(int(item["queue_depth"]) for item in deck_stats),
            "dropped_frames": sum(int(item["dropped_frames"]) for item in deck_stats),
            "retired_workers": sum(int(item["retired_workers"]) for item in deck_stats),
            "published_frames": sum(int(item["published_frames"]) for item in deck_stats),
            "decoded_frames": sum(int(item["decoded_frames"]) for item in deck_stats),
            "decode_time_ms": sum(float(item["decode_time_ms"]) for item in deck_stats),
            "conversion_time_ms": sum(
                float(item["conversion_time_ms"]) for item in deck_stats
            ),
            "skipped_output_frames": sum(
                int(item["skipped_output_frames"]) for item in deck_stats
            ),
        }

    def start_automation(
            self,
            collection_id: str | None = None,
            settings: AutomationSettings | None = None,
            duration_seconds: float | None = 1800.0,
    ) -> int:
        assets = self.media_library.list_assets(collection_id=collection_id)
        loaded = self.automation.start(
            assets,
            self.decks,
            self.composition.layers,
            self.effects,
            settings=settings,
            duration_seconds=duration_seconds,
        )
        self._automation_collection_id = collection_id
        self._frame_snapshots.clear()
        self.events.publish("automation.started", decks=loaded)
        return loaded

    def refresh_automation_media_pool(self) -> bool:
        """Apply media-library changes to Auto Mode without cutting current clips."""
        if not self.automation.running:
            return False
        assets = self.media_library.list_assets(
            collection_id=self._automation_collection_id
        )
        self.automation.replace_assets(assets)
        self.events.publish("automation.media_pool_changed", count=len(assets))
        return True

    def start_osc_receiver(self, bind_address: str = "127.0.0.1", port: int = 57121) -> int:
        """Start the versioned Sonic Pi OSC ingress on a dedicated UDP port."""
        actual_port = self.osc_receiver.start(bind_address, port)
        self.events.publish("performance.osc.started", bind_address=bind_address, port=actual_port)
        return actual_port

    def stop_osc_receiver(self) -> bool:
        """Stop the OSC worker without changing the visual transport state."""
        stopped = self.osc_receiver.stop()
        if stopped:
            self.events.publish("performance.osc.stopped")
        return stopped

    def start_performance_mode(
            self,
            plan: PerformanceModePlan | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Arm audio, Sonic Pi ingress, shared curves and unattended automation."""
        if plan is None:
            plan = self.performance_mode.plan
        elif isinstance(plan, dict):
            plan = PerformanceModePlan(**plan)
        if not isinstance(plan, PerformanceModePlan):
            raise TypeError("Performance Mode requires a PerformanceModePlan.")
        self.performance_mode.begin(plan)
        errors: list[str] = []
        osc_owned = False
        audio_owned = False
        audio_status = "Sonic Pi macros only"

        try:
            receiver = self.osc_receiver.snapshot()
            if not receiver["running"]:
                self.start_osc_receiver(plan.osc_bind_address, plan.osc_port)
                osc_owned = True
            else:
                # Use the already-open receiver as the single source of truth.
                plan.osc_bind_address = str(receiver["bind_address"])
                plan.osc_port = int(receiver["port"])

            audio_device_id = plan.audio_device_id
            if not audio_device_id and plan.prefer_loopback and not plan.audio_test_signal:
                try:
                    audio_device_id = next(
                        (
                            device.id
                            for device in self.audio_capture.list_devices()
                            if device.is_loopback
                        ),
                        "",
                    )
                    if audio_device_id:
                        plan.audio_device_id = audio_device_id
                except Exception:
                    audio_device_id = ""
            if plan.audio_test_signal or audio_device_id:
                capture_state = self.audio_capture.state.value
                if capture_state in {"running", "starting"}:
                    audio_status = f"already active · {self.audio_capture.selected_device_name}"
                else:
                    try:
                        self.start_audio_capture(
                            device_id=audio_device_id or None,
                            test_signal=plan.audio_test_signal,
                        )
                        audio_owned = True
                        audio_status = self.audio_capture.selected_device_name or "audio input"
                    except Exception as exc:
                        # The visual show still operates from Sonic Pi energy/cutoff
                        # and transport if local loopback is unavailable.
                        audio_status = f"local capture unavailable · {exc} · Sonic Pi macros active"
                        self.events.publish("performance.mode.audio_fallback", error=str(exc))
            else:
                audio_status = "Sonic Pi macros only · no local audio capture"

            if plan.install_default_mappings:
                route_count = install_default_matrix_routes(self.modulation)
                modulator_ids = install_default_modulators(self.modulator_bank)
                modifier_count = install_default_layer_modifiers(
                    self.composition.layers,
                    modulator_ids,
                )
                set_default_routing_enabled(
                    self.modulation,
                    self.modulator_bank,
                    self.composition.layers,
                    True,
                )
                self.events.publish(
                    "performance.defaults.installed",
                    routes=route_count,
                    layer_modifiers=modifier_count,
                    modulators=len(modulator_ids),
                )

            settings_data = dict(plan.automation_settings)
            allowed = AutomationSettings.__dataclass_fields__
            settings = AutomationSettings(**{
                key: value for key, value in settings_data.items() if key in allowed
            })
            settings.normalize()
            self._performance_automation_settings = settings
            self._performance_automation_duration = plan.automation_duration_seconds
            self._performance_automation_armed = bool(plan.start_automation)

            self.performance_mode.mark_armed(
                osc_owned=osc_owned,
                audio_owned=audio_owned,
                audio_status=audio_status,
            )
            self.performance_mode.set_automation_armed(
                self._performance_automation_armed,
                self.automation.running,
            )
            live_receiver = self.osc_receiver.snapshot()
            if (
                    self.performance_control.source_id == "sonic_pi"
                    and self.performance_control.transport_running
                    and live_receiver.get("status") == "LIVE"
            ):
                self._activate_armed_performance_automation()
                self.performance_mode.mark_live(
                    "existing Sonic Pi transport",
                    self.osc_receiver.snapshot().get("active_session", ""),
                )
        except Exception as exc:
            errors.append(str(exc))
            self.performance_mode.mark_degraded("performance mode startup", "; ".join(errors))
            # A partial startup is recoverable. Keep the mode armed if the OSC
            # receiver is available; Stop Performance Mode owns the cleanup path.
            self.performance_mode.snapshot_state.osc_owned = osc_owned
            self.performance_mode.snapshot_state.audio_owned = audio_owned
            self.performance_mode.snapshot_state.audio_status = audio_status

        snapshot = self.performance_mode.snapshot()
        self.events.publish("performance.mode.changed", state=snapshot)
        return snapshot

    def _activate_armed_performance_automation(self) -> bool:
        if not self.performance_mode.enabled or not self._performance_automation_armed:
            return False
        if self.automation.running:
            self._performance_automation_armed = False
            self._performance_automation_owned = False
            self.performance_mode.set_automation_armed(False, True)
            return True
        settings = self._performance_automation_settings or AutomationSettings(
            performance_style="generative",
            musical_sync="phrase",
        )
        try:
            self.start_automation(
                collection_id=None,
                settings=settings,
                duration_seconds=self._performance_automation_duration,
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            self.performance_mode.mark_degraded(
                "AUTO PERFORMANCE could not start",
                str(exc),
            )
            self.performance_mode.set_automation_armed(False, False)
            self._performance_automation_armed = False
            return False
        self._performance_automation_armed = False
        self._performance_automation_owned = True
        self.performance_mode.set_automation_armed(False, True)
        self.events.publish("performance.mode.automation_started")
        return True

    def _automation_musical_context(
            self,
            sources: dict[str, float] | None = None,
    ) -> tuple[float, float]:
        values = self._modulation_sources() if sources is None else sources
        energy = max(
            float(values.get("macro.energy", 0.0)),
            float(values.get("audio.rms", 0.0)),
            float(values.get("audio.peak", 0.0)) * 0.85,
            float(values.get("audio.low", 0.0)) * 0.80,
            float(values.get("audio.onset", 0.0)) * 0.70,
        )
        cutoff = max(
            float(values.get("macro.cutoff", 0.0)),
            float(values.get("audio.high", 0.0)),
        )
        return max(0.0, min(1.0, energy)), max(0.0, min(1.0, cutoff))

    def _handle_performance_mode_event(self, event: ControlEvent) -> None:
        if event.source != "sonic_pi":
            return
        mode_active = self.performance_mode.enabled
        if not mode_active and not self.automation.running:
            return

        snapshot = self.osc_receiver.snapshot()
        session_id = event.session_id or str(snapshot.get("active_session", ""))
        if mode_active:
            self.performance_mode.note_event(event.kind, session_id)

        sources = self._modulation_sources()
        energy, cutoff = self._automation_musical_context(sources)
        self.automation.set_performance_context(
            energy=energy,
            cutoff=cutoff,
            intensity=float(self.performance_control.intensity),
            bar_index=int(self.performance_control.bar_index),
        )

        if mode_active and event.kind in {"transport.start", "clock.bar"}:
            self.performance_mode.mark_live(event.kind, session_id)
            self._activate_armed_performance_automation()

        # A manually started AUTO PERFORMANCE session can also subscribe to
        # SONATA cues; only the one-button mode owns receiver/audio lifecycle.
        if self.automation.running:
            if event.kind == "scene.select":
                self.automation.on_musical_event(
                    "scene",
                    scene_id=str(event.payload.get("scene_id", "")),
                    intensity=float(
                        event.payload.get(
                            "intensity",
                            self.performance_control.intensity,
                        )
                    ),
                    energy=energy,
                    cutoff=cutoff,
                    bar_index=int(
                        event.payload.get(
                            "bar_index",
                            self.performance_control.bar_index,
                        )
                    ),
                )
            elif event.kind == "clock.bar":
                self.automation.on_musical_event(
                    "bar",
                    intensity=float(self.performance_control.intensity),
                    energy=energy,
                    cutoff=cutoff,
                    bar_index=int(self.performance_control.bar_index),
                )
            elif event.kind == "cue.trigger":
                cue = str(event.payload.get("name", "")).lower()
                if cue == "phrase" or cue.startswith("phrase_"):
                    self.automation.on_musical_event(
                        "phrase",
                        intensity=float(self.performance_control.intensity),
                        energy=energy,
                        cutoff=cutoff,
                        bar_index=int(self.performance_control.bar_index),
                    )

        if mode_active:
            if event.kind == "transport.stop":
                if (
                        self.performance_mode.plan.stop_automation_on_patch_stop
                        and self._performance_automation_owned
                ):
                    self.stop_automation()
                # Keep the show armed for a SONATA restart. The next
                # transport/start or clock/bar event starts a fresh AUTO pass.
                self._performance_automation_armed = bool(
                    self.performance_mode.plan.start_automation
                )
                self.performance_mode.set_automation_armed(
                    self._performance_automation_armed,
                    self.automation.running,
                )
                self.performance_mode.mark_waiting("Sonic Pi transport stopped")
            elif event.kind in {"scene.select", "clock.bar", "cue.trigger"}:
                self.performance_mode.set_automation_armed(
                    self._performance_automation_armed,
                    self.automation.running,
                )

    def stop_performance_mode(self) -> dict[str, Any]:
        """Stop only services owned by the mode and restore modulation baselines."""
        if not self.performance_mode.enabled:
            return self.performance_mode.snapshot()
        previous = self.performance_mode.stop()
        self._performance_automation_armed = False
        self._performance_automation_settings = None
        self._performance_automation_duration = None
        if self._performance_automation_owned and self.automation.running:
            self.stop_automation()
        self._performance_automation_owned = False
        if previous.audio_owned:
            self.stop_audio_capture()
        if previous.osc_owned:
            self.stop_osc_receiver()
        self.transport.stop()
        self._external_clock_bar_at = None
        self.performance_control.reset()
        if previous.audio_owned:
            self._audio_sources.clear()
            self._latest_audio_frame = None
            self._audio_last_received_at = 0.0
        if self.performance_mode.plan.install_default_mappings:
            set_default_routing_enabled(
                self.modulation,
                self.modulator_bank,
                self.composition.layers,
                False,
            )
        # Disabled AUTO routes/modifiers release to their stored baselines on
        # this tick. User-authored routes and layer modifiers remain untouched.
        self.apply_modulation()
        self.events.publish("performance.mode.changed", state=self.performance_mode.snapshot())
        return self.performance_mode.snapshot()

    def performance_mode_snapshot(self) -> dict[str, Any]:
        return self.performance_mode.snapshot()

    def submit_control_event(self, event: ControlEvent) -> bool:
        """Submit a normalized event from an internal or future external source."""
        return self.control_events.submit(event)

    def process_control_events(self, max_events: int = 128) -> int:
        """Apply a bounded number of queued control events on the UI thread."""
        processed = 0
        for event in self.control_events.drain(max_events):
            try:
                if event.source == "sonic_pi" and event.kind == "transport.start":
                    # Sonic Pi is the clock authority while its session is active.
                    self.transport.stop()
                    self.transport.set_tempo(float(event.payload["bpm"]))
                    self.transport.set_meter(int(event.payload["beats_per_bar"]))
                    self._external_clock_bar_at = None
                elif event.source == "sonic_pi" and event.kind == "transport.tempo":
                    self.transport.set_tempo(float(event.payload["bpm"]))
                elif event.source == "midi" and event.kind == "transport.tempo":
                    self.transport.set_tempo(float(event.payload["bpm"]))
                    processed += 1
                elif event.source == "midi" and event.kind == "scene.intensity":
                    intensity = max(0.0, min(1.0, float(event.payload["intensity"])))
                    self.performance_control.intensity = intensity
                    self.events.publish("performance.scene.intensity", intensity=intensity)
                    processed += 1
                elif event.source == "sonic_pi" and event.kind == "clock.bar":
                    # A start datagram can be lost while a later bar still arrives.
                    # Treat the first bar as an authority hand-off too, so the
                    # internal test clock can never run alongside Sonic Pi.
                    self.transport.stop()
                    self.transport.set_tempo(float(event.payload["bpm"]))
                    self.transport.set_meter(int(event.payload["beats_per_bar"]))
                    self._external_clock_bar_at = event.received_at
                elif event.source == "sonic_pi" and event.kind == "transport.stop":
                    self.transport.stop()
                    self._external_clock_bar_at = None
                elif event.source != "sonic_pi" and event.kind == "transport.start":
                    self._external_clock_bar_at = None
                if self.performance_control.apply(event):
                    processed += 1
                    if event.kind == "scene.select":
                        scene_id = str(event.payload["scene_id"])
                        if scene_id in getattr(self, "performance_scenes", {}):
                            duration = getattr(self, "_pending_scene_morph_seconds", {}).pop(
                                scene_id, 0.0
                            )
                            self.recall_performance_scene(scene_id, morph_seconds=duration)
                        else:
                            self._activate_scene_profile(scene_id)
                    elif event.kind == "cue.trigger":
                        self.trigger_performance_scene_cue(str(event.payload.get("name", "")))
                    if event.kind in {"clock.beat", "clock.bar"}:
                        self._fire_due_external_scene_recall()
                    self._handle_performance_mode_event(event)
            except (TypeError, ValueError, KeyError) as exc:
                _LOG.warning(
                    "Rejected performance control event %s from %s: %s",
                    event.kind,
                    event.source,
                    exc,
                )
        if processed:
            self.events.publish(
                "performance.control.updated",
                state=self.performance_control.snapshot(),
                processed=processed,
            )
        return processed

    def start_internal_transport(
            self,
            bpm: float | None = None,
            beats_per_bar: int | None = None,
    ) -> None:
        if bpm is not None:
            self.transport.set_tempo(bpm)
        if beats_per_bar is not None:
            self.transport.set_meter(beats_per_bar)
        for event in self.transport.start():
            self.submit_control_event(event)
        self.process_control_events()

    def pause_internal_transport(self) -> None:
        for event in self.transport.pause():
            self.submit_control_event(event)
        self.process_control_events()

    def resume_internal_transport(self) -> None:
        for event in self.transport.resume():
            self.submit_control_event(event)
        self.process_control_events()

    def stop_internal_transport(self) -> None:
        for event in self.transport.stop():
            self.submit_control_event(event)
        self.process_control_events()

    def set_internal_tempo(self, bpm: float) -> None:
        self.transport.set_tempo(bpm)
        self.submit_control_event(ControlEvent(
            "transport.tempo",
            "internal",
            {"bpm": self.transport.bpm},
        ))
        self.process_control_events()

    def set_transport_meter(self, beats_per_bar: int) -> None:
        self.transport.set_meter(beats_per_bar)
        self.submit_control_event(ControlEvent(
            "transport.meter",
            "internal",
            {"beats_per_bar": self.transport.beats_per_bar},
        ))
        self.process_control_events()

    def request_scene_selection(
            self,
            scene_id: str,
            quantization: Quantization = "bar",
    ) -> None:
        profile = self.scene_profiles.get(scene_id)
        if not self.transport.running or self.transport.paused or quantization == "immediate":
            self.submit_control_event(ControlEvent(
                "scene.select",
                "internal",
                {
                    "scene_id": profile.scene_id,
                    "intensity": profile.intensity,
                    "bar_index": self.performance_control.bar_index,
                },
            ))
            self.process_control_events()
            return
        self.transport.schedule_scene(
            profile.scene_id,
            profile.intensity,
            quantization=quantization,
        )

    def update_scene_profile(self, profile: SceneProfile) -> None:
        self.scene_profiles.update(profile)
        self.events.publish("performance.scene_profiles.updated")

    def _activate_scene_profile(self, scene_id: str) -> None:
        profile = self.scene_profiles.get(scene_id)
        self.active_palette = profile.palette
        if profile.master_look:
            self.effects.apply_preset(profile.master_look)
        try:
            palette = palette_look(profile.palette)
        except KeyError:
            palette = None
        if palette:
            for layer in self.composition.layers:
                if layer.source_type != "generator" or not layer.generator_type:
                    continue
                values = dict(layer.generator_settings)
                for key in ("primary_color", "secondary_color", "background_color"):
                    if key in values and key in palette:
                        values[key] = palette[key]
                layer.generator_settings = normalize_settings(layer.generator_type, values)
                self._request_generator_raster(layer)
        self.events.publish(
            "performance.scene.activated",
            profile=profile.to_dict(),
            state=self.performance_control.snapshot(),
        )

    def set_layer_locked(self, layer_id: str, locked: bool) -> None:
        layer = self.composition.get_layer(layer_id)
        if layer is None or layer.locked == bool(locked):
            return
        target_ids = _SELECTED_LAYER_MODULATION_TARGETS
        if locked and layer_id == self._selected_layer_id:
            for target_id in target_ids:
                base = self._modulation_base_values.pop(target_id, None)
                if base is not None:
                    self._set_modulation_target(target_id, base)
                self.modulation.manual_override(target_id, 0.25)
        layer.locked = bool(locked)
        self.events.publish("layer.locked", layer_id=layer_id, locked=layer.locked)

    def set_selected_layer_id(self, layer_id: str | None) -> None:
        next_id = layer_id or None
        previous_id = self._selected_layer_id
        if next_id == previous_id:
            return
        target_ids = _SELECTED_LAYER_MODULATION_TARGETS
        if previous_id is not None:
            for target_id in target_ids:
                base = self._modulation_base_values.pop(target_id, None)
                if base is not None:
                    self._set_modulation_target(target_id, base)
                self.modulation.manual_override(target_id, 0.25)
        self._selected_layer_id = next_id

    def start_audio_capture(self, device_id: str | None = None, test_signal: bool = False) -> None:
        if test_signal:
            self.audio_capture.start_test_signal(self.transport.bpm)
        elif device_id:
            self.audio_capture.start(device_id)
        else:
            raise ValueError("Select an audio input or system-loopback device first.")
        self._audio_sources.clear()
        self._latest_audio_frame = None
        self._audio_last_received_at = 0.0
        self.events.publish(
            "audio.capture.started",
            source=self.audio_capture.source_kind,
            device=self.audio_capture.selected_device_name,
        )

    def start_audio_replay(
            self,
            samples,
            sample_rate: int,
            repeat: bool = False,
    ) -> None:
        self.audio_capture.start_replay(samples, sample_rate, repeat=repeat)
        self._audio_sources.clear()
        self._latest_audio_frame = None
        self._audio_last_received_at = 0.0

    def stop_audio_capture(self) -> bool:
        stopped = self.audio_capture.stop()
        self._audio_sources.clear()
        self._latest_audio_frame = None
        self._audio_last_received_at = 0.0
        self.events.publish("audio.capture.stopped", stopped=stopped)
        return stopped

    def update_audio_analysis_settings(self, settings: AudioAnalysisSettings) -> None:
        settings.normalize()
        self.audio_capture.update_settings(settings)

    def process_audio_frames(self, max_frames: int = 4) -> int:
        frames = self.audio_capture.drain_frames(max_frames)
        if not frames:
            return 0
        self._latest_audio_frame = frames[-1]
        self._audio_sources = self._latest_audio_frame.sources()
        self._audio_last_received_at = time.monotonic()
        self._audio_last_received_at = time.monotonic()
        self.events.publish(
            "audio.analysis.updated",
            features=self._audio_sources.copy(),
            source=self.audio_capture.source_kind,
        )
        return len(frames)

    def audio_analysis_snapshot(self) -> dict[str, float | str | None]:
        frame = self._latest_audio_frame
        if frame is None:
            return {
                "rms": 0.0,
                "low": 0.0,
                "mid": 0.0,
                "high": 0.0,
                "onset": 0.0,
                "bpm": None,
                "beat_confidence": 0.0,
            }
        return {
            "rms": frame.rms,
            "low": frame.low,
            "mid": frame.mid,
            "high": frame.high,
            "onset": frame.onset,
            "bpm": frame.bpm,
            "beat_confidence": frame.beat_confidence,
        }

    def _modulation_sources(self) -> dict[str, float]:
        values = dict(self._audio_sources)
        now = time.monotonic()
        if (
                self._audio_last_received_at <= 0.0
                or now - self._audio_last_received_at > 1.5
        ):
            values = {key: value for key, value in values.items()
                      if not key.startswith("audio.")}
        values["transport.intensity"] = self.performance_control.intensity
        external_clock_active = (
                self.performance_control.source_id == "sonic_pi"
                and self.performance_control.transport_running
                and self._external_clock_bar_at is not None
        )
        beat_index = 0
        beat_phase = 0.0
        bar_phase = 0.0
        clock_active = False
        phrase_bars = max(1, int(getattr(self.transport, "phrase_bars", 4)))
        beats_per_bar = max(1, int(self.performance_control.beats_per_bar))

        if external_clock_active:
            elapsed = max(0.0, time.monotonic() - self._external_clock_bar_at)
            beat_duration = 60.0 / max(20.0, self.performance_control.bpm)
            bar_duration = beat_duration * beats_per_bar
            fresh_for = max(5.0, bar_duration * 2.0)
            if elapsed <= fresh_for:
                clock_active = True
                beat_position = elapsed / beat_duration
                beat_index = int(beat_position) % beats_per_bar
                beat_phase = beat_position % 1.0
                bar_phase = (beat_index + beat_phase) / beats_per_bar
            else:
                external_clock_active = False

        if not external_clock_active:
            internal_running = self.transport.running and not self.transport.paused
            if internal_running:
                clock_active = True
                beat_phase = max(0.0, min(1.0, self.transport.phase))
                beat_index = int(self.transport.beat_index)
                beats_per_bar = max(1, int(self.transport.beats_per_bar))
                bar_phase = (beat_index + beat_phase) / beats_per_bar
                phrase_bars = max(1, int(self.transport.phrase_bars))
            else:
                beat_phase = 0.0
                beat_index = 0
                bar_phase = 0.0

        beat_pulse = max(0.0, 1.0 - beat_phase / 0.22) if clock_active else 0.0
        downbeat_pulse = beat_pulse if clock_active and beat_index == 0 else 0.0
        if external_clock_active:
            bar_index = max(1, int(self.performance_control.bar_index))
        elif self.transport.running and not self.transport.paused:
            bar_index = max(1, int(self.transport.bar_index))
        else:
            bar_index = 0
        phrase_start = (
                bar_index > 0
                and (bar_index - 1) % phrase_bars == 0
                and beat_index == 0
                and clock_active
        )
        phrase_pulse = beat_pulse if phrase_start else 0.0

        if clock_active:
            beat_position = (
                    max(0, bar_index - 1) * beats_per_bar
                    + beat_index
                    + beat_phase
            )
        else:
            beat_position = 0.0
        values["transport.running"] = 1.0 if clock_active else 0.0
        values["transport.beat_position"] = beat_position
        values["transport.beats_per_bar"] = float(beats_per_bar)
        values["transport.phrase_beats"] = float(
            max(1, phrase_bars) * max(1, beats_per_bar)
        )
        values["transport.phase"] = beat_phase
        values["transport.bar_phase"] = bar_phase
        values["transport.beat_pulse"] = beat_pulse
        values["transport.downbeat_pulse"] = downbeat_pulse
        values["transport.phrase_pulse"] = phrase_pulse

        # SONATA sends energy/cutoff once per bar. Keep those controls live
        # across the bar, but release them after the same bounded freshness
        # window as the external clock instead of holding a stale macro forever.
        macro_fresh_for = max(
            5.0,
            (60.0 / max(20.0, float(self.performance_control.bpm)))
            * max(1, beats_per_bar)
            * 2.0,
        )
        macro_timestamps = getattr(
            self.performance_control, "macro_updated_at", {}
        )
        for name, value in self.performance_control.macros.items():
            updated_at = macro_timestamps.get(name)
            if updated_at is None or now - float(updated_at) > macro_fresh_for:
                continue
            values[f"macro.{name}"] = value
        return values

    @staticmethod
    def _generator_modifier_setting_key(field: str) -> str | None:
        return {
            "animation_speed": "animation_speed",
            "animation_amount": "animation_amount",
            "density": "density",
            "rotation": "rotation",
            "text_animation_speed": "text_animation_speed",
            "text_animation_amount": "text_animation_amount",
            "font_size": "font_size",
            "letter_spacing": "letter_spacing",
            "waveform_amplitude": "amplitude",
            "waveform_frequency": "frequency",
            "particle_speed": "speed",
            "particle_size": "size",
            "particle_spread": "spread",
            "particle_trail": "trail",
            "text_animation_columns": "text_animation_columns",
            "particle_emission_rate": "emission_rate",
            "particle_system_size": "particle_size",
            "particle_lifetime": "lifetime",
            "particle_turbulence": "turbulence",
            "particle_force_strength": "force_strength",
            "particle_reform_strength": "reform_strength",
        }.get(field)

    def _get_layer_modifier_target(
            self,
            layer_id: str,
            target_id: str,
    ) -> float | None:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            return None
        if target_id.startswith("layer."):
            field = target_id.split(".", 1)[1]
            if field in {"opacity", "rotation"}:
                return float(getattr(layer, field))
            if field == "scale":
                return float(layer.scale[0])
            if field == "position_x":
                return float(layer.position[0])
            if field == "position_y":
                return float(layer.position[1])
            return None
        if target_id.startswith("layer_fx."):
            field = target_id.split(".", 1)[1]
            settings = normalize_layer_effects(layer.layer_effects)
            value = settings.get(field)
            return float(value) if isinstance(value, (int, float)) else None
        if target_id.startswith("generator."):
            if layer.source_type != "generator" or not layer.generator_type:
                return None
            field = target_id.split(".", 1)[1]
            setting_key = self._generator_modifier_setting_key(field)
            if setting_key is None:
                return None
            settings = normalize_settings(layer.generator_type, layer.generator_settings)
            value = settings.get(setting_key)
            return float(value) if isinstance(value, (int, float)) else None
        if target_id.startswith("overlay."):
            player = self._overlay_images.get(layer.id)
            if layer.source_type != "overlay" or player is None or not player.animated:
                return None
            field = target_id.split(".", 1)[1]
            if field == "playback_speed":
                return float(layer.overlay_speed)
            if field == "frame_hold":
                return float(layer.overlay_frame_hold)
        return None

    def _set_layer_modifier_target(
            self,
            layer_id: str,
            target_id: str,
            value: float,
    ) -> bool:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            return False
        if target_id.startswith("layer."):
            field = target_id.split(".", 1)[1]
            if field == "opacity":
                layer.opacity = max(0.0, min(1.0, float(value)))
            elif field == "rotation":
                layer.rotation = max(-180.0, min(180.0, float(value)))
            elif field == "scale":
                amount = max(0.05, min(2.0, float(value)))
                layer.scale = (amount, amount)
            elif field == "position_x":
                layer.position = (max(0.0, min(1.0, float(value))), layer.position[1])
            elif field == "position_y":
                layer.position = (layer.position[0], max(0.0, min(1.0, float(value))))
            else:
                return False
            return True
        if target_id.startswith("layer_fx."):
            field = target_id.split(".", 1)[1]
            settings = normalize_layer_effects(layer.layer_effects)
            if field not in settings or field in {"enabled", "stages"}:
                return False
            settings[field] = float(value)
            layer.layer_effects = normalize_layer_effects(settings)
            return True
        if target_id.startswith("generator."):
            if layer.source_type != "generator" or not layer.generator_type:
                return False
            setting_key = self._generator_modifier_setting_key(target_id.split(".", 1)[1])
            if setting_key is None:
                return False
            settings = normalize_settings(layer.generator_type, layer.generator_settings)
            if setting_key not in settings:
                return False
            current = settings[setting_key]
            settings[setting_key] = (
                int(round(value))
                if isinstance(current, int) and not isinstance(current, bool)
                else float(value)
            )
            layer.generator_settings = normalize_settings(layer.generator_type, settings)
            self._request_generator_raster(layer)
            return True
        if target_id.startswith("overlay."):
            player = self._overlay_images.get(layer.id)
            if layer.source_type != "overlay" or player is None or not player.animated:
                return False
            field = target_id.split(".", 1)[1]
            if field == "playback_speed":
                layer.overlay_speed = max(0.1, min(4.0, float(value)))
            elif field == "frame_hold":
                layer.overlay_frame_hold = max(1, min(24, int(round(value))))
            else:
                return False
            player.configure_playback(
                layer.overlay_speed,
                layer.overlay_frame_hold,
                layer.overlay_loop,
            )
            return True
        return False

    def add_layer_performance_modifier(
            self,
            layer_id: str,
            modifier: LayerPerformanceModifier | dict[str, object],
    ) -> str:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            raise KeyError(f"Unknown layer: {layer_id}")
        item = (
            modifier
            if isinstance(modifier, LayerPerformanceModifier)
            else LayerPerformanceModifier.from_dict(modifier)
        )
        item.normalize()
        if any(
                raw.get("modifier_id") == item.modifier_id
                for raw in layer.performance_modifiers
        ):
            raise ValueError(f"Duplicate modifier ID: {item.modifier_id}")
        layer.performance_modifiers.append(item.to_dict())
        self.events.publish(
            "layer.performance_modifiers.updated",
            layer_id=layer_id,
            modifier_id=item.modifier_id,
        )
        return item.modifier_id

    def remove_layer_performance_modifier(self, layer_id: str, modifier_id: str) -> bool:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            return False
        before = len(layer.performance_modifiers)
        layer.performance_modifiers = [
            raw for raw in layer.performance_modifiers
            if str(raw.get("modifier_id", "")) != modifier_id
        ]
        removed = len(layer.performance_modifiers) != before
        if removed:
            self.events.publish(
                "layer.performance_modifiers.updated",
                layer_id=layer_id,
                modifier_id=modifier_id,
            )
        return removed

    def layer_performance_modifier_values(self, layer_id: str) -> dict[str, float]:
        return self.performance_modifier_engine.live_values(layer_id)

    def add_modulator(self, definition: ModulatorDefinition) -> str:
        modulator_id = self.modulator_bank.add(definition)
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=modulator_id,
        )
        return modulator_id

    def update_modulator(self, definition: ModulatorDefinition) -> None:
        self.modulator_bank.update(definition)
        self.modulator_bank_engine.reset_modulator(definition.modulator_id)
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=definition.modulator_id,
        )

    def remove_modulator(self, modulator_id: str) -> bool:
        source_id = f"modulator.{modulator_id}"
        removed = self.modulator_bank.remove(modulator_id)
        if not removed:
            return False
        removed_routes = [
            route.route_id
            for route in self.modulation.routes
            if route.source_id == source_id
        ]
        for route_id in removed_routes:
            self.modulation.remove_route(route_id)
        if removed_routes:
            self.events.publish(
                "performance.modulation.updated",
                removed_routes=removed_routes,
            )
        for layer in self.composition.layers:
            before = len(layer.performance_modifiers)
            layer.performance_modifiers = [
                raw for raw in layer.performance_modifiers
                if str(raw.get("source_id", "")) != source_id
            ]
            if len(layer.performance_modifiers) != before:
                self.events.publish(
                    "layer.performance_modifiers.updated",
                    layer_id=layer.id,
                    modulator_removed=modulator_id,
                )
        self.modulator_bank_engine.reset_modulator(modulator_id)
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=modulator_id,
        )
        return True

    def duplicate_modulator(self, modulator_id: str) -> str:
        definition = self.modulator_bank.duplicate(modulator_id)
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=definition.modulator_id,
        )
        return definition.modulator_id

    def create_modulator_from_preset(self, preset_id: str) -> str:
        definition = self.modulator_bank.instantiate_preset(preset_id)
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=definition.modulator_id,
        )
        return definition.modulator_id

    def apply_modulator_preset(
            self,
            modulator_id: str,
            name: str,
            description: str = "",
    ) -> str:
        preset_id = self.modulator_bank.save_preset(
            modulator_id, name, description
        )
        self.events.publish(
            "performance.modulator_bank.updated",
            modulator_id=modulator_id,
            preset_id=preset_id,
        )
        return preset_id

    def delete_modulator_preset(self, preset_id: str) -> bool:
        removed = self.modulator_bank.delete_preset(preset_id)
        if removed:
            self.events.publish("performance.modulator_bank.updated")
        return removed

    def export_modulator_presets(self, path: str | Path) -> Path:
        return self.modulator_bank.export_presets(path)

    def import_modulator_presets(self, path: str | Path) -> int:
        imported = self.modulator_bank.import_presets(path)
        if imported:
            self.events.publish(
                "performance.modulator_bank.updated",
                imported=imported,
            )
        return imported

    def apply_layer_performance_modifiers(
            self,
            now: float | None = None,
    ) -> dict[tuple[str, str], float]:
        sources = self._modulation_sources()
        sources.update(
            self.modulator_bank_engine.evaluate(
                self.modulator_bank,
                sources,
                now=now,
            )
        )
        return self.performance_modifier_engine.evaluate(
            self.composition.layers,
            sources,
            self._get_layer_modifier_target,
            self._set_layer_modifier_target,
            now=now,
        )

    def _get_modulation_target(self, target_id: str) -> float | None:
        if target_id.startswith("master."):
            field = target_id.split(".", 1)[1]
            if field in _MASTER_MODULATION_FIELDS:
                value = getattr(self.effects, field)
                return float(value) if isinstance(value, (int, float)) else None
            return None

        if target_id.startswith("selected_layer."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked:
                return None
            field = target_id.split(".", 1)[1]
            if field in {"opacity", "rotation"}:
                return float(getattr(layer, field))
            if field == "position_x":
                return float(layer.position[0])
            if field == "position_y":
                return float(layer.position[1])
            if field == "scale":
                return float(layer.scale[0])
            return None

        if target_id.startswith("layer_fx."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked:
                return None
            field = target_id.split(".", 1)[1]
            settings = normalize_layer_effects(layer.layer_effects)
            value = settings.get(field)
            return float(value) if isinstance(value, (int, float)) else None

        if target_id.startswith("generator."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked or layer.source_type != "generator":
                return None
            field = target_id.split(".", 1)[1]
            settings = normalize_settings(
                layer.generator_type or "geometry",
                layer.generator_settings,
            )
            setting_key = self._generator_modifier_setting_key(field)
            value = settings.get(setting_key) if setting_key else None
            return float(value) if isinstance(value, (int, float)) else None

        if target_id.startswith("overlay."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            player = self._overlay_images.get(layer.id) if layer is not None else None
            if (
                    layer is None or layer.locked or layer.source_type != "overlay"
                    or player is None or not player.animated
            ):
                return None
            field = target_id.split(".", 1)[1]
            if field == "playback_speed":
                return float(layer.overlay_speed)
            if field == "frame_hold":
                return float(layer.overlay_frame_hold)
            return None

        if target_id.startswith("automation."):
            field = target_id.split(".", 1)[1]
            settings = self.automation.settings
            mapping = {
                "loop_probability": "loop_probability",
                "clip_switch_probability": "clip_switch_probability",
                "cut_interval": "min_cut_interval",
                "min_segment_seconds": "min_segment_seconds",
                "max_segment_seconds": "max_segment_seconds",
                "layout_interval": "min_layout_interval",
                "effect_interval": "min_effect_interval",
                "generator_interval": "min_generator_interval",
            }
            setting_key = mapping.get(field)
            value = getattr(settings, setting_key) if setting_key else None
            return float(value) if isinstance(value, (int, float)) else None
        return None

    def _set_modulation_target(self, target_id: str, value: float) -> bool:
        if target_id.startswith("master."):
            field = target_id.split(".", 1)[1]
            if field not in _MASTER_MODULATION_FIELDS:
                return False
            current = getattr(self.effects, field)
            if isinstance(current, int) and not isinstance(current, bool):
                setattr(self.effects, field, int(round(value)))
            else:
                setattr(self.effects, field, float(value))
            self.effects.clamp()
            self.effects.preset_name = "Custom"
            return True

        if target_id.startswith("selected_layer."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked:
                return False
            field = target_id.split(".", 1)[1]
            if field in {"opacity", "rotation"}:
                setattr(layer, field, float(value))
            elif field == "position_x":
                layer.position = (max(0.0, min(1.0, float(value))), layer.position[1])
            elif field == "position_y":
                layer.position = (layer.position[0], max(0.0, min(1.0, float(value))))
            elif field == "scale":
                scale = max(0.05, min(2.0, float(value)))
                layer.scale = (scale, scale)
            else:
                return False
            self.events.publish("layer.modulated", layer_id=layer.id, target=target_id)
            return True

        if target_id.startswith("layer_fx."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked:
                return False
            field = target_id.split(".", 1)[1]
            settings = normalize_layer_effects(layer.layer_effects)
            if field not in settings or field in {"enabled", "stages"}:
                return False
            settings[field] = float(value)
            layer.layer_effects = normalize_layer_effects(settings)
            self.events.publish("layer.modulated", layer_id=layer.id, target=target_id)
            return True

        if target_id.startswith("generator."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            if layer is None or layer.locked or layer.source_type != "generator":
                return False
            field = target_id.split(".", 1)[1]
            setting_key = self._generator_modifier_setting_key(field)
            if not setting_key or not layer.generator_type:
                return False
            settings = normalize_settings(layer.generator_type, layer.generator_settings)
            if setting_key not in settings:
                return False
            current = settings[setting_key]
            settings[setting_key] = (
                int(round(value))
                if isinstance(current, int) and not isinstance(current, bool)
                else float(value)
            )
            layer.generator_settings = normalize_settings(layer.generator_type, settings)
            self._request_generator_raster(layer)
            self.events.publish("layer.modulated", layer_id=layer.id, target=target_id)
            return True

        if target_id.startswith("overlay."):
            layer = self.composition.get_layer(self._selected_layer_id or "")
            player = self._overlay_images.get(layer.id) if layer is not None else None
            if (
                    layer is None or layer.locked or layer.source_type != "overlay"
                    or player is None or not player.animated
            ):
                return False
            field = target_id.split(".", 1)[1]
            if field == "playback_speed":
                layer.overlay_speed = max(0.1, min(4.0, float(value)))
            elif field == "frame_hold":
                layer.overlay_frame_hold = max(1, min(24, int(round(value))))
            else:
                return False
            player.configure_playback(
                layer.overlay_speed,
                layer.overlay_frame_hold,
                layer.overlay_loop,
            )
            self.events.publish("layer.modulated", layer_id=layer.id, target=target_id)
            return True

        if target_id.startswith("automation."):
            field = target_id.split(".", 1)[1]
            settings = self.automation.settings
            if field in {"loop_probability", "clip_switch_probability"}:
                setattr(settings, field, max(0.0, min(1.0, float(value))))
            elif field == "cut_interval":
                minimum = max(1.0, min(60.0, float(value)))
                settings.min_cut_interval = minimum
                settings.max_cut_interval = max(minimum, settings.max_cut_interval)
            elif field == "min_segment_seconds":
                minimum = max(0.5, min(30.0, float(value)))
                settings.min_segment_seconds = minimum
                settings.max_segment_seconds = max(minimum, settings.max_segment_seconds)
            elif field == "max_segment_seconds":
                maximum = max(0.5, min(60.0, float(value)))
                settings.max_segment_seconds = maximum
                settings.min_segment_seconds = min(settings.min_segment_seconds, maximum)
            elif field in {"layout_interval", "effect_interval", "generator_interval"}:
                minimum = max(2.0, min(120.0, float(value)))
                field_map = {
                    "layout_interval": ("min_layout_interval", "max_layout_interval"),
                    "effect_interval": ("min_effect_interval", "max_effect_interval"),
                    "generator_interval": ("min_generator_interval", "max_generator_interval"),
                }
                low_field, high_field = field_map[field]
                setattr(settings, low_field, minimum)
                setattr(settings, high_field, max(minimum, getattr(settings, high_field)))
            else:
                return False
            settings.normalize()
            return True
        return False

    def notify_layer_manual_override(
            self,
            layer_id: str,
            duration_seconds: float = 3.0,
    ) -> None:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            return
        local_targets = {
            str(raw.get("target_id", ""))
            for raw in layer.performance_modifiers
            if isinstance(raw, dict)
        }
        modifier_engine = getattr(self, "performance_modifier_engine", None)
        if modifier_engine is not None:
            modifier_engine.notify_manual_override(
                layer_id,
                local_targets,
                layer.performance_modifiers,
                duration_seconds,
            )
        if layer_id == self._selected_layer_id:
            self.notify_manual_override("selected_layer.*", duration_seconds)

    def notify_manual_override(
            self,
            target_id: str,
            duration_seconds: float = 3.0,
    ) -> None:
        targets = (
            [key for key, spec in TARGET_SPECS.items() if spec.category == "master"]
            if target_id == "master.*"
            else [key for key in TARGET_SPECS if key.startswith(target_id[:-1])]
            if target_id.endswith(".*")
            else [target_id]
        )
        for key in targets:
            current = self._get_modulation_target(key)
            if current is not None:
                self._modulation_base_values[key] = current
            self.modulation.manual_override(key, duration_seconds)
        selected = self.composition.get_layer(self._selected_layer_id or "")
        modifier_engine = getattr(self, "performance_modifier_engine", None)
        if selected is not None and modifier_engine is not None:
            local_targets = set()
            for raw in selected.performance_modifiers:
                if not isinstance(raw, dict):
                    continue
                local_target = str(raw.get("target_id", ""))
                selected_layer_aliases = {
                    "selected_layer.opacity": "layer.opacity",
                    "selected_layer.rotation": "layer.rotation",
                    "selected_layer.scale": "layer.scale",
                    "selected_layer.position_x": "layer.position_x",
                    "selected_layer.position_y": "layer.position_y",
                }
                local_alias = selected_layer_aliases.get(target_id)
                if (
                        target_id == "generator.*" and local_target.startswith("generator.")
                        or target_id == "overlay.*" and local_target.startswith("overlay.")
                        or target_id == "selected_layer.*" and local_target.startswith("layer.")
                        or local_target == local_alias
                        or target_id == local_target
                ):
                    local_targets.add(local_target)
            modifier_engine.notify_manual_override(
                selected.id,
                local_targets,
                selected.performance_modifiers,
                duration_seconds,
            )

    def apply_modulation(self) -> dict[str, float]:
        now = time.monotonic()
        sources = self._modulation_sources()
        sources.update(
            self.modulator_bank_engine.evaluate(
                self.modulator_bank,
                sources,
                now=now,
            )
        )
        selected = self.composition.get_layer(self._selected_layer_id or "")
        claimed = {
            target_id
            for target_id in self.performance_modifier_engine.claimed_targets(
                selected,
                now=now,
                available_sources=set(sources),
            )
            if selected is not None
               and self._get_layer_modifier_target(selected.id, target_id) is not None
        }
        global_aliases = {
            "layer.opacity": "selected_layer.opacity",
            "layer.rotation": "selected_layer.rotation",
            "layer.scale": "selected_layer.scale",
            "layer.position_x": "selected_layer.position_x",
            "layer.position_y": "selected_layer.position_y",
        }
        suppressed_global = {
            global_aliases.get(target, target) for target in claimed
        }

        # If a global route was already moving a parameter before a layer-local
        # modifier claimed it, return to the global route's baseline first. The
        # per-layer engine then captures the clean baseline, not a transient value.
        for target_id in suppressed_global:
            base = self._modulation_base_values.get(target_id)
            if base is not None:
                self._set_modulation_target(target_id, base)

        # Evaluate local modifiers first. When the last local modifier is disabled
        # or its source disappears, its baseline is restored before a global route
        # is allowed to take over on this same application tick.
        self.performance_modifier_engine.evaluate(
            self.composition.layers,
            sources,
            self._get_layer_modifier_target,
            self._set_layer_modifier_target,
            now=now,
        )

        outputs, released = self.modulation.evaluate(sources, now=now)
        for target_id in released:
            if target_id in suppressed_global:
                continue
            base = self._modulation_base_values.pop(target_id, None)
            if base is not None:
                self._set_modulation_target(target_id, base)
        for target_id, value in outputs.items():
            if target_id in suppressed_global:
                continue
            if target_id not in self._modulation_base_values:
                base = self._get_modulation_target(target_id)
                if base is None:
                    continue
                self._modulation_base_values[target_id] = base
            self._set_modulation_target(target_id, value)
        return outputs

    def _validate_modulation_bank_source(self, source_id: str) -> None:
        if not source_id.startswith("modulator."):
            return
        modulator_id = source_id.removeprefix("modulator.")
        if self.modulator_bank.get(modulator_id) is None:
            raise ValueError(f"Unknown Modulator Bank source: {source_id}")

    def add_modulation_route(self, route) -> None:
        self._validate_modulation_bank_source(str(route.source_id))
        self.modulation.add_route(route)
        self.events.publish("performance.modulation.updated")

    def update_modulation_route(
            self,
            route_id: str,
            changes: dict[str, object],
    ) -> None:
        existing = next(
            (route for route in self.modulation.routes if route.route_id == route_id),
            None,
        )
        if existing is None:
            raise KeyError(f"Unknown modulation route: {route_id}")
        next_source = str(changes.get("source_id", existing.source_id))
        self._validate_modulation_bank_source(next_source)
        previous_target = existing.target_id
        self.modulation.update_route(route_id, changes)
        updated = next(
            route for route in self.modulation.routes if route.route_id == route_id
        )
        if previous_target != updated.target_id:
            base = self._modulation_base_values.pop(previous_target, None)
            if base is not None:
                self._set_modulation_target(previous_target, base)
        self.events.publish("performance.modulation.updated")

    def remove_modulation_route(self, route_id: str) -> None:
        self.modulation.remove_route(route_id)
        outputs, released = self.modulation.evaluate(self._modulation_sources())
        for target_id in released:
            base = self._modulation_base_values.pop(target_id, None)
            if base is not None:
                self._set_modulation_target(target_id, base)
        self.events.publish("performance.modulation.updated")

    def tick_performance_control(self) -> int:
        midi_events = self.midi_input.drain(64)
        clock_events = self.transport.tick()
        for event in clock_events:
            self.submit_control_event(event)
        processed_events = self.process_control_events()
        processed_audio = self.process_audio_frames()
        self._tick_scene_morph()
        sources = self._modulation_sources()
        energy, cutoff = self._automation_musical_context(sources)
        self.automation.set_performance_context(
            energy=energy,
            cutoff=cutoff,
            intensity=float(self.performance_control.intensity),
            bar_index=int(self.performance_control.bar_index),
        )
        self.apply_modulation()
        self._monitor_performance_mode()
        return processed_events + processed_audio + len(clock_events) + midi_events

    def tick_automation(self) -> bool:
        changed = self.automation.tick()
        if self.performance_mode.enabled:
            self.performance_mode.set_automation_armed(
                self._performance_automation_armed,
                self.automation.running,
            )
            if not self.automation.running:
                self._performance_automation_owned = False
        if changed:
            for deck_id, deck in self.decks.items():
                if deck.current_frame is None:
                    self._frame_snapshots.pop(deck_id, None)
            self.events.publish("automation.changed", action=self.automation.last_action)
        return changed

    # M5 — MIDI controls and complete performance sets.
    @staticmethod
    def discover_midi_inputs() -> list[str]:
        return MIDIInputService.discover()

    def start_midi_input(self, device_name: str) -> bool:
        started = self.midi_input.start(device_name)
        self.events.publish(
            "performance.midi.status", state=self.midi_input.state,
            device=self.midi_input.device_id, error=self.midi_input.error,
        )
        return started

    def stop_midi_input(self) -> None:
        self.midi_input.stop()
        self.events.publish("performance.midi.status", state="stopped", device="", error="")

    def begin_midi_learn(self, target: str, device_id: str = "*", minimum: float = 0.0,
                         maximum: float = 1.0, curve: str = "linear",
                         pickup: bool = True) -> None:
        mapping = MIDIMapping(
            device_id=device_id, message="cc", number=1, target=target,
            minimum=minimum, maximum=maximum, curve=curve, pickup=pickup,
        )
        mapping.normalize()
        self._midi_learn_request = {
            "device_id": mapping.device_id, "target": mapping.target,
            "minimum": mapping.minimum, "maximum": mapping.maximum,
            "curve": mapping.curve, "pickup": mapping.pickup,
        }
        self._midi_learn_last_event = ""
        self.events.publish("performance.midi.learn.started", target=target, device=device_id)

    def cancel_midi_learn(self) -> None:
        self._midi_learn_request = None
        self.events.publish("performance.midi.learn.cancelled")

    def set_midi_mappings(self, mappings: list[MIDIMapping | dict[str, Any]]) -> None:
        self.midi_mapping_engine.replace_mappings(mappings)
        self.events.publish(
            "performance.midi.mappings.updated",
            count=len(self.midi_mapping_engine.mappings),
        )

    def _midi_target_values(self) -> dict[str, float]:
        values: dict[str, float] = {}
        for layer in self.composition.layers:
            for target in (
                    "layer.opacity", "layer.rotation", "layer.scale",
                    "layer.position_x", "layer.position_y",
                    "generator.animation_speed", "generator.animation_amount",
                    "generator.density", "generator.rotation",
                    "generator.text_animation_speed", "generator.text_animation_amount",
                    "generator.text_animation_columns",
                    "generator.font_size", "generator.letter_spacing",
                    "generator.waveform_amplitude", "generator.waveform_frequency",
                    "generator.particle_speed", "generator.particle_size",
                    "generator.particle_spread", "generator.particle_trail",
                    "generator.particle_emission_rate", "generator.particle_system_size",
                    "generator.particle_lifetime", "generator.particle_turbulence",
                    "generator.particle_force_strength", "generator.particle_reform_strength",
                    "layer_fx.mix", "layer_fx.monochrome", "layer_fx.threshold",
                    "layer_fx.contrast", "layer_fx.brightness", "layer_fx.chromatic",
                    "layer_fx.scanlines", "layer_fx.posterize", "layer_fx.invert",
                    "layer_fx.hue", "layer_fx.saturation",
            ):
                current = self._get_layer_modifier_target(layer.id, target)
                if current is not None:
                    values[f"layer.{layer.id}.{target}"] = current
        for target in (
                "master.brightness", "master.exposure", "master.contrast",
                "master.saturation", "master.grain", "master.glitch", "master.vignette",
                "master.hue", "master.chromatic", "master.scanlines", "master.pixelate",
                "master.posterize", "master.invert", "master.halftone", "master.solarize",
                "master.transform_mix", "master.kaleidoscope_slices",
                "master.kaleidoscope_rotation", "master.kaleidoscope_zoom",
                "master.mosaic_tiles", "master.pixel_sort_amount",
                "master.pixel_sort_threshold", "master.edge_amount", "master.dither",
                "master.displacement_amount", "master.displacement_scale",
                "master.feedback_amount", "master.feedback_decay", "master.feedback_zoom",
                "master.feedback_rotation", "master.feedback_translate_x",
                "master.feedback_translate_y", "master.feedback_color_shift",
                "master.feedback_distortion", "master.feedback_motion_warp",
                "master.feedback_datamosh", "master.feedback_delay_frames",
        ):
            current = self._get_modulation_target(target)
            if current is not None:
                values[target] = current
        values["scene.intensity"] = float(self.performance_control.intensity)
        values["transport.tempo"] = float(self.transport.bpm)
        settings = self.automation.settings
        values["automation.loop_probability"] = float(settings.loop_probability)
        values["automation.clip_switch_probability"] = float(
            settings.clip_switch_probability
        )
        values["automation.cut_interval"] = float(settings.min_cut_interval)
        values["automation.min_segment_seconds"] = float(settings.min_segment_seconds)
        values["automation.max_segment_seconds"] = float(settings.max_segment_seconds)
        values["automation.layout_interval"] = float(settings.min_layout_interval)
        values["automation.effect_interval"] = float(settings.min_effect_interval)
        values["automation.generator_interval"] = float(settings.min_generator_interval)
        for name, value in self.performance_control.macros.items():
            values[f"macro.{name}"] = float(value)
        return values

    def _handle_midi_event(self, device_id: str, message: str, channel: int,
                           number: int, value: float) -> None:
        request = self._midi_learn_request
        if request is not None and request["device_id"] in {"*", device_id}:
            learned = MIDIMapping(
                device_id=device_id, message=message, channel=channel, number=number,
                target=request["target"], minimum=request["minimum"],
                maximum=request["maximum"], curve=request["curve"],
                pickup=request["pickup"],
            )
            learned.normalize()
            self.midi_mapping_engine.replace_mappings(
                [*self.midi_mapping_engine.mappings, learned]
            )
            self._midi_learn_request = None
            self._midi_learn_last_event = (
                f"{device_id} · ch {channel + 1} · {message.upper()} {number} → {learned.target}"
            )
            self.events.publish(
                "performance.midi.learned", mapping=learned.to_dict(),
                description=self._midi_learn_last_event,
            )
            return
        for target, mapped in self.midi_mapping_engine.process(
                device_id, message, channel, number, value, self._midi_target_values()
        ):
            self._apply_midi_target(target, mapped)

    def _apply_midi_target(self, target: str, value: float) -> bool:
        if target.startswith("scene.trigger."):
            scene_id = target.removeprefix("scene.trigger.")
            active = float(value) > 0.0
            was_active = self._midi_scene_trigger_state.get(target, False)
            self._midi_scene_trigger_state[target] = active
            if active and not was_active:
                return self.schedule_performance_scene(scene_id)
            return False
        if target.startswith("macro."):
            name = target.removeprefix("macro.")
            if not name or not name.replace("_", "").isalnum():
                return False
            return self.submit_control_event(ControlEvent(
                "macro.set", "midi", {"name": name, "value": max(0.0, min(1.0, value))}
            ))
        if target == "transport.tempo":
            return self.submit_control_event(ControlEvent(
                "transport.tempo", "midi", {"bpm": max(20.0, min(300.0, value))}
            ))
        if target == "scene.intensity":
            return self.submit_control_event(ControlEvent(
                "scene.intensity", "midi", {"intensity": max(0.0, min(1.0, value))}
            ))
        if target.startswith("layer."):
            remainder = target.removeprefix("layer.")
            layer_id, separator, parameter = remainder.partition(".")
            if not separator:
                return False
            layer = self.composition.get_layer(layer_id)
            if layer is None or layer.locked:
                return False
            return self._set_layer_modifier_target(layer_id, parameter, value)
        if target.startswith(("master.", "automation.")):
            return self._set_modulation_target(target, value)
        return False

    def capture_performance_scene(
            self,
            scene_id: str,
            label: str = "",
            quantization: Quantization = "bar",
            cue: str = "",
            tags: list[str] | None = None,
            transition: dict[str, Any] | None = None,
    ) -> PerformanceScene:
        """Capture a complete VJ scene without copying source media or runtime handles."""
        scene_id = str(scene_id).strip()
        if not scene_id:
            raise ValueError("Scene ID cannot be empty.")
        cue = str(cue).strip()[:128]
        duplicate_cue = next(
            (
                scene for existing_id, scene in self.performance_scenes.items()
                if existing_id != scene_id
                   and cue
                   and scene.cue.casefold() == cue.casefold()
            ),
            None,
        )
        if duplicate_cue is not None:
            raise ValueError(
                f"OSC cue '{cue}' is already assigned to scene '{duplicate_cue.label}'."
            )

        existing = self.performance_scenes.get(scene_id)
        selected_transition = (
            dict(transition)
            if isinstance(transition, dict)
            else dict(existing.transition) if existing else None
        )
        selected_tags = list(tags) if tags is not None else (
            list(existing.tags) if existing else []
        )
        snapshot = {
            "schema_version": 2,
            "composition": self.composition.to_dict(),
            "decks": [deck.to_dict() for deck in self.decks.values()],
            "effects": self.effects.to_dict(),
            "automation_settings": self.automation.settings.to_dict(),
            "transport": self.transport.to_dict(),
            "performance_control": {
                "intensity": self.performance_control.intensity,
                "macros": dict(self.performance_control.macros),
            },
            "modulation_routes": self.modulation.to_dict(),
            "modulator_bank": self.modulator_bank.to_dict(),
            "palette": self.active_palette,
        }
        scene = PerformanceScene(
            scene_id,
            label or scene_id.replace("_", " ").title(),
            snapshot,
            quantization=quantization,
            cue=cue,
            tags=selected_tags,
            transition=selected_transition or {
                "duration": 0.0,
                "curve": "smoothstep",
                "discrete": "cut",
            },
        )
        scene.normalize()
        self.performance_scenes[scene.scene_id] = scene
        self.events.publish(
            "performance.scene_bank.updated",
            scene_id=scene.scene_id,
            label=scene.label,
            layer_count=len(self.composition.layers),
            deck_count=len(self.decks),
        )
        return scene

    def schedule_performance_scene(
            self,
            scene_id: str,
            morph_seconds: float | None = None,
    ) -> bool:
        """Recall a scene immediately or at the selected internal/external clock boundary."""
        scene = self.performance_scenes.get(str(scene_id))
        if scene is None:
            return False
        requested_duration = (
            scene.transition.get("duration", 0.0)
            if morph_seconds is None else morph_seconds
        )
        duration = max(0.0, min(60.0, float(requested_duration)))
        if scene.quantization == "immediate":
            return self.recall_performance_scene(scene.scene_id, morph_seconds=duration)

        internal_clock = self.transport.running and not self.transport.paused
        external_clock = (
                self.performance_control.source_id == "sonic_pi"
                and self.performance_control.transport_running
                and not self.performance_control.transport_paused
        )
        if internal_clock:
            self._pending_scene_morph_seconds[scene.scene_id] = duration
            self.transport.schedule_scene(
                scene.scene_id,
                self.performance_control.intensity,
                quantization=scene.quantization,
            )
        elif external_clock:
            current_bar = max(1, int(self.performance_control.bar_index))
            current_beat = max(0, int(self.performance_control.beat_index))
            beats_per_bar = max(1, int(self.performance_control.beats_per_bar))
            if scene.quantization == "beat":
                if current_beat + 1 < beats_per_bar:
                    due_bar, due_beat = current_bar, current_beat + 1
                else:
                    due_bar, due_beat = current_bar + 1, 0
            elif scene.quantization == "bar":
                due_bar, due_beat = current_bar + 1, 0
            else:
                phrase_bars = max(1, int(self.transport.phrase_bars))
                due_bar = (
                        ((current_bar - 1) // phrase_bars + 1) * phrase_bars + 1
                )
                due_beat = 0
            self._pending_external_scene_recall[scene.scene_id] = {
                "due_bar": float(due_bar),
                "due_beat": float(due_beat),
                "morph_seconds": duration,
            }
        else:
            return self.recall_performance_scene(scene.scene_id, morph_seconds=duration)

        self.events.publish(
            "performance.scene.scheduled",
            scene_id=scene.scene_id,
            quantization=scene.quantization,
            morph_seconds=duration,
        )
        return True

    def _fire_due_external_scene_recall(self) -> None:
        if not self._pending_external_scene_recall:
            return
        current_bar = max(0, int(self.performance_control.bar_index))
        current_beat = max(0, int(self.performance_control.beat_index))
        due = []
        for scene_id, request in self._pending_external_scene_recall.items():
            due_bar = int(request["due_bar"])
            due_beat = int(request["due_beat"])
            if (current_bar, current_beat) >= (due_bar, due_beat):
                due.append((scene_id, float(request["morph_seconds"])))
        for scene_id, duration in due:
            self._pending_external_scene_recall.pop(scene_id, None)
            self.recall_performance_scene(scene_id, morph_seconds=duration)

    def trigger_performance_scene_cue(self, cue: str) -> bool:
        """Resolve a user scene by its OSC cue, scene ID or exact display label."""
        key = str(cue).strip().casefold()
        if not key:
            return False
        matches = [
            scene for scene in self.performance_scenes.values()
            if key in {
                scene.cue.casefold(),
                scene.scene_id.casefold(),
                scene.label.casefold(),
            }
        ]
        if len(matches) != 1:
            if len(matches) > 1:
                _LOG.warning("Scene cue '%s' is ambiguous; no scene was triggered.", cue)
            return False
        return self.schedule_performance_scene(matches[0].scene_id)

    @staticmethod
    def _scene_compatibility_key(snapshot: dict[str, Any]) -> tuple[Any, ...]:
        composition_data = snapshot.get("composition", {})
        if not isinstance(composition_data, dict):
            return ()
        layers = composition_data.get("layers", [])
        if not isinstance(layers, list):
            return ()
        signature = []
        for raw in layers:
            if not isinstance(raw, dict):
                continue
            signature.append((
                str(raw.get("id", "")),
                str(raw.get("source_type", "")),
                str(raw.get("generator_type") or ""),
                str(raw.get("overlay_kind") or ""),
            ))
        return (
            int(composition_data.get("width", 0)),
            int(composition_data.get("height", 0)),
            tuple(sorted(signature)),
        )

    def compatible_performance_scenes(self) -> list[PerformanceScene]:
        current = {"composition": self.composition.to_dict()}
        key = self._scene_compatibility_key(current)
        return [
            scene for scene in self.performance_scenes.values()
            if scene.scene_id
               and self._scene_compatibility_key(scene.snapshot) == key
        ]

    def random_performance_scene(self) -> PerformanceScene | None:
        """Choose a random scene with the same layer topology as the current composition."""
        candidates = self.compatible_performance_scenes()
        if not candidates:
            self.events.publish("performance.scene.random.empty")
            return None
        scene = random.choice(candidates)
        if self.schedule_performance_scene(scene.scene_id):
            self.events.publish("performance.scene.random.selected", scene_id=scene.scene_id)
            return scene
        return None

    def remove_performance_scene(self, scene_id: str) -> bool:
        scene_id = str(scene_id)
        removed = self.performance_scenes.pop(scene_id, None) is not None
        self._pending_scene_morph_seconds.pop(scene_id, None)
        self._pending_external_scene_recall.pop(scene_id, None)
        self._midi_scene_trigger_state.pop(f"scene.trigger.{scene_id}", None)
        if removed:
            self.events.publish("performance.scene_bank.updated", scene_id=scene_id)
        return removed

    def _restore_scene_decks(self, values: object) -> None:
        """Restore saved deck assignments while respecting live deck locks and missing media."""
        if not isinstance(values, list):
            return
        for state in values:
            if not isinstance(state, dict):
                continue
            deck_id = str(state.get("id", ""))
            deck = self.decks.get(deck_id)
            if deck is None or deck.locked:
                continue
            media_path = state.get("path")
            if not media_path:
                deck.close()
                self._frame_snapshots.pop(deck_id, None)
                continue
            source = Path(str(media_path)).expanduser()
            if not source.is_file():
                _LOG.warning(
                    "VJ scene %s references missing media for %s: %s; keeping current deck source",
                    state.get("id", "unknown"),
                    deck_id,
                    source,
                )
                self.events.publish(
                    "performance.scene.media_missing",
                    deck_id=deck_id,
                    path=str(source),
                )
                continue
            try:
                deck.load(
                    source,
                    asset_id=state.get("asset_id"),
                    collection_id=state.get("collection_id"),
                    segment_start=float(state.get("segment_start", 0.0)),
                    segment_end=state.get("segment_end"),
                    loop=bool(state.get("loop", True)),
                )
                if not bool(state.get("playing", True)):
                    deck.pause()
                self._frame_snapshots.pop(deck_id, None)
            except (OSError, TypeError, ValueError) as exc:
                _LOG.warning("Could not restore scene deck %s: %s", deck_id, exc)

    def _restore_scene_modulators(self, snapshot: dict[str, Any]) -> None:
        bank_state = snapshot.get("modulator_bank")
        if isinstance(bank_state, dict):
            self.modulator_bank.load_dict(bank_state)
            self.modulator_bank_engine.reset()
        routes = snapshot.get("modulation_routes")
        if isinstance(routes, list):
            self.modulation.load_dict(routes)
            known_sources = {
                f"modulator.{definition.modulator_id}"
                for definition in self.modulator_bank.list_modulators()
            }
            self.modulation.routes = [
                route for route in self.modulation.routes
                if (
                        not route.source_id.startswith("modulator.")
                        or route.source_id in known_sources
                )
            ]
            self.modulation.reset_runtime()

    def recall_performance_scene(
            self,
            scene_id: str,
            morph_seconds: float = 0.0,
    ) -> bool:
        scene = self.performance_scenes.get(str(scene_id))
        if scene is None:
            return False
        composition_data = scene.snapshot.get("composition")
        if not isinstance(composition_data, dict):
            return False
        try:
            candidate = Composition.from_dict(composition_data)
        except (TypeError, ValueError, KeyError) as exc:
            _LOG.warning("VJ scene %s has invalid composition data: %s", scene.scene_id, exc)
            return False

        # Capture numeric start values before replacing the scene. Existing layer IDs
        # are morphed where target types are compatible; discrete payloads switch now.
        start_values = self._midi_target_values() if morph_seconds > 0.0 else {}
        for current in self.composition.layers:
            if not current.locked:
                continue
            replacement = candidate.get_layer(current.id)
            if replacement is not None:
                candidate.layers[candidate.layers.index(replacement)] = current
            else:
                candidate.add_layer(current)

        self.composition = candidate
        self.layer_manager = LayerManager(self.composition, self.events)
        self.performance_modifier_engine.reset()
        self._restore_scene_decks(scene.snapshot.get("decks"))
        self._clear_overlays()
        for layer in self.composition.layers:
            if layer.source_type == "overlay":
                try:
                    self._attach_overlay_layer(layer)
                except Exception as exc:
                    _LOG.warning("Could not restore scene overlay %s: %s", layer.name, exc)

        if isinstance(scene.snapshot.get("effects"), dict):
            loaded = EffectSettings.from_dict(scene.snapshot["effects"])
            for key, value in loaded.to_dict().items():
                setattr(self.effects, key, value)
        if isinstance(scene.snapshot.get("automation_settings"), dict):
            allowed = AutomationSettings.__dataclass_fields__
            values = {
                key: value
                for key, value in scene.snapshot["automation_settings"].items()
                if key in allowed
            }
            settings = AutomationSettings(**values)
            settings.normalize()
            self.automation.settings = settings
        transport_settings = scene.snapshot.get("transport")
        if isinstance(transport_settings, dict):
            try:
                self.transport.load_settings(transport_settings)
            except (TypeError, ValueError):
                _LOG.warning("Skipping invalid transport settings in scene %s", scene.scene_id)
        self._restore_scene_modulators(scene.snapshot)

        palette = str(scene.snapshot.get("palette", self.active_palette))
        if palette in palette_names():
            self.active_palette = palette

        control_state = scene.snapshot.get("performance_control")
        if isinstance(control_state, dict):
            requested_intensity = float(
                control_state.get("intensity", self.performance_control.intensity)
            )
            self.performance_control.intensity = max(
                0.0, min(1.0, requested_intensity)
            )
            macros = control_state.get("macros")
            if isinstance(macros, dict):
                for name, value in macros.items():
                    if name in self.performance_control.macros:
                        self.performance_control.macros[name] = max(
                            0.0, min(1.0, float(value))
                        )

        self._active_scene_morph = None
        if morph_seconds > 0.0:
            end_values = self._midi_target_values()
            common = start_values.keys() & end_values.keys()
            morph_start = {key: start_values[key] for key in common}
            morph_end = {key: end_values[key] for key in common}
            if morph_start:
                self._active_scene_morph = SceneMorph(
                    morph_start,
                    morph_end,
                    time.monotonic(),
                    max(0.01, min(60.0, float(morph_seconds))),
                    curve=str(scene.transition.get("curve", "smoothstep")),
                )
                for target, value in morph_start.items():
                    self._apply_midi_target(target, value)
        self.events.publish(
            "performance.scene.recalled",
            scene_id=scene.scene_id,
            morph_seconds=max(0.0, float(morph_seconds)),
            discrete_mode=scene.transition.get("discrete", "cut"),
            palette=self.active_palette,
        )
        return True

    def _tick_scene_morph(self) -> None:
        morph = self._active_scene_morph
        if morph is None:
            return
        fraction, values = morph.value()
        for target, value in values.items():
            self._apply_midi_target(target, value)
        if fraction >= 1.0:
            self._active_scene_morph = None
            self.events.publish("performance.scene.morph.completed")

    def save_performance_set(self, path: str | Path) -> Path:
        # Reuse project snapshot logic so per-layer/global modulation baselines
        # are restored in the package without changing the live performance.
        previous_project_path = self.current_project_path
        try:
            with tempfile.TemporaryDirectory(prefix="eli-m5-set-") as temp_dir:
                project_path = Path(temp_dir) / "snapshot.eliav"
                self.save_project(project_path)
                project = json.loads(project_path.read_text(encoding="utf-8"))
        finally:
            self.current_project_path = previous_project_path
        app_state = project.get("app_state", {})
        payload = PerformanceSetStore.build_payload(
            project.get("composition", {}),
            project.get("decks", []),
            app_state.get("effects", self.effects.to_dict()),
            app_state.get("automation_settings", self.automation.settings.to_dict()),
            app_state.get("performance_settings", {}),
            list(self.performance_scenes.values()),
            self.midi_mapping_engine.mappings,
        )
        destination = PerformanceSetStore.save(path, payload)
        self.events.publish("performance.set.saved", path=destination)
        return destination

    def load_performance_set(self, path: str | Path) -> None:
        # Validate the complete package and all control definitions before mutation.
        payload = PerformanceSetStore.load(path)
        scenes = {}
        for raw in payload.get("scenes", []):
            scene = PerformanceScene(**raw)
            scene.normalize()
            scenes[scene.scene_id] = scene
        mappings = [MIDIMapping.from_dict(raw) for raw in payload.get("midi_mappings", [])]
        with tempfile.TemporaryDirectory(prefix="eli-m5-restore-") as temp_dir:
            staged_project = Path(temp_dir) / "restore.eliav"
            project_payload = {
                "format": "eli_lab_av_translator",
                "schema_version": 2,
                "project": {"name": payload.get("metadata", {}).get("name", "Performance Set")},
                "composition": payload["composition"],
                "decks": payload.get("decks", []),
                "app_state": {
                    "effects": payload.get("effects", {}),
                    "automation_settings": payload.get("automation_settings", {}),
                    "performance_settings": payload.get("performance_settings", {}),
                },
            }
            staged_project.write_text(
                json.dumps(project_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.load_project(staged_project)
        # The staged project file is temporary; do not retain its deleted path or
        # let a later ordinary project-save action overwrite the .eliset package.
        self.current_project_path = None
        self.set_midi_mappings(mappings)
        self.performance_scenes = scenes
        self.events.publish("performance.set.loaded", path=Path(path).resolve())

    def stop_automation(self) -> None:
        self.automation.stop()
        self._automation_collection_id = None
        if self.performance_mode.enabled:
            self._performance_automation_armed = False
            self._performance_automation_owned = False
            self.performance_mode.set_automation_armed(False, False)
        self.events.publish("automation.stopped")

    def save_project(self, path: str | Path) -> Path:
        deck_states = [deck.to_dict() for deck in self.decks.values()]
        app_state = {
            "effects": self.effects.to_dict(),
            "automation_settings": self.automation.settings.to_dict(),
            "performance_settings": {
                "transport": self.transport.to_dict(),
                "audio_analysis": self.audio_capture.settings.to_dict(),
                "modulation_routes": self.modulation.to_dict(),
                "scene_profiles": self.scene_profiles.to_dict(),
                "active_palette": self.active_palette,
                "modulator_bank": self.modulator_bank.to_dict(),
                "midi_mappings": getattr(
                    getattr(self, "midi_mapping_engine", None), "to_dict", lambda: []
                )(),
                "performance_scenes": [
                    scene.to_dict()
                    for scene in getattr(self, "performance_scenes", {}).values()
                ],
                "performance_mode_plan": self.performance_mode.plan.to_dict(),
            },
        }
        composition_snapshot = Composition.from_dict(self.composition.to_dict())
        if self.performance_mode.enabled:
            # Persist a ready-to-edit project, not a show that starts modulating
            # immediately on open. The saved Performance Mode button remains off.
            performance_settings = app_state["performance_settings"]
            for route in performance_settings.get("modulation_routes", []):
                if str(route.get("route_id", "")).startswith("auto-performance-"):
                    route["enabled"] = False
            bank_state = performance_settings.get("modulator_bank", {})
            for definition in bank_state.get("modulators", []):
                if str(definition.get("name", "")).startswith("AUTO ·"):
                    definition["enabled"] = False
            for layer in composition_snapshot.layers:
                for modifier in layer.performance_modifiers:
                    if str(modifier.get("name", "")).startswith("AUTO ·"):
                        modifier["enabled"] = False
        for (layer_id, target_id), base_value in (
                self.performance_modifier_engine.base_values().items()
        ):
            layer = composition_snapshot.get_layer(layer_id)
            if layer is None:
                continue
            if target_id.startswith("layer."):
                field = target_id.split(".", 1)[1]
                if field in {"opacity", "rotation"}:
                    setattr(layer, field, float(base_value))
                elif field == "scale":
                    layer.scale = (float(base_value), float(base_value))
                elif field == "position_x":
                    layer.position = (float(base_value), layer.position[1])
                elif field == "position_y":
                    layer.position = (layer.position[0], float(base_value))
            elif target_id.startswith("generator.") and layer.generator_type:
                setting_key = self._generator_modifier_setting_key(
                    target_id.split(".", 1)[1]
                )
                if setting_key:
                    settings = normalize_settings(
                        layer.generator_type,
                        layer.generator_settings,
                    )
                    current = settings.get(setting_key)
                    settings[setting_key] = (
                        int(round(base_value))
                        if isinstance(current, int) and not isinstance(current, bool)
                        else float(base_value)
                    )
                    layer.generator_settings = normalize_settings(
                        layer.generator_type,
                        settings,
                    )
            elif target_id == "overlay.playback_speed":
                layer.overlay_speed = max(0.1, min(4.0, float(base_value)))
            elif target_id == "overlay.frame_hold":
                layer.overlay_frame_hold = max(1, min(24, int(round(base_value))))

        # The global modulation matrix also writes into the live composition.
        # Save its pre-modulation values so a project never opens on a random beat peak.
        selected_layer = composition_snapshot.get_layer(
            getattr(self, "_selected_layer_id", None) or ""
        )
        effect_state = app_state["effects"]
        automation_state = app_state["automation_settings"]
        for target_id, base_value in getattr(self, "_modulation_base_values", {}).items():
            if target_id.startswith("master."):
                field = target_id.split(".", 1)[1]
                if field in effect_state:
                    effect_state[field] = base_value
            elif selected_layer is not None and target_id.startswith("selected_layer."):
                field = target_id.split(".", 1)[1]
                if field in {"opacity", "rotation"}:
                    setattr(selected_layer, field, float(base_value))
                elif field == "scale":
                    selected_layer.scale = (float(base_value), float(base_value))
                elif field == "position_x":
                    selected_layer.position = (
                        float(base_value), selected_layer.position[1]
                    )
                elif field == "position_y":
                    selected_layer.position = (
                        selected_layer.position[0], float(base_value)
                    )
            elif selected_layer is not None and target_id.startswith("generator."):
                setting_key = self._generator_modifier_setting_key(
                    target_id.split(".", 1)[1]
                )
                if setting_key and selected_layer.generator_type:
                    settings = normalize_settings(
                        selected_layer.generator_type,
                        selected_layer.generator_settings,
                    )
                    current = settings.get(setting_key)
                    settings[setting_key] = (
                        int(round(base_value))
                        if isinstance(current, int) and not isinstance(current, bool)
                        else float(base_value)
                    )
                    selected_layer.generator_settings = normalize_settings(
                        selected_layer.generator_type,
                        settings,
                    )
            elif selected_layer is not None and target_id == "overlay.playback_speed":
                selected_layer.overlay_speed = max(0.1, min(4.0, float(base_value)))
            elif selected_layer is not None and target_id == "overlay.frame_hold":
                selected_layer.overlay_frame_hold = max(
                    1, min(24, int(round(base_value)))
                )
            elif target_id.startswith("automation."):
                field = {
                    "automation.loop_probability": "loop_probability",
                    "automation.clip_switch_probability": "clip_switch_probability",
                    "automation.cut_interval": "min_cut_interval",
                    "automation.min_segment_seconds": "min_segment_seconds",
                    "automation.max_segment_seconds": "max_segment_seconds",
                    "automation.layout_interval": "min_layout_interval",
                    "automation.effect_interval": "min_effect_interval",
                    "automation.generator_interval": "min_generator_interval",
                }.get(target_id)
                if field in automation_state:
                    automation_state[field] = base_value

        saved_path = self.project_manager.save(
            path,
            composition_snapshot,
            deck_states,
            app_state=app_state,
        )
        self.current_project_path = saved_path
        self.events.publish("project.saved", path=saved_path)
        return saved_path

    def load_project(self, path: str | Path) -> None:
        if self.performance_mode.enabled:
            self.stop_performance_mode()
        self._pending_scene_morph_seconds.clear()
        self._pending_external_scene_recall.clear()
        self._active_scene_morph = None
        composition, deck_states = self.project_manager.load(path)
        self.control_events.clear()
        self.performance_control.reset()
        self._external_clock_bar_at = None
        self.transport.stop()
        self.transport.load_settings({
            "bpm": 120.0,
            "beats_per_bar": 4,
            "phrase_bars": 4,
        })
        self.audio_capture.update_settings(AudioAnalysisSettings())
        self.scene_profiles = SceneProfileRegistry()
        self.modulation.reset_runtime()
        self.performance_modifier_engine.reset()
        self._modulation_base_values.clear()
        self.automation.stop()
        self._clear_overlays()
        for deck in self.decks.values():
            deck.close()
            deck.locked = False

        self._frame_snapshots.clear()
        self.generator_raster_service.invalidate_missing(set())
        self.composition = composition
        self.layer_manager = LayerManager(self.composition, self.events)
        for layer in self.composition.layers:
            if layer.source_type == "overlay":
                try:
                    self._attach_overlay_layer(layer)
                except Exception as exc:
                    _LOG.warning("Could not restore overlay %s: %s", layer.name, exc)

        for state in deck_states:
            deck_id = str(state.get("id", ""))
            if deck_id not in self.decks:
                continue
            deck = self.decks[deck_id]
            deck.set_loop(bool(state.get("loop", True)))
            deck.locked = bool(state.get("locked", False))
            media_path = state.get("path")
            if media_path and Path(media_path).exists():
                deck.load(
                    str(media_path),
                    asset_id=state.get("asset_id"),
                    collection_id=state.get("collection_id"),
                    segment_start=float(state.get("segment_start", 0.0)),
                    segment_end=state.get("segment_end"),
                    loop=bool(state.get("loop", True)),
                )
            elif media_path:
                _LOG.warning("Project media is missing: %s", media_path)

        app_state = self.project_manager.last_app_state
        self.audio_capture.stop()
        self._audio_sources.clear()
        self._latest_audio_frame = None
        self.modulation.reset_runtime()
        self.modulator_bank = ModulatorBank()
        self.modulator_bank_engine.reset()
        self.performance_modifier_engine.reset()
        self._modulation_base_values.clear()
        performance_settings = app_state.get("performance_settings", {})
        self.performance_mode.plan = PerformanceModePlan()
        if isinstance(performance_settings, dict):
            if isinstance(performance_settings.get("performance_mode_plan"), dict):
                try:
                    self.performance_mode.plan = PerformanceModePlan(
                        **performance_settings["performance_mode_plan"]
                    )
                    self.performance_mode.plan.normalize()
                except (TypeError, ValueError):
                    _LOG.warning("Skipping invalid saved Performance Mode preferences")
            if isinstance(performance_settings.get("transport"), dict):
                self.transport.load_settings(performance_settings["transport"])
            if isinstance(performance_settings.get("audio_analysis"), dict):
                allowed_audio = AudioAnalysisSettings.__dataclass_fields__
                audio_values = {
                    key: value for key, value in performance_settings["audio_analysis"].items()
                    if key in allowed_audio
                }
                self.update_audio_analysis_settings(AudioAnalysisSettings(**audio_values))
            self.modulation.load_dict(performance_settings.get("modulation_routes", []))
            self.scene_profiles.load_dict(performance_settings.get("scene_profiles", []))
            active_palette = str(
                performance_settings.get("active_palette", self.active_palette)
            )
            if active_palette in palette_names():
                self.active_palette = active_palette
            self.modulator_bank.load_dict(
                performance_settings.get("modulator_bank", {})
            )
            known_modulator_sources = {
                f"modulator.{definition.modulator_id}"
                for definition in self.modulator_bank.list_modulators()
            }
            self.modulation.routes = [
                route for route in self.modulation.routes
                if (
                        not route.source_id.startswith("modulator.")
                        or route.source_id in known_modulator_sources
                )
            ]
            self.modulation.reset_runtime()
        self.performance_control.bpm = self.transport.bpm
        self.performance_control.beats_per_bar = self.transport.beats_per_bar
        if isinstance(app_state.get("effects"), dict):
            loaded_effects = EffectSettings.from_dict(app_state["effects"])
            for key, value in loaded_effects.to_dict().items():
                setattr(self.effects, key, value)
        if isinstance(app_state.get("automation_settings"), dict):
            allowed = AutomationSettings.__dataclass_fields__
            values = {
                key: value for key, value in app_state["automation_settings"].items()
                if key in allowed
            }
            self.automation.settings = AutomationSettings(**values)
            self.automation.settings.normalize()

        self.midi_mapping_engine.load_dict(performance_settings.get("midi_mappings", []))
        scenes = []
        for raw in performance_settings.get("performance_scenes", []):
            if isinstance(raw, dict):
                try:
                    scene = PerformanceScene(**raw)
                    scene.normalize()
                    scenes.append(scene)
                except (TypeError, ValueError):
                    _LOG.warning("Skipping invalid performance scene definition")
        self.performance_scenes = {scene.scene_id: scene for scene in scenes}
        self.current_project_path = Path(path).resolve()
        self.events.publish("project.loaded", path=self.current_project_path)

    def shutdown(self) -> None:
        if self.performance_mode.enabled:
            self.stop_performance_mode()
        self.generator_raster_service.shutdown()
        self.midi_input.stop()
        self.osc_receiver.stop()
        self.control_events.clear()
        self.audio_capture.shutdown()
        self.transport.stop()
        self.modulation.reset_runtime()
        self.automation.stop()
        self._clear_overlays()
        for deck in self.decks.values():
            deck.close()
        self.events.publish("application.shutdown")
        self.events.clear()
