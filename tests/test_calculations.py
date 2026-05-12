import pytest

from app.calculations import calculate_income_split


# ---------------------------------------------------------------------------
# Return shape
# ---------------------------------------------------------------------------

def test_returns_all_keys():
    result = calculate_income_split(10000, vat_included=False)
    expected_keys = {
        "amount",
        "vat_amount",
        "base_amount",
        "income_tax_amount",
        "national_insurance_amount",
        "social_savings_amount",
        "total_to_save",
        "available_amount",
    }
    assert set(result.keys()) == expected_keys


# ---------------------------------------------------------------------------
# VAT-included (canonical example: ₪11,700)
# ---------------------------------------------------------------------------

def test_vat_included_standard_amount():
    r = calculate_income_split(11700, vat_included=True)
    assert r["amount"] == 11700
    assert r["vat_amount"] == pytest.approx(1700.0, rel=1e-6)
    assert r["base_amount"] == pytest.approx(10000.0, rel=1e-6)
    assert r["income_tax_amount"] == pytest.approx(2000.0, rel=1e-6)
    assert r["national_insurance_amount"] == pytest.approx(800.0, rel=1e-6)
    assert r["social_savings_amount"] == pytest.approx(500.0, rel=1e-6)
    assert r["total_to_save"] == pytest.approx(5000.0, rel=1e-6)
    assert r["available_amount"] == pytest.approx(6700.0, rel=1e-6)


def test_vat_included_base_equals_amount_minus_vat():
    r = calculate_income_split(5850, vat_included=True)
    assert r["base_amount"] == pytest.approx(r["amount"] - r["vat_amount"], rel=1e-9)


def test_vat_included_available_equals_amount_minus_total_to_save():
    r = calculate_income_split(11700, vat_included=True)
    assert r["available_amount"] == pytest.approx(
        r["amount"] - r["total_to_save"], rel=1e-9
    )


# ---------------------------------------------------------------------------
# VAT-excluded
# ---------------------------------------------------------------------------

def test_vat_excluded_vat_is_zero():
    r = calculate_income_split(10000, vat_included=False)
    assert r["vat_amount"] == 0


def test_vat_excluded_base_equals_amount():
    r = calculate_income_split(10000, vat_included=False)
    assert r["base_amount"] == 10000


def test_vat_excluded_totals():
    r = calculate_income_split(10000, vat_included=False)
    assert r["income_tax_amount"] == pytest.approx(2000.0)
    assert r["national_insurance_amount"] == pytest.approx(800.0)
    assert r["social_savings_amount"] == pytest.approx(500.0)
    assert r["total_to_save"] == pytest.approx(3300.0)
    assert r["available_amount"] == pytest.approx(6700.0)


def test_vat_excluded_available_equals_amount_minus_total_to_save():
    r = calculate_income_split(10000, vat_included=False)
    assert r["available_amount"] == pytest.approx(
        r["amount"] - r["total_to_save"], rel=1e-9
    )


# ---------------------------------------------------------------------------
# Custom rates
# ---------------------------------------------------------------------------

def test_custom_income_tax_rate():
    r = calculate_income_split(10000, vat_included=False, income_tax_rate=0.30)
    assert r["income_tax_amount"] == pytest.approx(3000.0)


def test_custom_national_insurance_rate():
    r = calculate_income_split(10000, vat_included=False, national_insurance_rate=0.10)
    assert r["national_insurance_amount"] == pytest.approx(1000.0)


def test_custom_social_savings_rate():
    r = calculate_income_split(10000, vat_included=False, social_savings_rate=0.0)
    assert r["social_savings_amount"] == pytest.approx(0.0)


def test_zero_all_rates_vat_excluded():
    r = calculate_income_split(
        10000,
        vat_included=False,
        income_tax_rate=0.0,
        national_insurance_rate=0.0,
        social_savings_rate=0.0,
    )
    assert r["total_to_save"] == pytest.approx(0.0)
    assert r["available_amount"] == pytest.approx(10000.0)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_zero_raises():
    with pytest.raises(ValueError):
        calculate_income_split(0)


def test_negative_raises():
    with pytest.raises(ValueError):
        calculate_income_split(-500)


def test_very_small_positive_does_not_raise():
    r = calculate_income_split(0.01, vat_included=False)
    assert r["amount"] == pytest.approx(0.01)


# ---------------------------------------------------------------------------
# Accounting identity: total_to_save components sum correctly
# ---------------------------------------------------------------------------

def test_total_to_save_is_sum_of_components_vat_included():
    r = calculate_income_split(11700, vat_included=True)
    expected = (
        r["vat_amount"]
        + r["income_tax_amount"]
        + r["national_insurance_amount"]
        + r["social_savings_amount"]
    )
    assert r["total_to_save"] == pytest.approx(expected, rel=1e-9)


def test_total_to_save_is_sum_of_components_vat_excluded():
    r = calculate_income_split(10000, vat_included=False)
    expected = (
        r["vat_amount"]
        + r["income_tax_amount"]
        + r["national_insurance_amount"]
        + r["social_savings_amount"]
    )
    assert r["total_to_save"] == pytest.approx(expected, rel=1e-9)
