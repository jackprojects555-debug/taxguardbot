from app.message_store import format_message
from app.storage import get_transactions, list_user_ids_with_transactions


def _aggregate(user_id: int, month: str) -> dict | None:
    active = [t for t in get_transactions(user_id) if t.month == month and t.status != "canceled"]
    if not active:
        return None
    return {
        "total_income": sum(t.amount for t in active),
        "total_vat": sum(t.vat_amount for t in active),
        "total_income_tax": sum(t.income_tax_amount for t in active),
        "total_national_insurance": sum(t.national_insurance_amount for t in active),
        "total_social_savings": sum(t.social_savings_amount for t in active),
        "total_to_save": sum(t.total_to_save for t in active),
        "total_saved": sum(t.saved_amount for t in active),
        "total_gap": sum(
            t.remaining_amount for t in active if t.status in ("open", "partially_saved")
        ),
    }


def build_midmonth_report(user_id: int, month: str) -> str | None:
    agg = _aggregate(user_id, month)
    if agg is None:
        return None
    return format_message(
        "midmonth_report_he",
        month=month,
        total_income=agg["total_income"],
        total_to_save=agg["total_to_save"],
        total_saved=agg["total_saved"],
        total_gap=agg["total_gap"],
    )


def build_endmonth_report(user_id: int, month: str) -> str | None:
    agg = _aggregate(user_id, month)
    if agg is None:
        return None
    return format_message(
        "endmonth_report_he",
        month=month,
        total_income=agg["total_income"],
        total_vat=agg["total_vat"],
        total_income_tax=agg["total_income_tax"],
        total_national_insurance=agg["total_national_insurance"],
        total_social_savings=agg["total_social_savings"],
        total_to_save=agg["total_to_save"],
        total_saved=agg["total_saved"],
        total_gap=agg["total_gap"],
    )


async def send_midmonth_reports(context) -> None:
    from datetime import datetime

    month = datetime.now().strftime("%Y-%m")
    for user_id in list_user_ids_with_transactions():
        report = build_midmonth_report(user_id, month)
        if report:
            await context.bot.send_message(chat_id=user_id, text=report)


async def send_endmonth_reports(context) -> None:
    from datetime import datetime

    month = datetime.now().strftime("%Y-%m")
    for user_id in list_user_ids_with_transactions():
        report = build_endmonth_report(user_id, month)
        if report:
            await context.bot.send_message(chat_id=user_id, text=report)
