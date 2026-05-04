VAT_RATE = 17 / 117


def calculate_income_split(
    amount: float,
    vat_included: bool = True,
    income_tax_rate: float = 0.20,
    national_insurance_rate: float = 0.08,
    social_savings_rate: float = 0.05,
) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if vat_included:
        vat_amount = amount * VAT_RATE
        base_amount = amount - vat_amount
    else:
        vat_amount = 0
        base_amount = amount

    income_tax_amount = base_amount * income_tax_rate
    national_insurance_amount = base_amount * national_insurance_rate
    social_savings_amount = base_amount * social_savings_rate

    total_to_save = (
        vat_amount
        + income_tax_amount
        + national_insurance_amount
        + social_savings_amount
    )

    available_amount = amount - total_to_save

    return {
        "amount": amount,
        "vat_amount": vat_amount,
        "base_amount": base_amount,
        "income_tax_amount": income_tax_amount,
        "national_insurance_amount": national_insurance_amount,
        "social_savings_amount": social_savings_amount,
        "total_to_save": total_to_save,
        "available_amount": available_amount,
    }