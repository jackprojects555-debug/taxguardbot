from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    # Required fields — must be provided at creation time
    amount: float
    vat_included: bool
    vat_amount: float
    base_amount: float
    income_tax_amount: float
    national_insurance_amount: float
    social_savings_amount: float
    total_to_save: float
    remaining_amount: float
    available_amount: float
    month: str  # "YYYY-MM", stored explicitly so corrections don't shift it
    created_at: datetime
    # Fields with defaults — assigned/updated by storage layer
    id: int = 0  # assigned by add_transaction; 1-indexed per user
    status: str = "open"  # "open" | "partially_saved" | "fully_saved" | "canceled"
    saved_amount: float = 0.0
    updated_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
