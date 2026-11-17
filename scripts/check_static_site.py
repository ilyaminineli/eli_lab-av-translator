from __future__ import annotations

import posixpath
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html",
    "site/index.html",
    "site/features.html",
    "site/manual.html",
    "site/wiki.html",
    "site/downloads.html",
    "site/about.html",
    "site/guides/windows-setup.html",
    "site/guides/sonic-pi.html",
    "site/ja/index.html",
    "site/ja/features.html",
    "site/ja/manual.html",
    "site/ja/wiki.html",
    "site/ja/downloads.html",
    "site/ja/about.html",
    "site/ja/guides/windows-setup.html",
    "site/ja/guides/sonic-pi.html",
)


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.in_head = False
        self.has_head = False
        self.has_title = False
        self.has_charset = False
        self.has_viewport = False
        self.stylesheets: list[str] = []
        self.links: list[str] = []
        self.has_favicon = False
        self.in_primary_nav = False
        self._nav_anchor_href: str | None = None
        self._nav_anchor_text = ""
        self.primary_nav_links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.lang = str(attributes.get("lang") or "")
        if tag == "head":
            self.in_head = True
            self.has_head = True
        if tag == "nav" and "primary-nav" in str(attributes.get("class") or "").split():
            self.in_primary_nav = True
        if self.in_head and tag == "title":
            self.has_title = True
        if tag == "meta":
            if str(attributes.get("charset") or "").lower() == "utf-8":
                self.has_charset = True
            if str(attributes.get("name") or "").lower() == "viewport":
                self.has_viewport = True
        if tag == "link":
            href = str(attributes.get("href") or "")
            relation = str(attributes.get("rel") or "").lower().split()
            if href:
                self.links.append(href)
                if "stylesheet" in relation:
                    self.stylesheets.append(href)
                if "icon" in relation:
                    self.has_favicon = True
        if tag == "a":
            href = str(attributes.get("href") or "")
            if href:
                self.links.append(href)
                if self.in_primary_nav:
                    self._nav_anchor_href = href
                    self._nav_anchor_text = ""

    def handle_data(self, data: str) -> None:
        if self.in_primary_nav and self._nav_anchor_href is not None:
            self._nav_anchor_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.in_primary_nav and self._nav_anchor_href is not None:
            self.primary_nav_links.append(
                (self._nav_anchor_href, self._nav_anchor_text.strip())
            )
            self._nav_anchor_href = None
            self._nav_anchor_text = ""
        if tag == "nav" and self.in_primary_nav:
            self.in_primary_nav = False
        if tag == "head":
            self.in_head = False


def local_target(page: str, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    parent = posixpath.dirname(page)
    resolved = posixpath.normpath(posixpath.join(parent, unquote(parsed.path)))
    if resolved == ".":
        resolved = "index.html"
    return ROOT / resolved


def expected_primary_nav_targets(page: str) -> set[str]:
    """Return every public section expected in a page's global navigation."""
    if page == "index.html":
        home = "index.html"
        prefix = "site"
    elif page == "site/index.html":
        home = "site/index.html"
        prefix = "site"
    elif "/ja/" in f"/{page}":
        home = "site/ja/index.html"
        prefix = "site/ja"
    else:
        home = "index.html"
        prefix = "site"
    return {
        home,
        f"{prefix}/features.html",
        f"{prefix}/manual.html",
        f"{prefix}/wiki.html",
        f"{prefix}/guides/windows-setup.html",
        f"{prefix}/guides/sonic-pi.html",
        f"{prefix}/downloads.html",
        f"{prefix}/about.html",
    }


def main() -> int:
    problems: list[str] = []
    if not (ROOT / ".nojekyll").is_file():
        problems.append("Missing .nojekyll; GitHub Pages may invoke Jekyll.")
    if not (ROOT / "site/style.css").is_file():
        problems.append("Missing site/style.css.")

    for relative_path in PAGES:
        source = ROOT / relative_path
        if not source.is_file():
            problems.append(f"Missing page: {relative_path}")
            continue

        html = source.read_text(encoding="utf-8")
        inspector = PageInspector()
        inspector.feed(html)
        expected_lang = "ja" if "/ja/" in f"/{relative_path}" else "en"
        checks = (
            (html.lstrip().lower().startswith("<!doctype html>"), "HTML5 doctype"),
            (inspector.has_head, "head element"),
            (inspector.has_title, "title element"),
            (inspector.has_charset, "UTF-8 charset"),
            (inspector.has_viewport, "responsive viewport meta"),
            (inspector.lang == expected_lang, f"lang={expected_lang}"),
            (
                not any(token in html for token in ("{{", "{%", "---\n")),
                "no template/front-matter syntax",
            ),
            (bool(inspector.stylesheets), "stylesheet link"),
            (inspector.has_favicon, "application seal favicon"),
        )
        for passed, label in checks:
            if not passed:
                problems.append(f"{relative_path}: missing or invalid {label}")

        actual_nav_targets: set[str] = set()
        for href, _label in inspector.primary_nav_links:
            target = local_target(relative_path, href)
            if target is not None:
                try:
                    actual_nav_targets.add(target.relative_to(ROOT).as_posix())
                except ValueError:
                    pass
        for expected_target in expected_primary_nav_targets(relative_path):
            if expected_target not in actual_nav_targets:
                problems.append(
                    f"{relative_path}: primary navigation is missing {expected_target}"
                )

        for href in inspector.links:
            parsed_href = urlsplit(href)
            if (
                    parsed_href.path.lower().endswith(".md")
                    and not parsed_href.scheme
                    and not parsed_href.netloc
            ):
                problems.append(
                    f"{relative_path}: raw Markdown links are not public site routes: {href!r}"
                )
            target = local_target(relative_path, href)
            if target is not None and not target.is_file():
                problems.append(f"{relative_path}: broken local link {href!r}")

    if problems:
        print("Static site check failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"Static site check passed · {len(PAGES)} HTML pages and local links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
