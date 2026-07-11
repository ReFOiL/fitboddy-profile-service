from __future__ import annotations

import re

# Letters/digits (any script), spaces, hyphen, apostrophe. 2–64 chars.
_NAME_RE = re.compile(r"^[\w](?:[\w \-']{0,62}[\w])?$", re.UNICODE)

# Short preset list for UI/meta only. Rare gear = custom display name.
CANONICAL_EQUIPMENT: tuple[tuple[str, str], ...] = (
    ("dumbbells", "Гантели"),
    ("barbell", "Штанга"),
    ("kettlebell", "Гиря"),
    ("resistance_bands", "Эспандеры / резинки"),
    ("treadmill", "Беговая дорожка"),
)

CANONICAL_EQUIPMENT_VALUES = {value for value, _label in CANONICAL_EQUIPMENT}


def normalize_equipment_name(raw: str) -> str | None:
    """Normalize to a canonical slug or a cleaned custom display name."""
    value = " ".join(raw.strip().split())
    if not value:
        return None

    folded = value.casefold()
    if folded == "none":
        return None

    for slug, label in CANONICAL_EQUIPMENT:
        if folded == slug.casefold() or folded == label.casefold():
            return slug

    if len(value) < 2 or len(value) > 64:
        return None
    if not _NAME_RE.fullmatch(value):
        return None
    return value


def normalize_equipment_list(items: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = normalize_equipment_name(item)
        if value is None:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(value)
    return normalized


# Back-compat alias
normalize_equipment_slug = normalize_equipment_name
