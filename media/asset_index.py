"""Searchable index for bundled and user-provided visual assets."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

IMG_EXNS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".apng", ".tif", ".tiff"}
VID_EXNS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


@dataclass(frozen=True)
class VisualAsset:
    id: str
    name: str
    path: str
    kind: str
    category: str
    tags: tuple[str, ...]
    purposes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _classify(path: Path, root: Path) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    relative = path.relative_to(root)
    parts = [
        part.lower().replace("_", " ").replace("-", " ") for part in relative.parts[:-1]
    ]
    stem = path.stem.lower().replace("_", " ").replace("-", " ")
    context = " ".join(parts + [stem])
    tags = set(parts)
    tags.update(word for word in stem.split() if len(word) > 2)
    purposes = {"overlay", "texture"}
    if any(word in context for word in ("paper", "film", "grunge", "ink", "fabric")):
        purposes.update(("postproduction", "surface", "distress"))
    if "normal" in context:
        purposes.update(("normal map", "material"))
    if "roughness" in context:
        purposes.update(("roughness map", "material"))
    if "displacement" in context or "height map" in context:
        purposes.update(("displacement map", "geometry", "material"))
    if "ambient occlusion" in context or "ao" in path.stem.lower().split("_"):
        purposes.update(("ambient occlusion", "material"))
    if "specular" in context:
        purposes.update(("specular map", "material"))
    if any(word in context for word in ("mask", "matte", "alpha", "silhouette")):
        purposes.update(("mask", "track matte"))
    if any(
        word in context
        for word in ("metal", "wood", "stone", "concrete", "bark", "clay")
    ):
        purposes.update(("material", "background", "geometry"))
    if any(
        word in context for word in ("particle", "dust", "smoke", "atmosphere", "spark")
    ):
        purposes.update(("particles", "atmosphere", "overlay"))
    if any(
        word in context for word in ("wall", "floor", "ceiling", "sky", "landscape")
    ):
        purposes.update(("background", "environment"))
    category = parts[0] if parts else "uncategorized"
    return category, tuple(sorted(tags)), tuple(sorted(purposes))


class VisualAssetIndex:
    """Small deterministic index; paths remain relative to the selected library root."""

    def __init__(self, roots: list[str | Path] | None = None) -> None:
        self.roots = [Path(root).expanduser().resolve() for root in (roots or [])]
        self.assets: list[VisualAsset] = []

    def scan(self) -> list[VisualAsset]:
        found: dict[str, VisualAsset] = {}
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file() or path.name.startswith("."):
                    continue
                suffix = path.suffix.lower()
                if suffix not in IMG_EXNS | VID_EXNS:
                    continue
                kind = "video" if suffix in VID_EXNS else "image"
                category, tags, purposes = _classify(path, root)
                identity = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
                found[identity] = VisualAsset(
                    id=identity,
                    name=path.stem.replace("_", " ").replace("-", " "),
                    path=str(path),
                    kind=kind,
                    category=category,
                    tags=tags,
                    purposes=purposes,
                )
        self.assets = list(found.values())
        return list(self.assets)

    def search(
        self,
        query: str = "",
        purpose: str | None = None,
        kind: str | None = None,
        category: str | None = None,
    ) -> list[VisualAsset]:
        terms = [term.lower() for term in query.split() if term]
        result = []
        for asset in self.assets:
            haystack = " ".join(
                (asset.name, asset.category, *asset.tags, *asset.purposes)
            ).lower()
            if terms and not all(term in haystack for term in terms):
                continue
            if purpose and purpose.lower() not in asset.purposes:
                continue
            if kind and kind != asset.kind:
                continue
            if category and category.lower() != asset.category:
                continue
            result.append(asset)
        return result
