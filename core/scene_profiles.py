from __future__ import annotations

from dataclasses import asdict, dataclass

from effects.settings import PSETS
from generators.palettes import palette_names


@dataclass
class SceneProfile:
    scene_id: str
    label: str
    intensity: float = 0.5
    master_look: str = "Clean"
    palette: str = "Sumi · 墨"

    def normalize(self) -> None:
        self.scene_id = str(self.scene_id).strip()
        self.label = str(self.label).strip()[:80] or self.scene_id
        self.intensity = max(0.0, min(1.0, float(self.intensity)))
        if self.master_look not in PSETS:
            self.master_look = "Clean"
        if self.palette not in palette_names():
            self.palette = palette_names()[0]

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)


_SCENE_DEFAULTS = (
    ("in", "Opening", 0.12, "Clean", "Sumi · 墨"),
    ("exp", "Expansion", 0.28, "Dream Haze", "Sakura · 桜"),
    ("tm_a", "Theme A", 0.45, "Sakura Fade", "Sakura · 桜"),
    ("trns", "Transition", 0.34, "Indigo Night", "Ai · 藍"),
    ("dev", "Development", 0.62, "Cold Steel", "Ai · 藍"),
    ("fr", "Frenzy", 0.84, "Digital Damage", "Beni · 紅"),
    ("ssp", "Suspension", 0.24, "Noh Theatre", "Fuji · 藤"),
    ("rtrns", "Return", 0.46, "Shin-hanga", "Matcha · 抹茶"),
    ("rc", "Recapitulation", 0.70, "Bleach Bypass", "Beni · 紅"),
    ("rc_w", "Wide Recapitulation", 1.0, "Infrared", "Riso · リソ"),
    ("peak", "Peak", 1.0, "Digital Damage", "Riso · リソ"),
    ("intd", "Interlude", 0.30, "Dream Haze", "Fuji · 藤"),
    ("s_s", "Second Surge", 1.0, "Digital Damage", "Kitsune · 狐"),
    ("rls", "Release", 0.42, "Shin-hanga", "Yamabuki · 山吹"),
    ("c", "Coda", 0.14, "16mm Film", "Sumi · 墨"),
    ("end", "End", 0.0, "Clean", "Sumi · 墨"),
)


class SceneProfileRegistry:
    """Persistable visual interpretation of musical scene IDs."""

    def __init__(self, profiles: list[SceneProfile] | None = None) -> None:
        if profiles is None:
            profiles = [
                SceneProfile(scene_id, label, intensity, look, palette)
                for scene_id, label, intensity, look, palette in _SCENE_DEFAULTS
            ]
        self._profiles: dict[str, SceneProfile] = {}
        for profile in profiles:
            profile.normalize()
            self._profiles[profile.scene_id] = profile

    def get(self, scene_id: str) -> SceneProfile:
        key = str(scene_id)
        if key not in self._profiles:
            profile = SceneProfile(key, key.replace("_", " ").title())
            profile.normalize()
            self._profiles[key] = profile
        return self._profiles[key]

    def all(self) -> list[SceneProfile]:
        return list(self._profiles.values())

    def update(self, profile: SceneProfile) -> None:
        profile.normalize()
        self._profiles[profile.scene_id] = profile

    def to_dict(self) -> list[dict[str, object]]:
        return [profile.to_dict() for profile in self._profiles.values()]

    def load_dict(self, values: object) -> None:
        if not isinstance(values, list):
            return
        profiles: list[SceneProfile] = []
        for item in values:
            if not isinstance(item, dict):
                continue
            try:
                profile = SceneProfile(
                    scene_id=str(item["scene_id"]),
                    label=str(item.get("label", item["scene_id"])),
                    intensity=float(item.get("intensity", 0.5)),
                    master_look=str(item.get("master_look", "Clean")),
                    palette=str(item.get("palette", palette_names()[0])),
                )
                profile.normalize()
                profiles.append(profile)
            except (KeyError, TypeError, ValueError):
                continue
        if profiles:
            self._profiles = {profile.scene_id: profile for profile in profiles}
