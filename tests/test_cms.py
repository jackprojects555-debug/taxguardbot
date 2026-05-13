"""Tests for CMS layer: t(), get_text, set_text, delete_text, list_texts."""

from app.cms import delete_text, get_text, list_texts, set_text, t

# ---------------------------------------------------------------------------
# t() — fallback to message_store when DB is empty
# ---------------------------------------------------------------------------


def test_t_falls_back_to_message_store_he():
    msg = t("help", "he")
    assert "עזרה" in msg  # Hebrew help contains the help command itself


def test_t_falls_back_to_message_store_en():
    msg = t("help", "en")
    assert "help" in msg.lower()


def test_t_falls_back_to_he_when_lang_variant_missing():
    # "onboarding_welcome" only exists as _he and _en; use a key that exists only in Hebrew
    # to simulate missing lang variant — use a nonexistent lang code
    msg = t("help", "xx")
    # should fall back to _he since _xx doesn't exist
    assert msg  # non-empty


def test_t_returns_debug_marker_for_completely_unknown_key():
    msg = t("totally_nonexistent_key_xyz", "he")
    assert "totally_nonexistent_key_xyz" in msg
    assert msg.startswith("[")


def test_t_formats_kwargs():
    # transaction_success_he has {amount:,.0f} etc
    msg = t(
        "transaction_success",
        "he",
        amount=10000,
        vat_amount=1404,
        income_tax_amount=1000,
        national_insurance_amount=400,
        social_savings_amount=250,
        total_to_save=3054,
        available_amount=6946,
    )
    assert "10,000" in msg or "10000" in msg


# ---------------------------------------------------------------------------
# get_text / set_text round-trip
# ---------------------------------------------------------------------------


def test_get_text_returns_none_when_not_set():
    assert get_text("help", "he") is None


def test_set_and_get_text_round_trip():
    set_text("help", "he", "Custom help text")
    assert get_text("help", "he") == "Custom help text"


def test_set_text_overwrites_existing():
    set_text("help", "he", "First version")
    set_text("help", "he", "Second version")
    assert get_text("help", "he") == "Second version"


def test_t_uses_db_override_over_fallback():
    set_text("help", "he", "Custom override")
    assert t("help", "he") == "Custom override"


def test_db_override_does_not_affect_other_language():
    set_text("help", "he", "Custom Hebrew")
    assert get_text("help", "en") is None


# ---------------------------------------------------------------------------
# delete_text
# ---------------------------------------------------------------------------


def test_delete_text_removes_override():
    set_text("help", "he", "To be deleted")
    assert delete_text("help", "he") is True
    assert get_text("help", "he") is None


def test_delete_text_returns_false_when_not_found():
    assert delete_text("nonexistent_key", "he") is False


def test_after_delete_t_falls_back_to_message_store():
    set_text("help", "he", "Override")
    delete_text("help", "he")
    msg = t("help", "he")
    assert "עזרה" in msg  # default Hebrew help


# ---------------------------------------------------------------------------
# list_texts
# ---------------------------------------------------------------------------


def test_list_texts_empty_when_no_overrides():
    assert list_texts() == []


def test_list_texts_returns_all_entries():
    set_text("help", "he", "Hebrew help")
    set_text("help", "en", "English help")
    rows = list_texts()
    assert len(rows) == 2
    keys = {(r["key"], r["language"]) for r in rows}
    assert ("help", "he") in keys
    assert ("help", "en") in keys


def test_list_texts_row_has_expected_fields():
    set_text("help", "he", "Test")
    rows = list_texts()
    assert len(rows) == 1
    row = rows[0]
    assert "key" in row
    assert "language" in row
    assert "content" in row
    assert "updated_at" in row
