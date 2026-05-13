import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from app.calculations import calculate_income_split
from app.command_registry import is_unsupported_format, parse_command
from app.corrections import (
    cancel_by_id,
    cancel_last,
    correct_by_id,
    correct_last,
    show_last,
    show_list,
)
from app.message_store import format_message
from app.models import Transaction
from app.onboarding import handle_onboarding, start_onboarding
from app.reminders import send_endmonth_reports, send_midmonth_reports
from app.storage import add_transaction, clear_transactions, get_transactions
from app.transfers import process_transfer
from app.user_storage import get_user, is_user_blocked, update_user_profile, upsert_from_telegram

_TZ = ZoneInfo("Asia/Jerusalem")
_REPORT_TIME = time(9, 0, tzinfo=_TZ)


def _detect_language(tg_user) -> str:
    code = (tg_user.language_code or "").lower()
    return "he" if code.startswith("he") or code == "iw" else "en"


async def _end_of_month_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    today = datetime.now(_TZ)
    if (today + timedelta(days=1)).month != today.month:
        await send_endmonth_reports(context)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    display_name_parts = [part for part in (tg_user.first_name, tg_user.last_name) if part]
    display_name = " ".join(display_name_parts).strip() or None

    upsert_from_telegram(
        telegram_user_id=tg_user.id,
        username=tg_user.username,
        display_name=display_name,
    )

    if is_user_blocked(tg_user.id):
        await update.message.reply_text(format_message("user_blocked_he"))
        return

    text = update.message.text.strip()
    user_id = tg_user.id
    user = get_user(user_id)

    if user and not user.onboarding_completed:
        if user.onboarding_step is None:
            lang = _detect_language(tg_user)
            update_user_profile(user_id, preferred_language=lang)
            reply = start_onboarding(user_id, lang=lang)
        else:
            reply, _done = handle_onboarding(user, text)
        await update.message.reply_text(reply)
        return

    if user and not user.profile_notified:
        update_user_profile(user_id, profile_notified=True)
        await update.message.reply_text(format_message("profile_notified_he"))

    result = parse_command(text)

    if result is None:
        if is_unsupported_format(text):
            await update.message.reply_text(format_message("unsupported_format_en"))
        else:
            await update.message.reply_text(format_message("invalid_number_en"))
        return

    action, args = result

    if action == "status":
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        all_txns = get_transactions(user_id)
        active = [t for t in all_txns if t.month == current_month and t.status != "canceled"]

        if not active:
            response = format_message("status_no_data_he")
        else:
            response = format_message(
                "status_summary_he",
                total_income=sum(t.amount for t in active),
                total_vat=sum(t.vat_amount for t in active),
                total_income_tax=sum(t.income_tax_amount for t in active),
                total_national_insurance=sum(t.national_insurance_amount for t in active),
                total_social_savings=sum(t.social_savings_amount for t in active),
                total_to_save=sum(t.total_to_save for t in active),
                total_saved=sum(t.saved_amount for t in active),
                total_gap=sum(
                    t.remaining_amount for t in active if t.status in ("open", "partially_saved")
                ),
                total_available=sum(t.available_amount for t in active),
            )
        await update.message.reply_text(response)

    elif action == "list":
        await update.message.reply_text(show_list(user_id))

    elif action == "last":
        await update.message.reply_text(show_last(user_id))

    elif action == "help":
        lang = user.preferred_language if user else "he"
        await update.message.reply_text(format_message(f"help_{lang}"))

    elif action == "cancel_last":
        await update.message.reply_text(cancel_last(user_id))

    elif action == "cancel_id":
        await update.message.reply_text(cancel_by_id(user_id, args["transaction_id"]))

    elif action == "reset":
        clear_transactions(user_id)
        await update.message.reply_text(format_message("reset_success_en"))

    elif action == "saved":
        await update.message.reply_text(process_transfer(user_id, args["amount_text"]))

    elif action == "fix_last":
        await update.message.reply_text(correct_last(user_id, args["amount_text"], user))

    elif action == "fix_id":
        await update.message.reply_text(
            correct_by_id(user_id, args["transaction_id"], args["amount_text"], user)
        )

    elif action == "income":
        amount = args["amount"]
        vat_override = args["vat_override"]

        # VAT-exempt users never include VAT; others use profile default unless overridden.
        if user and user.business_type == "vat_exempt":
            vat_included = False
        elif vat_override is not None:
            vat_included = vat_override
        elif user:
            vat_included = user.vat_included_default
        else:
            vat_included = True

        calc = calculate_income_split(
            amount=amount,
            vat_included=vat_included,
            income_tax_rate=user.income_tax_rate if user else 0.20,
            national_insurance_rate=user.national_insurance_rate if user else 0.08,
            social_savings_rate=user.social_savings_rate if user else 0.05,
        )

        now = datetime.now()
        transaction = Transaction(
            amount=calc["amount"],
            vat_included=vat_included,
            vat_amount=calc["vat_amount"],
            base_amount=calc["base_amount"],
            income_tax_amount=calc["income_tax_amount"],
            national_insurance_amount=calc["national_insurance_amount"],
            social_savings_amount=calc["social_savings_amount"],
            total_to_save=calc["total_to_save"],
            remaining_amount=calc["total_to_save"],
            available_amount=calc["available_amount"],
            month=now.strftime("%Y-%m"),
            created_at=now,
        )
        add_transaction(user_id, transaction)

        await update.message.reply_text(
            format_message(
                "transaction_success_he",
                amount=calc["amount"],
                vat_amount=calc["vat_amount"],
                income_tax_amount=calc["income_tax_amount"],
                national_insurance_amount=calc["national_insurance_amount"],
                social_savings_amount=calc["social_savings_amount"],
                total_to_save=calc["total_to_save"],
                available_amount=calc["available_amount"],
            )
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Missing BOT_TOKEN in .env file")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue
    jq.run_monthly(send_midmonth_reports, when=_REPORT_TIME, day=15)
    jq.run_daily(_end_of_month_job, time=_REPORT_TIME)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
