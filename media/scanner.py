from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterator
from pathlib import Path

from media.models import MediaAsset

_LOG = logging.getLogger(__name__)
SUPPORTED_VID_EXNS = {
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg",
    ".wmv", ".mts", ".m2ts", ".ogv",
}


class MediaScanner:
    """Find local video files and probe their basic stream metadata."""

    @staticmethod
    def collection_id_for(folder: str | Path) -> str:
        root = Path(folder).expanduser().resolve()
        return hashlib.sha1(str(root).casefold().encode("utf-8")).hexdigest()[:16]

    def scan_folder(self, folder: str | Path, recursive: bool = True) -> list[MediaAsset]:
        root = Path(folder).expanduser().resolve()
        if not root.is_dir():
            raise NotADirectoryError(f"Media folder does not exist: {root}")
        collection_id = self.collection_id_for(root)
        paths: Iterator[Path]
        paths = root.rglob("*") if recursive else root.iterdir()
        assets: list[MediaAsset] = []
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_VID_EXNS:
                continue
            try:
                stat = path.stat()
                asset_id = hashlib.sha1(
                    str(path.resolve()).casefold().encode("utf-8")
                ).hexdigest()[:20]
                details = self.probe_file(path)
                assets.append(
                    MediaAsset(
                        id=asset_id,
                        path=str(path.resolve()),
                        collection_id=collection_id,
                        name=path.name,
                        duration=details.get("duration"),
                        width=details.get("width"),
                        height=details.get("height"),
                        fps=details.get("fps"),
                        codec=details.get("codec"),
                        status=details.get("status", "ready"),
                        file_size=stat.st_size,
                        modified_at=stat.st_mtime,
                    )
                )
            except OSError:
                _LOG.exception("Could not inspect media file %s", path)
        return sorted(assets, key=lambda item: item.name.casefold())

    @staticmethod
    def probe_file(path: str | Path) -> dict[str, object]:
        try:
            import av
        except ImportError:
            return {"status": "unprobed"}

        try:
            with av.open(str(path)) as container:
                video_streams = [stream for stream in container.streams if stream.type == "video"]
                if not video_streams:
                    return {"status": "unsupported"}
                stream = video_streams[0]
                duration = None
                if stream.duration is not None and stream.time_base is not None:
                    duration = float(stream.duration * stream.time_base)
                elif container.duration is not None:
                    duration = float(container.duration / av.time_base)
                rate = float(stream.average_rate) if stream.average_rate else None
                return {
                    "duration": duration,
                    "width": int(stream.codec_context.width or 0) or None,
                    "height": int(stream.codec_context.height or 0) or None,
                    "fps": rate,
                    "codec": stream.codec_context.name,
                    "status": "ready",
                }
        except Exception as exc:
            _LOG.warning("Unable to probe %s: %s", path, exc)
            return {"status": "error"}
