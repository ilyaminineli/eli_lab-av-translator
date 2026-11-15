from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import APP_NAME, APP_SLUG, APP_VER  # noqa: E402

COMPRESSION_METHODS = {
    "stored": zipfile.ZIP_STORED,
    "deflate": zipfile.ZIP_DEFLATED,
    "bzip2": zipfile.ZIP_BZIP2,
    "lzma": zipfile.ZIP_LZMA,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_release_archive(
    binary_path: Path,
    platform_id: str,
    compression: str = "deflate",
    level: int = 6,
    output_dir: Path | None = None,
) -> Path:
    """Package one native executable and its notices as a versioned ZIP archive."""
    binary_path = Path(binary_path).expanduser().resolve()
    if not binary_path.is_file():
        raise FileNotFoundError(f"Build executable not found: {binary_path}")
    if compression not in COMPRESSION_METHODS:
        raise ValueError(
            f"Unsupported compression {compression!r}; "
            f"choose from {', '.join(COMPRESSION_METHODS)}."
        )
    if compression == "deflate" and not 0 <= int(level) <= 9:
        raise ValueError("Deflate compression level must be between 0 and 9.")
    if compression == "bzip2" and not 1 <= int(level) <= 9:
        raise ValueError("BZIP2 compression level must be between 1 and 9.")

    output_root = Path(output_dir or (ROOT / "dist" / "releases")).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    archive_path = output_root / f"{APP_SLUG}-{APP_VER}-{platform_id}.zip"
    method = COMPRESSION_METHODS[compression]

    manifest = {
        "application": APP_NAME,
        "version": APP_VER,
        "platform": platform_id,
        "binary": binary_path.name,
        "binary_size": binary_path.stat().st_size,
        "binary_sha256": sha256_file(binary_path),
        "archive_format": "zip",
        "compression": compression,
        "compression_level": (
            int(level) if compression in {"deflate", "bzip2"} else None
        ),
        "created_utc": datetime.now(UTC).isoformat(),
    }

    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=method,
        compresslevel=(
            int(level) if compression in {"deflate", "bzip2"} else None
        ),
        allowZip64=True,
    ) as archive:
        archive.write(binary_path, arcname=binary_path.name)

        for relative_path, archive_name in (
            (ROOT / "README.md", "README.md"),
            (ROOT / "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md"),
            (ROOT / "build" / "pyinstaller-build-report.txt", "build-report.txt"),
        ):
            if relative_path.is_file():
                archive.write(relative_path, arcname=archive_name)

        archive.writestr(
            "release-manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )

    with zipfile.ZipFile(archive_path, "r") as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            archive_path.unlink(missing_ok=True)
            raise RuntimeError(f"Release archive verification failed at {bad_member!r}.")

    archive_size = archive_path.stat().st_size
    print(f"Release archive: {archive_path}")
    print(f"Platform: {platform_id}")
    print(f"Compression: {compression}")
    if compression in {"deflate", "bzip2"}:
        print(f"Compression level: {level}")
    print(f"Archive size: {archive_size / (1024 * 1024):.1f} MiB")
    print(f"Archive SHA-256: {sha256_file(archive_path)}")
    return archive_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a versioned, compressed release archive for a native build."
    )
    parser.add_argument("--binary", required=True, type=Path, help="PyInstaller output file.")
    parser.add_argument(
        "--platform",
        required=True,
        choices=("windows-x64", "linux-x86_64"),
        help="Target platform label used in the archive filename.",
    )
    parser.add_argument(
        "--compression",
        choices=tuple(COMPRESSION_METHODS),
        default="deflate",
        help="ZIP compression method. Deflate is the compatibility default.",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=6,
        help="Deflate level 0-9 or BZIP2 level 1-9; ignored by stored/LZMA.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "dist" / "releases",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    create_release_archive(
        binary_path=args.binary,
        platform_id=args.platform,
        compression=args.compression,
        level=args.level,
        output_dir=args.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
