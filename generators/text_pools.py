from __future__ import annotations

import random
import re
from functools import lru_cache
from pathlib import Path

import unicodedata

from config import PROJECT_ROOT

# Curated phrases are retained as a reliable fallback and for short-form collage text.
TEXT_POOLS: dict[str, dict[str, tuple[str, ...]]] = {
    "memory": {
        "en": (
            "MEMORY", "AFTERIMAGE", "ARCHIVE", "REMNANT", "RECALL", "ERASURE",
            "ECHO", "TRACE", "REMEMBER", "NO RETURN", "THE SHAPE OF LOSS",
            "NOTHING STAYS",
        ),
        "ja": (
            "記憶", "残像", "記録", "痕跡", "忘却", "反復", "不在", "回想",
            "余白", "消去", "残響", "帰れない",
        ),
    },
    "body": {
        "en": (
            "BODY", "SKIN", "BLOOD", "TOUCH", "HUNGER", "DESIRE", "GENDER",
            "BREATH", "VEIL", "SENSATION", "THE OTHER",
        ),
        "ja": (
            "身体", "皮膚", "血", "接触", "空腹", "欲望", "性", "呼吸",
            "仮面", "感覚", "他者", "輪郭",
        ),
    },
    "signal": {
        "en": (
            "SIGNAL", "NOISE", "STATIC", "TRANSMISSION", "FEEDBACK", "CARRIER",
            "FREQUENCY", "INTERRUPT", "REBOOT", "ERROR", "LOST CONNECTION",
            "DECODE",
        ),
        "ja": (
            "信号", "雑音", "静電気", "伝送", "反響", "搬送波", "周波数",
            "中断", "再起動", "誤差", "接続不能", "解読",
        ),
    },
    "ritual": {
        "en": (
            "RITUAL", "OFFERING", "WITNESS", "THRESHOLD", "CURSE", "TOLERANCE",
            "GAZE", "VESSEL", "RETURN", "PROOF", "COLLECTION", "SACRED ERROR",
        ),
        "ja": (
            "儀式", "供物", "証人", "境界", "呪い", "寛容", "視線", "器",
            "帰還", "証明", "収集", "聖なる誤差",
        ),
    },
    "identity": {
        "en": (
            "IDENTITY", "INTEGRATION", "OUTSIDER", "BLIND SPOT", "MIRROR",
            "DOUBLE", "ALIAS", "NO CATEGORY", "BECOMING", "UNDEFINED",
            "ANOTHER NAME",
        ),
        "ja": (
            "自己", "統合", "異邦人", "盲点", "鏡", "分身", "別名", "分類不能",
            "変容", "未定義", "もう一つの名",
        ),
    },
    "queer": {
        "en": (
            "QUEER", "NONBINARY", "GENDERQUEER", "GENDERFLUID", "ANDROGYNY",
            "ANDROGYNOUS", "AGENDER", "BIGENDER", "TRANSGENDER", "INTERSEX",
            "ASEXUAL", "AROMANTIC", "BISEXUAL", "PANSEXUAL", "SAPPHIC",
            "ACHILLEAN", "DEMISEXUAL", "PRONOUNS", "THEY / THEM",
            "SHE / THEY", "HE / THEY", "NEOPRONOUNS", "CHOSEN FAMILY",
            "CHOSEN NAME", "GENDER EUPHORIA", "SELF-DEFINITION",
            "NO FIXED FORM", "BEYOND THE BINARY", "FEMME", "BUTCH",
            "FLUIDITY", "I NAME MYSELF", "MY NAME IS MINE",
            "NOT A CATEGORY", "ROOM TO BECOME", "JOY WITHOUT PERMISSION",
            "MORE THAN ONE TRUTH", "NO EXPLANATION OWED",
        ),
        "ja": (
            "クィア", "クイア", "ノンバイナリー", "Xジェンダー",
            "ジェンダーフルイド", "アンドロジナス", "中性", "両性", "無性",
            "性自認", "ジェンダー表現", "代名詞", "選んだ名前",
            "自分らしさ", "ジェンダーのよろこび", "選んだ家族",
            "流動性", "ありのまま", "境界の外", "名前を選ぶ",
        ),
    },
    "random": {
        "en": (
            "LOVE", "RESET", "GHOST", "ANGEL", "BLIND", "EMPTY", "CURSE",
            "GAZE", "LONELINESS", "INTEGRATION", "DESIRE", "PROOF", "STATIC",
            "MERCY", "VANISH",
        ),
        "ja": (
            "愛", "再起動", "幽霊", "天使", "盲目", "空虚", "呪い", "視線",
            "孤独", "統合", "欲望", "証明", "雑音", "慈悲", "消失",
        ),
    },
}

_THEME_HINTS = {
    "memory": ("memory", "remember", "recall", "archive", "trace", "記憶", "記録", "忘却", "残像"),
    "body": ("body", "skin", "blood", "body", "touch", "身体", "皮膚", "血", "接触"),
    "signal": (
        "signal", "noise", "radio", "frequency", "transmission",
        "信号", "雑音", "周波数", "伝送",
    ),
    "ritual": ("ritual", "sacred", "offering", "altar", "curse", "儀式", "供物", "呪い", "神"),
    "identity": ("identity", "self", "person", "name", "mirror", "自己", "名前", "鏡", "他者"),
    "queer": (
        "queer", "nonbinary", "non-binary", "genderqueer", "genderfluid",
        "gender-fluid", "pronouns", "chosen name", "androgyny", "sapphic",
        "achillean", "gender euphoria", "クィア", "クイア", "ノンバイナリー",
        "Xジェンダー", "性自認", "代名詞", "ジェンダー表現",
    ),
}

