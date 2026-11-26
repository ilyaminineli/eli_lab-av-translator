from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from core.composition import Composition

PROJECT_FORMAT = "eli_lab_av_translator"
PROJECT_SCHEMA_VER = 2


class ProjectManager:
    """Read/write portable project files without copying source media."""

    def __init__(self) -> None:
        self.last_app_state: dict[str, Any] = {}

    def save(
        self,
        path: str | Path,
        composition: Composition,
        decks: list[dict[str, Any]] | None = None,
        app_state: dict[str, Any] | None = None,
    ) -> Path:
        destination = Path(path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": PROJECT_FORMAT,
            "schema_version": PROJECT_SCHEMA_VER,
            "project": {"name": composition.name},
            "composition": composition.to_dict(),
            "decks": decks or [],
            "app_state": app_state or {},
        }
        temporary = destination.with_name(destination.name + ".tmp")
        try:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        return destination

    def load(self, path: str | Path) -> tuple[Composition, list[dict[str, Any]]]:
        source = Path(path).expanduser().resolve()
        payload = json.loads(source.read_text(encoding="utf-8"))
        if payload.get("format") != PROJECT_FORMAT:
            raise ValueError("This file is not an eli_lab AVTranslator project.")
        version = int(payload.get("schema_version", 0))
        if version > PROJECT_SCHEMA_VER:
            raise ValueError(
                f"Project schema {version} is newer than supported schema "
                f"{PROJECT_SCHEMA_VER}."
            )
        composition = Composition.from_dict(payload.get("composition", {}))
        decks = payload.get("decks", [])
        if not isinstance(decks, list):
            raise ValueError("Project deck data must be a list.")
        self.last_app_state = payload.get("app_state", {})
        if not isinstance(self.last_app_state, dict):
            self.last_app_state = {}
        return composition, decks
