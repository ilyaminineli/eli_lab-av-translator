from __future__ import annotations

from pathlib import Path

SITE = Path("_site")
REQUIRED_PAGES = (
    "index.html",
    "ja/index.html",
    "docs/PRODUCT_OVERVIEW/index.html",
    "docs/MANUAL/index.html",
    "docs/WIKI/index.html",
    "docs/ABOUT/index.html",
    "docs/ja/PRODUCT_OVERVIEW/index.html",
    "docs/ja/MANUAL/index.html",
    "docs/ja/WIKI/index.html",
)


def main() -> int:
    missing = [path for path in REQUIRED_PAGES if not (SITE / path).is_file()]
    stylesheet = SITE / "style.css"
    if not stylesheet.is_file():
        missing.append("style.css")

    if missing:
        print("Jekyll site is missing expected output:")
        for path in missing:
            print(f"  - {path}")
        return 1

    english = (SITE / "index.html").read_text(encoding="utf-8")
    japanese = (SITE / "ja/index.html").read_text(encoding="utf-8")
    english_manual = (SITE / "docs/MANUAL/index.html").read_text(encoding="utf-8")
    japanese_manual = (SITE / "docs/ja/MANUAL/index.html").read_text(encoding="utf-8")

    checks = {
        "English homepage title": "Make the" in english and "image" in english,
        "Japanese homepage copy": "映像を、" in japanese,
        "English homepage stylesheet": "/eli_lab-av-translator/style.css" in english,
        "Japanese navigation": "操作マニュアル" in japanese,
        "English Markdown manual rendered": "Field manual" in english_manual,
        "Japanese Markdown manual rendered": "操作マニュアル" in japanese_manual,
        "Japanese document language": 'lang="ja"' in japanese_manual,
    }
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} · {name}")
    if failed:
        return 1

    print(f"Jekyll site check passed · {len(REQUIRED_PAGES)} pages + stylesheet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