# Dictionary files are user-editable, so filter offensive English headwords at
# ingestion time as a second layer of protection. Reclaimed "queer" is allowed.
_BLOCKED_ENGLISH_TERMS = frozenset({
    "fuck", "fucking", "shit", "bullshit", "bitch", "bastard", "asshole",
    "arsehole", "cunt", "dick", "piss", "motherfucker", "faggot", "fag",
    "dyke", "tranny", "shemale", "retard", "nigger", "nigga", "kike",
    "spic", "chink", "gook", "wetback", "beaner", "coon",
})


def _is_blocked_english_term(term: str) -> bool:
    normalized = unicodedata.normalize("NFKC", term).casefold()
    compact = re.sub(r"[^a-z]", "", normalized)
    return compact in _BLOCKED_ENGLISH_TERMS


def _dictionary_candidates(root: Path, language: str, theme: str) -> list[str]:
    """Return cached, normalised candidates for one dictionary version."""
    dictionary_dir = root.expanduser().resolve() / "dictionary"
    if not dictionary_dir.is_dir():
        return []
    signature = []
    for path in sorted(dictionary_dir.glob("*.txt")):
        try:
            stat = path.stat()
        except OSError:
            continue
        signature.append((str(path), stat.st_mtime_ns, stat.st_size))
    return list(_cached_dictionary_candidates(
        language,
        theme,
        tuple(signature),
    ))


@lru_cache(maxsize=32)
def _cached_dictionary_candidates(
        language: str,
        theme: str,
        signature: tuple[tuple[str, int, int], ...],
) -> tuple[str, ...]:
    """Build a bounded dictionary index once per language/theme/file version."""
    files = [Path(path) for path, _mtime, _size in signature]
    if language == "english":
        files = [path for path in files if path.stem.lower() in set("abcdefghijklmnopqrstuvwxyz")]
    elif language == "japanese":
        files = [path for path in files if path.name == "special_readings.txt"]
    else:
        files = [
            path for path in files
            if path.name in {"special_readings.txt", "supplementary_kanji.txt"}
        ]
    hints = tuple(item.casefold() for item in _THEME_HINTS.get(theme, ()))
    candidates: list[str] = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8-sig", errors="ignore") as handle:
                for raw in handle:
                    line = raw.strip()
                    if not line or len(line) > 72 or line.startswith("#"):
                        continue
                    parts = [
                        part.strip("・、。[](){}")
                        for part in re.split(r"[\t,;| ]+", line)
                    ]
                    parts = [part for part in parts if part]
                    if language == "english":
                        term = next(
                            (
                                part for part in parts
                                if re.fullmatch(r"[A-Za-z][A-Za-z'’-]*", part)
                            ),
                            "",
                        )
                    else:
                        term = next(
                            (
                                part for part in parts
                                if any(
                                "\u3040" <= char <= "\u30ff"
                                or "\u4e00" <= char <= "\u9fff"
                                for char in part
                            )
                            ),
                            "",
                        )
                    if not term or len(term) > 24:
                        continue
                    if language == "english" and _is_blocked_english_term(term):
                        continue
                    if hints and not any(hint in line.casefold() for hint in hints):
                        continue
                    candidates.append(
                        term.upper() if language == "english" else term
                    )
        except OSError:
            continue
    # The immutable cached tuple prevents callers from mutating the shared index.
    return tuple(list(dict.fromkeys(candidates))[:12000])


def random_text_sample(
        language: str = "bilingual",
        theme: str = "random",
        count: int = 16,
        seed: int | None = None,
        dictionary_path: str | Path | None = None,
        use_dictionary: bool = True,
) -> str:
    """Return a seeded English/Japanese phrase set, optionally enriched from local dictionaries."""
    if language not in {"english", "japanese", "bilingual"}:
        language = "bilingual"
    if theme not in TEXT_POOLS:
        theme = "random"
    rng = random.Random(seed)
    pool = TEXT_POOLS[theme]
    english = list(pool["en"])
    japanese = list(pool["ja"])
    if use_dictionary:
        root = Path(dictionary_path) if dictionary_path else PROJECT_ROOT
        if language in {"english", "bilingual"}:
            english.extend(_dictionary_candidates(root, "english", theme))
        if language in {"japanese", "bilingual"}:
            japanese.extend(_dictionary_candidates(root, "japanese", theme))
    english = list(dict.fromkeys(english))
    japanese = list(dict.fromkeys(japanese))
    if language == "english":
        source = english
    elif language == "japanese":
        source = japanese
    else:
        source = [item for pair in zip(english, japanese) for item in pair]
    sample_count = max(1, min(60, int(count)))
    if not source:
        source = list(pool["en"] if language == "english" else pool["ja"])
    if sample_count <= len(source):
        selected = rng.sample(source, sample_count)
    else:
        selected = [rng.choice(source) for _ in range(sample_count)]
    return "\n".join(selected)
