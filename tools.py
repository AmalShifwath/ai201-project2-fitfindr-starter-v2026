"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    """Lowercase word/number tokens, split on anything that isn't one."""
    return set(_WORD_RE.findall(text.lower()))


def _size_matches(user_size: str, listing_size: str) -> bool:
    """
    True if a user's size token shows up as a whole token of the listing's
    size string.

    Tokenizing both sides and comparing whole tokens — rather than a plain
    substring test — is what keeps "M" from matching "US 9" and "L" from
    matching "XL". `"s" in "us 9"` is True and `"l" in "xl"` is True; neither
    of those is a real size match, and a tool that returns shoes for a "size
    M" top search reads like a broken search.
    """
    return bool(_tokens(user_size) & _tokens(listing_size))


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Matched case-insensitively by whole token — "M" matches
                     "S/M" because they share the token "m", but "L" does not
                     match "XL" because "l" and "xl" are different tokens.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first, each with the
        fields documented in utils/data_loader.load_listings (id, title,
        description, category, style_tags, size, condition, price, colors,
        brand, platform). At most config.SEARCH_RESULT_LIMIT of them.
        Returns an empty list when nothing matches — never None, never a
        raised exception.
    """
    candidates = load_listings()

    if max_price is not None:
        candidates = [c for c in candidates if c["price"] <= max_price]

    if size:
        candidates = [c for c in candidates if _size_matches(size, c["size"])]

    description_tokens = _tokens(description) if description else set()

    scored: list[tuple[int, dict]] = []
    for listing in candidates:
        searchable = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                " ".join(listing["style_tags"]),
            ]
        )
        score = len(description_tokens & _tokens(searchable))
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def _format_wardrobe(items: list[dict]) -> str:
    lines = []
    for item in items:
        colors = ", ".join(item.get("colors", []))
        tags = ", ".join(item.get("style_tags", []))
        notes = item.get("notes")
        line = f"- {item['name']} ({item['category']}; colors: {colors}; style: {tags})"
        if notes:
            line += f" — {notes}"
        lines.append(line)
    return "\n".join(lines)


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  May be empty.

    Returns:
        A non-empty string with outfit suggestions. With an empty wardrobe,
        returns general styling advice instead of raising or returning "".
    """
    items = wardrobe.get("items", [])
    item_desc = (
        f"{new_item['title']} — {new_item['category']}, "
        f"colors: {', '.join(new_item['colors'])}, "
        f"style: {', '.join(new_item['style_tags'])}"
    )

    if not items:
        prompt = (
            f"Someone is considering thrifting this item:\n{item_desc}\n\n"
            "They haven't told us what else they own. Suggest one or two "
            "general outfit ideas for this piece — what kind of pieces it "
            "would pair well with (e.g. 'a slim dark-wash jean and white "
            "sneakers'), not specific items from a closet we don't know "
            "about. Keep it to two or three sentences."
        )
    else:
        prompt = (
            f"Someone is considering thrifting this item:\n{item_desc}\n\n"
            f"Here is their existing wardrobe:\n{_format_wardrobe(items)}\n\n"
            "Suggest one or two outfits that combine the new item with "
            "pieces they already own. Name the specific wardrobe pieces by "
            "name. Keep it to two or three sentences."
        )

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption. If `outfit` is empty or
        whitespace-only, returns a descriptive message rather than raising.
    """
    if not outfit or not outfit.strip():
        return (
            f"No fit card available — no outfit suggestion was generated for "
            f"{new_item.get('title', 'this item')}, so there's nothing to "
            f"write a caption around."
        )

    brand = f"{new_item['brand']} " if new_item.get("brand") else ""
    item_desc = (
        f"{brand}{new_item['title']}, ${new_item['price']:.2f} on "
        f"{new_item['platform']}"
    )

    prompt = (
        f"Write a short caption someone would actually post about this "
        f"thrift find, the way a real person captions a photo — not a "
        f"product description.\n\n"
        f"Item: {item_desc}\n"
        f"Outfit idea: {outfit}\n\n"
        "Mention the item and its price and platform once each, and be "
        "specific about the vibe. Two to four sentences."
    )

    return generate(prompt)
