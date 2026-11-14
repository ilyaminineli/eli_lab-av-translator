from __future__ import annotations

from types import SimpleNamespace

from core.application import Application
from core.automation import AutomationDirector
from generators.catalog import normalize_settings
from generators.raster_service import GeneratorRasterService


def test_timeline_arm_waiting_flag_uses_transport_position() -> None:
    armed: dict[str, object] = {}
    published: list[tuple[str, dict[str, object]]] = []
    app = SimpleNamespace(
        performance_control=SimpleNamespace(
            source_id="internal",
            transport_running=False,
            transport_paused=False,
        ),
        transport=SimpleNamespace(
            running=False,
            paused=False,
            bar_index=0,
            beat_index=0,
        ),
        performance_timeline=SimpleNamespace(
            arm=lambda **values: armed.update(values),
        ),
        events=SimpleNamespace(
            publish=lambda name, **values: published.append((name, values)),
        ),
    )

    Application.arm_performance_timeline(app)

    assert armed["transport_running"] is False
    assert published[-1][1]["waiting_for_transport"] is True


def test_timeline_arm_starts_from_current_internal_position() -> None:
    armed: dict[str, object] = {}
    published: list[tuple[str, dict[str, object]]] = []
    app = SimpleNamespace(
        performance_control=SimpleNamespace(
            source_id="internal",
            transport_running=False,
            transport_paused=False,
        ),
        transport=SimpleNamespace(
            running=True,
            paused=False,
            bar_index=12,
            beat_index=2,
        ),
        performance_timeline=SimpleNamespace(
            arm=lambda **values: armed.update(values),
        ),
        events=SimpleNamespace(
            publish=lambda name, **values: published.append((name, values)),
        ),
    )

    Application.arm_performance_timeline(app)

    assert armed["current_bar"] == 12
    assert armed["current_beat"] == 3
    assert armed["transport_running"] is True
    assert published[-1][1]["waiting_for_transport"] is False


def test_control_tick_passes_latest_macro_values_to_auto_performance() -> None:
    macro_values = {"chaos": 0.1, "density": 0.2}
    director = AutomationDirector(seed=5)

    def evaluate_modulation() -> None:
        macro_values.update({"chaos": 0.91, "density": 0.82})

    app = SimpleNamespace(
        midi_input=SimpleNamespace(drain=lambda _limit: 0),
        transport=SimpleNamespace(tick=lambda: []),
        submit_control_event=lambda _event: None,
        process_control_events=lambda: 0,
        _tick_external_performance_timeline=lambda: None,
        process_audio_frames=lambda: 0,
        _tick_scene_morph=lambda: None,
        _modulation_sources=lambda: {},
        _automation_musical_context=lambda _sources: (0.3, 0.4),
        performance_control=SimpleNamespace(intensity=0.5, bar_index=16),
        apply_modulation=evaluate_modulation,
        performance_macro_values=lambda: dict(macro_values),
        automation=director,
        _monitor_performance_mode=lambda: None,
    )

    Application.tick_performance_control(app)

    assert director._macro_values["chaos"] == 0.91
    assert director._macro_values["density"] == 0.82


def test_generator_preview_dimensions_are_bounded_and_full_resolution_is_available() -> None:
    service = GeneratorRasterService()
    try:
        assert service._dimensions("geometry") == (1200, 675)
        assert service._dimensions("waveform") == (1200, 675)
        assert service._dimensions("text") == (800, 450)
        assert service._dimensions("geometry", full_resolution=True) == (1600, 900)
    finally:
        service.shutdown()
        service._worker_thread.join(timeout=2.0)


def test_gpu_uniform_changes_reuse_static_generator_fingerprint() -> None:
    service = GeneratorRasterService()
    try:
        settings = normalize_settings("geometry", {})
        original = service.fingerprint_for("geometry-layer", "geometry", settings)

        settings["animation_speed"] = float(settings["animation_speed"]) + 0.5

        assert service.fingerprint_for("geometry-layer", "geometry", settings) == original

        settings["line_width"] = float(settings["line_width"]) + 1.0

        assert service.fingerprint_for("geometry-layer", "geometry", settings) != original
    finally:
        service.shutdown()
        service._worker_thread.join(timeout=2.0)


def test_waveform_content_changes_remain_part_of_raster_fingerprint() -> None:
    service = GeneratorRasterService()
    try:
        settings = normalize_settings("waveform", {})
        original = service.fingerprint_for("waveform-layer", "waveform", settings)

        settings["amplitude"] = min(0.48, float(settings["amplitude"]) + 0.05)

        assert service.fingerprint_for("waveform-layer", "waveform", settings) != original
        assert service._max_waveform_update_hz == 4.0
    finally:
        service.shutdown()
        service._worker_thread.join(timeout=2.0)
