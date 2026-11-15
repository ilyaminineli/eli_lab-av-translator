from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout


def configure_inspector_form(form: QFormLayout) -> QFormLayout:
    """Apply the shared responsive form policy used by inspector panels.

    Long field labels wrap above their controls on narrow docks. Fields remain
    expandable, labels stay left-aligned, and row/column spacing stays consistent.
    """
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    form.setHorizontalSpacing(8)
    form.setVerticalSpacing(8)
    return form
