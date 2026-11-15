from __future__ import annotations

import json
import zipfile

import pytest

from config import APP_VER
from scripts.package_release import COMPRESSION_METHODS, create_release_archive


@pytest.mark.parametrize("compression", tuple(COMPRESSION_METHODS))
def test_versioned_release_archives_use_selected_zip_compression(
    tmp_path, compression: str
) -> None:
    binary = tmp_path / "AVTranslator.exe"
    binary.write_bytes(b"ELI-LAB-AVT-BUILD\x00" * 512)
    archive_path = create_release_archive(
        binary_path=binary,
        platform_id="windows-x64",
        compression=compression,
        level=6,
        output_dir=tmp_path / "releases",
    )

    assert archive_path.is_file()
    assert f"-{APP_VER}-windows-x64.zip" in archive_path.name
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert archive.read(binary.name) == binary.read_bytes()
        manifest = json.loads(archive.read("release-manifest.json"))
        assert manifest["platform"] == "windows-x64"
        assert manifest["compression"] == compression
        assert archive.getinfo(binary.name).compress_type == COMPRESSION_METHODS[compression]


def test_release_archive_rejects_missing_binary(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        create_release_archive(
            binary_path=tmp_path / "missing.exe",
            platform_id="windows-x64",
            output_dir=tmp_path / "releases",
        )


@pytest.mark.parametrize(
    ("compression", "level"),
    (("deflate", 10), ("bzip2", 0)),
)
def test_release_archive_validates_compression_levels(
    tmp_path, compression: str, level: int
) -> None:
    binary = tmp_path / "avtranslator"
    binary.write_bytes(b"binary")
    with pytest.raises(ValueError):
        create_release_archive(
            binary_path=binary,
            platform_id="linux-x86_64",
            compression=compression,
            level=level,
            output_dir=tmp_path / "releases",
        )
