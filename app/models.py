from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    amount: float
    vat_included: bool
    vat_amount: float
    base_amount: float
    income_tax_amount: float
    national_insurance_amount: float
    social_savings_amount: float
    total_to_save: float
    available_amount: float
    created_at: datetime