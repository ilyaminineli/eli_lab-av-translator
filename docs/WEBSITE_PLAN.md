# Website content and design plan

> **Implementation status — 14 November 2026:** The first website implementation is committed to `main`. The live structure uses Jekyll with Markdown pages, a shared editorial layout, a responsive monochrome stylesheet, English/Japanese homepage and documentation entry points, and a GitHub Pages Actions workflow. This document remains the content/design specification; the implementation notes at the end record what is now live in the repository.

## Purpose

The website should explain the software in the language of artists and performers, then lead visitors to a download, a first-session guide or the technical reference. It should feel like an old printed instrument manual or a small archival catalogue, not a generic SaaS landing page.

The site should be bilingual-ready. English and Japanese should be treated as equal content languages, not as a machine-translated footer. The application already has an English/Japanese language setting; the website can follow the same language choice.

## Core message

**eli_lab AV Translator is a live audiovisual instrument for building video collages, generative graphics and typographic scenes that move with music.**

Use this as the homepage's main description. Keep the distinction clear: this is a performance environment, not a conventional non-linear video editor or an audio workstation.

## Homepage copy

### Lead

**Make the image perform.**

Bring footage, typography, procedural graphics and visual effects into one live composition. Shape it with sound, rhythm, MIDI or Sonic Pi, then send it to a screen or projector.

### Supporting paragraph

eli_lab AV Translator is a Windows desktop instrument for live audiovisual work. Build a visual system from four video decks, generators, text, overlays and effects. Let it respond to a musical structure, perform it by hand, or combine both approaches.

### Primary links

- **Download the latest release** → GitHub Releases: https://github.com/ilyaminineli/eli_lab-av-translator/releases
- **Read the field manual** → Windows setup and the first-performance guide
- **Explore the source** → https://github.com/ilyaminineli/eli_lab-av-translator

Do not hard-code a version number or a direct asset filename into the website. The Releases page should remain the source of truth for the newest packaged build and its release notes.

## Recommended navigation

1. **Home** — concise product introduction, current screenshots, release link and quick orientation.
2. **Features** — footage decks, collage composition, text, generators, effects, audio reactivity, performance macros, Sonic Pi and projector output.
3. **Who it is for** — VJs, electronic musicians, audiovisual artists, generative artists and typography-led artists; include a short "not intended for" section.
4. **Manual** — installation, first launch, preparing footage, composing layers, running a performance, audio/MIDI/OSC, projector setup, saving and recovery.
5. **Wiki / Reference** — concepts, project format, OSC protocol, macro and modulation reference, generators, effects and troubleshooting.
6. **Downloads** — latest GitHub release, release notes, build requirements and known limitations.
7. **About** — project intent, author, source repository and contribution route.

The navigation should be small. Features and audience explain the product; the Manual teaches the workflow; the Wiki explains individual systems.

## Content source map

The website should render repository Markdown rather than maintain a second copy of technical explanations.

| Website section | Canonical source in the repository |
| --- | --- |
| Home and product introduction | [PRODUCT_OVERVIEW.md](PRODUCT_OVERVIEW.md) and this document |
| Features | [README.md](../README.md), [ROADMAP.md](ROADMAP.md), and milestone guides |
| Who it is for | [PRODUCT_OVERVIEW.md](PRODUCT_OVERVIEW.md) |
| Installation | [SETUP_WINDOWS.md](SETUP_WINDOWS.md) |
| Build and packaging | [BUILD_PYINSTALLER_WINDOWS.md](BUILD_PYINSTALLER_WINDOWS.md) |
| First performance | [README.md](../README.md), [M5_PERFORMANCE_ENVIRONMENT.md](M5_PERFORMANCE_ENVIRONMENT.md) |
| Generators and typography | [M2_GENERATIVE_VISUALS.md](M2_GENERATIVE_VISUALS.md), [M6_E_TYPOGRAPHY.md](M6_E_TYPOGRAPHY.md) |
| Automation and visual performance | [M5_AUTONOMOUS_PERFORMANCE.md](M5_AUTONOMOUS_PERFORMANCE.md), [M6_ADVANCED_PERFORMANCE_CONTROLS.md](M6_ADVANCED_PERFORMANCE_CONTROLS.md), [M7.md](M7.md) |
| Sonic Pi and OSC | [SONIC_PI_SONATA_INTEGRATION.md](SONIC_PI_SONATA_INTEGRATION.md) |
| Project files | [PROJECT_FORMAT.md](PROJECT_FORMAT.md) |
| Architecture and technical reference | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Release download | GitHub Releases page |

Keep product language and implementation detail separate. A visitor should not need to understand milestone names such as M2, M5 or M7 to understand what the application does. Milestone labels belong in the developer-facing roadmap.

## Manual and Wiki structure

The Manual should be task-oriented:

- Install and launch the application.
- Prepare a footage folder and build the media library.
- Load and operate the four video decks.
- Create a composition with layers, generators and overlays.
- Work with Text Art and typography.
- Apply master and per-layer effects.
- Set up audio analysis, MIDI and Performance Macros.
- Connect Sonic Pi through OSC.
- Build scenes and a bar/beat timeline.
- Open projector output.
- Save, restore and move a project.

The Wiki should be reference-oriented:

- Workspace and composition vocabulary.
- Deck and segment behaviour.
- Generator types and text raster behaviour.
- Blend modes and effect stages.
- Performance Macro and modulation concepts.
- OSC address and message reference.
- `.eliav` and `.eliset` file formats.
- Troubleshooting and performance diagnostics.
- Known omissions and hardware acceptance notes.

