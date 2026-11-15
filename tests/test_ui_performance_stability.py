from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFormLayout

from core.application import Application
from ui.automation_panel import AutomationPanel
from ui.panel_layout import configure_inspector_form
from ui.performance_control_panel import PerformanceControlPanel


def test_inspector_form_policy_wraps_labels_and_expands_fields() -> None:
    form = QFormLayout()
    assert configure_inspector_form(form) is form

    assert form.rowWrapPolicy() == QFormLayout.RowWrapPolicy.WrapLongRows
    assert form.fieldGrowthPolicy() == QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
    assert form.horizontalSpacing() == 8
    assert form.verticalSpacing() == 8


def test_auto_perf_forms_use_the_shared_inspector_policy() -> None:
    qt_app = QApplication.instance() or QApplication([])
    application = Application()
    panel = AutomationPanel(application.media_library)
    try:
        forms = panel.findChildren(QFormLayout)
        assert len(forms) >= 2
        assert all(
            form.rowWrapPolicy() == QFormLayout.RowWrapPolicy.WrapLongRows
            and form.fieldGrowthPolicy()
            == QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
            for form in forms
        )
        qt_app.processEvents()
    finally:
        panel.close()
        application.shutdown()


def test_macro_drag_defers_modulation_to_the_30_fps_runtime_tick(
    monkeypatch,
) -> None:
    qt_app = QApplication.instance() or QApplication([])
    application = Application()
    panel = PerformanceControlPanel(application)
    apply_calls = 0

    def counted_apply() -> dict[str, float]:
        nonlocal apply_calls
        apply_calls += 1
        return {}

    monkeypatch.setattr(application, "apply_modulation", counted_apply)
    try:
        slider = panel.macro_sliders["chaos"]
        for value in range(1001):
            slider.setValue(value)

        # UI feedback and the normalized macro value update immediately, but
        # each pointer-move event must not trigger a second full modulation pass.
        assert application.performance_macro_values()["chaos"] == 1.0
        assert panel.macro_value_labels["chaos"].text() == "1.00"
        assert apply_calls == 0

        application.tick_performance_control()
        assert apply_calls == 1
        qt_app.processEvents()
    finally:
        panel.close()
        application.shutdown()
