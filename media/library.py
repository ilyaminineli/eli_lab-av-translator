from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from time import time

from config import MEDIA_DB_PATH, THUMB_DIR
from media.models import MediaAsset
from media.scanner import MediaScanner


class MediaLibrary:
    """SQLite-backed media index. Cleanup operations never delete source footage."""

    _TEXT_SCHEMA = {
        "assets": (
            "id TEXT PRIMARY KEY",
            "path TEXT NOT NULL UNIQUE",
            "collection_id TEXT NOT NULL",
            "name TEXT NOT NULL",
            "duration REAL",
            "width INTEGER",
            "height INTEGER",
            "fps REAL",
            "codec TEXT",
            "thumbnail_path TEXT",
            "status TEXT NOT NULL",
            "file_size INTEGER NOT NULL",
            "modified_at REAL NOT NULL",
        ),
        "collections": (
            "id TEXT PRIMARY KEY",
            "root_path TEXT NOT NULL",
            "name TEXT NOT NULL",
            "imported_at REAL NOT NULL",
        ),
    }

    @classmethod
    def _repair_legacy_txt_affinity(cls, connection: sqlite3.Connection) -> None:
        """Repair 0.6.0 databases created while SQL TEXT types were abbreviated to TXT."""
        for table_name, definitions in cls._TEXT_SCHEMA.items():
            info = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
            if not any(str(column["type"]).strip().upper() == "TXT" for column in info):
                continue

            expected_columns = [definition.split()[0] for definition in definitions]
            actual_columns = [str(column["name"]) for column in info]
            if set(actual_columns) != set(expected_columns):
                # Do not risk dropping data from a database with an unknown extension.
                continue

            temporary_name = f"{table_name}__text_affinity_fix"
            connection.execute(f"DROP TABLE IF EXISTS {temporary_name}")
            connection.execute(
                f"CREATE TABLE {temporary_name} ({', '.join(definitions)})"
            )
            columns = ", ".join(expected_columns)
            connection.execute(
                f"INSERT INTO {temporary_name} ({columns}) "
                f"SELECT {columns} FROM {table_name}"
            )
            connection.execute(f"DROP TABLE {table_name}")
            connection.execute(
                f"ALTER TABLE {temporary_name} RENAME TO {table_name}"
            )

    def __init__(
            self,
            database_path: str | Path | None = None,
            thumbnail_directory: str | Path | None = None,
    ) -> None:
        self.database_path = Path(database_path or MEDIA_DB_PATH).expanduser()
        self.thumbnail_directory = Path(
            thumbnail_directory or THUMB_DIR
        ).expanduser()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.thumbnail_directory.mkdir(parents=True, exist_ok=True)
        self.scanner = MediaScanner()
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 15000")
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL UNIQUE,
                    collection_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    duration REAL,
                    width INTEGER,
                    height INTEGER,
                    fps REAL,
                    codec TEXT,
                    thumbnail_path TEXT,
                    status TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    modified_at REAL NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_assets_collection ON assets(collection_id)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS collections (
                    id TEXT PRIMARY KEY,
                    root_path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    imported_at REAL NOT NULL
                )
                """
            )

            # Earlier 0.6.0 builds accidentally declared text columns as TXT, which
            # SQLite treats as BLOB affinity. Rebuild only those known tables while
            # preserving their rows and the canonical TEXT/REAL/INTEGER declarations.
            self._repair_legacy_txt_affinity(connection)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_assets_collection ON assets(collection_id)"
            )

            # Upgrade older media databases which only stored collection IDs on assets.
            legacy_ids = connection.execute(
                """
                SELECT collection_id, MIN(path) AS sample_path
                FROM assets
                GROUP BY collection_id
                """
            ).fetchall()
            for row in legacy_ids:
                sample = Path(row["sample_path"])
                root = sample.parent
                # Older databases did not persist the imported root path.
                # Recover it by matching the historical collection hash against
                # the sample file's ancestor directories.
                for candidate in sample.parents:
                    if self.scanner.collection_id_for(candidate) == row["collection_id"]:
                        root = candidate
                        break
                connection.execute(
                    """
                    INSERT OR IGNORE INTO collections (id, root_path, name, imported_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (row["collection_id"], str(root), root.name or str(root), time()),
                )

    def add_folder(self, folder: str | Path, recursive: bool = True) -> list[MediaAsset]:
        root = Path(folder).expanduser().resolve()
        assets = self.scanner.scan_folder(root, recursive=recursive)
        if not assets:
            # Keep an imported empty folder visible so the user can choose to remove it.
            collection_id = self.scanner.collection_id_for(root)
        else:
            collection_id = assets[0].collection_id
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO collections (id, root_path, name, imported_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    root_path=excluded.root_path,
                    name=excluded.name
                """,
                (collection_id, str(root), root.name or str(root), time()),
            )
            for asset in assets:
                connection.execute(
                    """
                    INSERT INTO assets (
                        id, path, collection_id, name, duration, width, height,
                        fps, codec, thumbnail_path, status, file_size, modified_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        collection_id=excluded.collection_id,
                        name=excluded.name,
                        duration=excluded.duration,
                        width=excluded.width,
                        height=excluded.height,
                        fps=excluded.fps,
                        codec=excluded.codec,
                        thumbnail_path=CASE
                            WHEN assets.file_size != excluded.file_size
                              OR assets.modified_at != excluded.modified_at
                            THEN NULL
                            ELSE assets.thumbnail_path
                        END,
                        status=excluded.status,
                        file_size=excluded.file_size,
                        modified_at=excluded.modified_at
                    """,
                    (
                        asset.id, asset.path, asset.collection_id, asset.name,
                        asset.duration, asset.width, asset.height, asset.fps,
                        asset.codec, asset.thumbnail_path, asset.status,
                        asset.file_size, asset.modified_at,
                    ),
                )
            connection.execute(
                """
                DELETE FROM collections
                WHERE id NOT IN (SELECT DISTINCT collection_id FROM assets)
                  AND id != ?
                """,
                (collection_id,),
            )
        return assets

    def list_assets(self, collection_id: str | None = None) -> list[MediaAsset]:
        with self._connection() as connection:
            if collection_id:
                rows = connection.execute(
                    "SELECT * FROM assets WHERE collection_id=? ORDER BY name COLLATE NOCASE",
                    (collection_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM assets ORDER BY name COLLATE NOCASE"
                ).fetchall()
        return [MediaAsset.from_row(row) for row in rows]

    def list_collections(self) -> list[dict[str, object]]:
        """Return imported folders with their current indexed asset counts."""
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT c.id, c.root_path, c.name, COUNT(a.id) AS asset_count
                FROM collections AS c
                LEFT JOIN assets AS a ON a.collection_id = c.id
                GROUP BY c.id, c.root_path, c.name
                ORDER BY c.name COLLATE NOCASE, c.root_path COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_asset(self, asset_id: str) -> MediaAsset | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM assets WHERE id=?", (asset_id,)
            ).fetchone()
        return MediaAsset.from_row(row) if row else None

    def update_thumbnail(self, asset_id: str, thumbnail_path: str | Path) -> None:
        path = Path(thumbnail_path).expanduser().resolve()
        if not path.is_file():
            return
        with self._connection() as connection:
            connection.execute(
                "UPDATE assets SET thumbnail_path=? WHERE id=?",
                (str(path), asset_id),
            )

    def remove_collection(self, collection_id: str) -> int:
        """Remove one folder's index rows, never the original media files."""
        with self._connection() as connection:
            cursor = connection.execute(
                "DELETE FROM assets WHERE collection_id=?", (collection_id,)
            )
            removed = max(0, cursor.rowcount)
            connection.execute(
                "DELETE FROM collections WHERE id=?", (collection_id,)
            )
        self.cleanup_thumbnail_cache()
        return removed

    def clear_index(self) -> int:
        """Remove every indexed asset and collection without touching source footage."""
        with self._connection() as connection:
            count = int(connection.execute("SELECT COUNT(*) FROM assets").fetchone()[0])
            connection.execute("DELETE FROM assets")
            connection.execute("DELETE FROM collections")
        self.cleanup_thumbnail_cache()
        return count

    def remove_missing(self) -> int:
        """Prune records whose source files no longer exist."""
        with self._connection() as connection:
            rows = connection.execute("SELECT id, path FROM assets").fetchall()
            missing = [
                row["id"] for row in rows
                if not Path(row["path"]).is_file()
            ]
            connection.executemany(
                "DELETE FROM assets WHERE id=?", [(item,) for item in missing]
            )
            connection.execute(
                """
                DELETE FROM collections
                WHERE id NOT IN (SELECT DISTINCT collection_id FROM assets)
                """
            )
        self.cleanup_thumbnail_cache()
        return len(missing)

    def cleanup_thumbnail_cache(self) -> int:
        """Delete only cached thumbnails which are no longer referenced by an asset."""
        with self._connection() as connection:
            referenced = {
                str(Path(row[0]).expanduser().resolve())
                for row in connection.execute(
                    "SELECT thumbnail_path FROM assets WHERE thumbnail_path IS NOT NULL"
                )
            }

        removed = 0
        if not self.thumbnail_directory.is_dir():
            return removed
        for path in self.thumbnail_directory.glob("*.jpg"):
            try:
                if str(path.resolve()) not in referenced:
                    path.unlink(missing_ok=True)
                    removed += 1
            except OSError:
                continue
        return removed