Existing technical guides can be reused directly where they are already understandable. When a guide is implementation-heavy, add a short artist-facing introduction before the technical detail rather than rewriting or duplicating the specification.

## Visual direction

The visual identity should share the application's restrained monochrome palette:

| Token | Value | Use |
| --- | --- | --- |
| Ink / page | `#090909` | Main background |
| Raised surface | `#101010` | Reading panels and navigation |
| Inset surface | `#151515` | Code blocks, tables and archive cards |
| Main text | `#eeeeee` | Body copy |
| Muted text | `#a3a3a3` | Captions and metadata |
| Rule / border | `#303030` | Dividers, frames and table rules |
| Active mark | `#dedede` / `#f0f0f0` | Selected links, focus and important controls |

The old-fashioned character should come from composition, typography and editorial details—not sepia colour. Use a restrained grid, thin rules, framed figures, folio-like page numbers, small index labels, chapter markers and occasional marginal notes. Avoid glossy gradients, rounded marketing cards, neon accents and oversized software-dashboard graphics.

A good visual reference is a dark technical field manual: the page is nearly black, type is quiet and carefully spaced, diagrams are schematic, and each page feels indexed and deliberate.

## Typography

### Application

- **English UI:** Segoe UI as the first choice. It is designed for clear on-screen interface text and is the normal Windows UI family.
- **Japanese UI:** Yu Gothic UI first, then Meiryo UI / BIZ UDGothic, followed by Noto Sans JP and the normal Qt/system fallback.
- Keep the application UI sans-serif and compact. Use regular weights for control labels and medium/bold weights only for section headings.
- Do not bundle proprietary Windows fonts. They should be resolved from the operating system.

### Website

- Use an editorial serif for large English headings, such as Newsreader with Georgia as a system fallback.
- Use Noto Serif JP or Yu Mincho for Japanese display headings if the site adopts a book-like title treatment.
- Keep body copy highly readable: Noto Sans for Latin text and Noto Sans JP for Japanese, with system sans-serif fallbacks.
- Use a monospace face for OSC addresses, code, values and technical identifiers.

Noto Sans JP is an open-font option with Japanese and Latin coverage and an SIL Open Font License entry in the Google Fonts repository. If font files are ever bundled with the application or website, include the required licence and copyright notices.

## Site implementation

The current implementation uses **Jekyll** because GitHub Pages can build it directly from the repository and the existing `docs/*.md` files can remain the canonical documentation source.

- `_config.yml` configures the site, relative Markdown links and page defaults.
- `_layouts/default.html` provides the shared masthead, language navigation and footer.
- `_layouts/doc.html` presents Markdown documentation in a consistent reader with a document rail.
- `index.html` and `ja/index.html` are separate English and Japanese homepage entry points.
- `style.css` defines the shared typography, grid, monochrome palette and responsive layouts.
- `docs/MANUAL.md`, `docs/WIKI.md`, `docs/ABOUT.md` and the corresponding `docs/ja/*.md` pages provide the artist-facing entry points.
- Existing technical Markdown guides remain in `docs/` and are linked from the Wiki and Manual rather than copied into standalone HTML.

The Pages workflow is `.github/workflows/pages.yml`. It builds the repository using the GitHub Pages Jekyll action and deploys the resulting artifact. Repository Pages settings and the first deployment still depend on GitHub's repository-level permissions and policy. An owner or administrator must enable **Settings → Pages → Build and deployment → GitHub Actions** once before the deployment workflow can configure the site. The workflow token in this repository cannot create the Pages site itself.

Keep release downloads pointed at the GitHub Releases page. Do not hard-code version numbers or direct executable filenames. The release page remains the source for current binaries, dates and notes.

## Screenshots and media

Use real application captures for feature pages: a full PERF workspace, a four-deck collage, a Text Art / generator panel, the modulation controls and projector output. Screenshots should show the real state of the application, not invented UI. Add short captions explaining what the visitor is seeing.

A small number of animated demonstrations may help explain visual behaviour, but keep them short and compressed. Every animated example should have a still image fallback and a caption.

## Release and trust information

The Downloads page should show:

- Latest version and release date as read from GitHub Releases.
- Windows build download and SHA-256 checksum when the release provides them.
- Release notes and known issues.
- Current system requirements.
- A plain statement that source media and Sonic Pi are installed separately.

Do not label the application production-stable until the target Windows/GPU, projector and sustained-performance acceptance runs have been completed. Distinguish automated test results from hardware validation.

## Editorial rules

- Explain outcomes before implementation details.
- Prefer verbs such as *compose*, *perform*, *shape*, *connect* and *project*.
- Explain technical terms the first time they appear.
- Do not claim that the application records a finished master, replaces a DAW, or edits video like a traditional NLE.
- Keep current capabilities, active development and future ideas clearly separate.
- Keep English and Japanese versions aligned in meaning and update them together.


## Implementation boundary and remaining work

The first pass intentionally uses a schematic HTML/CSS plate in place of a screenshot. It is labelled as a schematic, not a capture of the application. Real screenshots and short, optimized demonstrations should be added only after they can be captured from the running Windows application and validated for accuracy.

The initial English and Japanese homepages, Features, Manuals, Wiki, Downloads and About pages are present. The technical reference corpus is predominantly English; Japanese navigation marks English-only guides explicitly. Keep the two languages semantically aligned as translations are expanded.

Before treating the website as published, verify the first successful Pages deployment and inspect the generated home, representative Markdown guide, Japanese pages, responsive mobile layout and all internal links. GitHub Actions code checks do not verify the website's appearance in a real browser.
