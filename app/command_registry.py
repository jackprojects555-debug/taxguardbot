"""
Central command parser for TaxGuardBot.

parse_command(text) normalises raw user input and returns (action, args) or None.
Handlers in bot.py receive typed args and never touch raw text.

Supported actions and their args:
  status        {}
  list          {}
  last          {}
  help          {}
  cancel_last   {}
  reset         {}
  saved         {amount_text: str}          — "" means fully saved
  cancel_id     {transaction_id: int}
  fix_last      {amount_text: str}
  fix_id        {transaction_id: int, amount_text: str}
  income        {amount: float, vat_override: bool | None}
                  vat_override=False → user said VAT excluded
                  vat_override=None  → use user profile default
"""

import re
from typing import Optional, Tuple

ParseResult = Tuple[str, dict]

_EXACT: dict[str, str] = {
    "מצב": "status",
    "status": "status",
    "רשימה": "list",
    "list": "list",
    "אחרון": "last",
    "last": "last",
    "עזרה": "help",
    "help": "help",
    "בטל אחרון": "cancel_last",
    "cancel last": "cancel_last",
    "העברתי": "saved",
    "saved": "saved",
    "אפס": "reset",
    "נקה": "reset",
    "מחק": "reset",
    "reset": "reset",
    "clear": "reset",
    "delete": "reset",
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def parse_command(text: str) -> Optional[ParseResult]:
    raw = _normalise(text)
    lower = raw.lower()

    # Exact aliases (try original case first, then lowercase for English)
    action = _EXACT.get(raw) or _EXACT.get(lower)
    if action:
        args: dict = {"amount_text": ""} if action == "saved" else {}
        return (action, args)

    # "saved {amount}" / "העברתי {amount}"
    if raw.startswith("העברתי "):
        return ("saved", {"amount_text": raw[len("העברתי ") :]})
    if lower.startswith("saved "):
        return ("saved", {"amount_text": raw[len("saved ") :]})

    # "בטל {id}" / "cancel {id}"
    m = re.fullmatch(r"(?:בטל|cancel)\s+(\d+)", raw, re.IGNORECASE)
    if m:
        return ("cancel_id", {"transaction_id": int(m.group(1))})

    # "תקן אחרון {amount}" / "fix last {amount}"
    m = re.fullmatch(r"(?:תקן\s+אחרון|fix\s+last)\s+(.+)", raw, re.IGNORECASE)
    if m:
        return ("fix_last", {"amount_text": m.group(1).strip()})

    # "תקן {id} {amount}" / "fix {id} {amount}"
    m = re.fullmatch(r"(?:תקן|fix)\s+(\d+)\s+(.+)", raw, re.IGNORECASE)
    if m:
        return ("fix_id", {"transaction_id": int(m.group(1)), "amount_text": m.group(2).strip()})

    # Income — try to parse as a number
    income = parse_income(raw)
    if income is not None:
        amount, vat_override = income
        return ("income", {"amount": amount, "vat_override": vat_override})

    return None


def parse_income(text: str) -> Optional[Tuple[float, Optional[bool]]]:
    """
    Returns (amount, vat_override) or None if text is not a valid income input.

    vat_override:
      False — modifier present (נוכה / vat excluded / novat)
      None  — no modifier; caller should use user profile default
    """
    t = _normalise(text)
    vat_override: Optional[bool] = None

    if "נוכה" in t:
        vat_override = False
        t = t.replace("נוכה", "").strip()
    elif re.search(r"vat\s+excluded", t, re.IGNORECASE):
        vat_override = False
        t = re.sub(r"vat\s+excluded", "", t, flags=re.IGNORECASE).strip()
    elif re.search(r"\bnovat\b", t, re.IGNORECASE):
        vat_override = False
        t = re.sub(r"\bnovat\b", "", t, flags=re.IGNORECASE).strip()

    t = t.replace("₪", "").replace(",", "").replace(" ", "")

    if not t:
        return None

    if t.lower().endswith("k"):
        return None

    try:
        amount = float(t)
    except ValueError:
        return None

    if amount <= 0:
        return None

    return (amount, vat_override)


def is_unsupported_format(text: str) -> bool:
    """True when input looks like a 'k-suffix' shorthand (e.g. '11k')."""
    t = _normalise(text).replace("₪", "").replace(",", "").replace(" ", "")
    if not t or not t.lower().endswith("k"):
        return False
    prefix = t[:-1].replace(".", "", 1)
    return bool(prefix) and prefix.isdigit()
