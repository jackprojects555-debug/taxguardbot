"""Tests for status command message formatting — V2-010 enhancements."""

from app.message_store import format_message

_BASE = dict(
    total_income=11700,
    total_vat=1700,
    total_income_tax=2000,
    total_national_insurance=800,
    ni_mode_label="",
    total_social_savings=500,
    ss_mode_label="",
    pension_line="",
    total_to_save=5000,
    total_saved=0,
    total_gap=5000,
    total_available=6700,
)


def _render(**overrides) -> str:
    return format_message("status_summary_he", **{**_BASE, **overrides})


# ---------------------------------------------------------------------------
# Pension line
# ---------------------------------------------------------------------------


def test_pension_line_absent_when_empty():
    msg = _render(pension_line="")
    assert "פנסיה" not in msg


def test_pension_line_present_when_set():
    msg = _render(pension_line="פנסיה: ₪600\n")
    assert "פנסיה" in msg
    assert "600" in msg


def test_pension_line_appears_before_total_to_save():
    msg = _render(pension_line="פנסיה: ₪600\n")
    assert msg.index("פנסיה") < msg.index("לשמירה")


def test_no_extra_blank_line_when_pension_absent():
    without = _render(pension_line="")
    with_pension = _render(pension_line="פנסיה: ₪600\n")
    # Both should contain לשמירה; structure shouldn't break
    assert "לשמירה" in without
    assert "לשמירה" in with_pension


# ---------------------------------------------------------------------------
# NI mode label
# ---------------------------------------------------------------------------


def test_ni_mode_label_absent_for_percentage():
    msg = _render(ni_mode_label="")
    # Should NOT contain fixed indicator
    assert "(קבוע)" not in msg.split("ביטוח")[1].split("\n")[0]


def test_ni_mode_label_present_for_fixed():
    msg = _render(ni_mode_label=" (קבוע)")
    ni_line = [line for line in msg.splitlines() if "ביטוח" in line][0]
    assert "(קבוע)" in ni_line


def test_ni_mode_label_does_not_affect_ss_line():
    msg = _render(ni_mode_label=" (קבוע)", ss_mode_label="")
    ss_line = [line for line in msg.splitlines() if "סוציאליות" in line][0]
    assert "(קבוע)" not in ss_line


# ---------------------------------------------------------------------------
# Social savings mode label
# ---------------------------------------------------------------------------


def test_ss_mode_label_absent_for_percentage():
    msg = _render(ss_mode_label="")
    ss_line = [line for line in msg.splitlines() if "סוציאליות" in line][0]
    assert "(קבוע)" not in ss_line


def test_ss_mode_label_present_for_fixed():
    msg = _render(ss_mode_label=" (קבוע)")
    ss_line = [line for line in msg.splitlines() if "סוציאליות" in line][0]
    assert "(קבוע)" in ss_line


def test_ss_mode_label_does_not_affect_ni_line():
    msg = _render(ni_mode_label="", ss_mode_label=" (קבוע)")
    ni_line = [line for line in msg.splitlines() if "ביטוח" in line][0]
    assert "(קבוע)" not in ni_line


# ---------------------------------------------------------------------------
# Both fixed + pension together
# ---------------------------------------------------------------------------


def test_all_three_enhancements_together():
    msg = _render(
        ni_mode_label=" (קבוע)",
        ss_mode_label=" (קבוע)",
        pension_line="פנסיה: ₪600\n",
    )
    assert "פנסיה" in msg
    ni_line = [line for line in msg.splitlines() if "ביטוח" in line][0]
    ss_line = [line for line in msg.splitlines() if "סוציאליות" in line][0]
    assert "(קבוע)" in ni_line
    assert "(קבוע)" in ss_line


# ---------------------------------------------------------------------------
# Core amounts still present
# ---------------------------------------------------------------------------


def test_all_amounts_present():
    msg = _render()
    assert "11,700" in msg  # total_income
    assert "1,700" in msg  # vat
    assert "2,000" in msg  # income_tax
    assert "800" in msg  # NI
    assert "500" in msg  # SS
    assert "5,000" in msg  # total_to_save
    assert "6,700" in msg  # available


def test_structure_contains_required_sections():
    msg = _render()
    assert "הכנסות" in msg
    assert "מע״מ" in msg
    assert "מס הכנסה" in msg
    assert "ביטוח לאומי" in msg
    assert "סוציאליות" in msg
    assert "לשמירה" in msg
    assert "הועבר" in msg
    assert "פנוי" in msg
