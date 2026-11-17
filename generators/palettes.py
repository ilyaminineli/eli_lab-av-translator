"""Curated four-colour looks inspired by traditional Japanese colour families.

The named looks provide primary, accent and background colours for generator
layers. Import the original ACO file separately if exact source swatches are needed.
"""

from __future__ import annotations

import struct
from pathlib import Path

JP_PALETTE_LOOKS = {
    "Sakura · 桜": ["#F8C3CD", "#F4A7B9", "#FEDFE1", "#DC9FB4"],
    "Beni · 紅": ["#CB1B45", "#8E354A", "#B5495B", "#FFFFFB"],
    "Matcha · 抹茶": ["#7BA23F", "#91AD70", "#42602D", "#FCFAF2"],
    "Ai · 藍": ["#006284", "#2B5F75", "#577C8A", "#FFFFFB"],
    "Fuji · 藤": ["#8A6BBE", "#8F77B5", "#B28FCE", "#3C2F41"],
    "Kitsune · 狐": ["#C46243", "#DB8E71", "#6A4028", "#FCFAF2"],
    "Yamabuki · 山吹": ["#FFC408", "#E9CD4C", "#A28C37", "#554236"],
    "Sumi · 墨": ["#0B1013", "#787878", "#BDC0BA", "#FFFFFB"],
    "Shinbashi · 新橋": ["#00AA90", "#66BAB7", "#4F726C", "#0B1013"],
    "Riso · リソ": ["#D0104C", "#FFC408", "#8A6BBE", "#FCFAF2"],
}


def palette_look(name: str) -> dict[str, str | list[str]]:
    colours = JP_PALETTE_LOOKS[name]
    return {
        "name": name,
        "primary_color": colours[0],
        "secondary_color": colours[1],
        "background_color": colours[3],
        "colors": list(colours),
    }


def random_palette_look(rng) -> dict[str, str | list[str]]:
    import random

    chooser = rng if rng is not None else random
    return palette_look(chooser.choice(tuple(JP_PALETTE_LOOKS)))


def palette_names() -> list[str]:
    return list(JP_PALETTE_LOOKS)


def import_aco_palette(path: str | Path) -> list[str]:
    """Import Photoshop ACO RGB/grayscale swatches as named four-colour looks."""
    data = Path(path).expanduser().read_bytes()
    offset = 0
    swatches: list[tuple[str, str]] = []
    while offset + 4 <= len(data):
        version, count = struct.unpack_from(">HH", data, offset)
        offset += 4
        if version not in (1, 2) or count > 4096:
            break
        if version == 2:
            swatches.clear()
        for index in range(count):
            if offset + 10 > len(data):
                raise ValueError("ACO palette is truncated.")
            colour_space, c1, c2, c3, _c4 = struct.unpack_from(">5H", data, offset)
            offset += 10
            name = ""
            if version == 2:
                if offset + 4 > len(data):
                    raise ValueError("ACO swatch name is truncated.")
                name_length = struct.unpack_from(">I", data, offset)[0]
                offset += 4
                byte_length = name_length * 2
                if name_length > 1024 or offset + byte_length > len(data):
                    raise ValueError("ACO swatch name has an invalid length.")
                raw_name = data[offset: offset + byte_length]
                offset += byte_length
                name = raw_name.decode("utf-16-be", errors="replace").rstrip(chr(0))
            if colour_space == 0:
                rgb = tuple(round(value / 65535 * 255) for value in (c1, c2, c3))
            elif colour_space == 8:
                grey = round(c1 / 10000 * 255)
                rgb = (grey, grey, grey)
            else:
                continue
            hex_value = "#{:02X}{:02X}{:02X}".format(*rgb)
            swatches.append((name or f"JP {index + 1:03d}", hex_value))
    if not swatches:
        raise ValueError("No RGB or grayscale swatches were found in this ACO file.")
    imported: list[str] = []
    for group_index in range(0, len(swatches), 4):
        group = swatches[group_index: group_index + 4]
        if len(group) < 2:
            break
        while len(group) < 4:
            group.append(group[-1])
        first_name = group[0][0]
        label = f"ACO · {first_name[:24]} · {group_index // 4 + 1:02d}"
        JP_PALETTE_LOOKS[label] = [colour for _name, colour in group]
        imported.append(label)
    return imported
