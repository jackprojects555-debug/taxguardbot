import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from app.calculations import calculate_income_split
from app.message_store import format_message
from app.models import Transaction
from app.onboarding import handle_onboarding, start_onboarding
from app.storage import add_transaction, clear_transactions, get_transactions
from app.transfers import process_transfer
from app.user_storage import get_user, is_user_blocked, update_user_profile, upsert_from_telegram

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
            reply = start_onboarding(user_id)
        else:
            reply, _done = handle_onboarding(user, text)
        await update.message.reply_text(reply)
        return

    if user and not user.profile_notified:
        update_user_profile(user_id, profile_notified=True)
        await update.message.reply_text(format_message("profile_notified_he"))

    if text == "העברתי" or text.startswith("העברתי "):
        amount_text = text[len("העברתי"):].strip()
        await update.message.reply_text(process_transfer(user_id, amount_text))
        return

    if text.lower() == "reset" or text in ("אפס", "נקה", "מחק"):
        clear_transactions(user_id)
        await update.message.reply_text(format_message("reset_success_en"))
        return

    if text == "מצב":
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        all_txns = get_transactions(user_id)
        active = [t for t in all_txns if t.month == current_month and t.status != "canceled"]

        if not active:
            response = format_message("status_no_data_he")
        else:
            total_income = sum(t.amount for t in active)
            total_vat = sum(t.vat_amount for t in active)
            total_income_tax = sum(t.income_tax_amount for t in active)
            total_national_insurance = sum(t.national_insurance_amount for t in active)
            total_social_savings = sum(t.social_savings_amount for t in active)
            total_to_save = sum(t.total_to_save for t in active)
            total_saved = sum(t.saved_amount for t in active)
            total_gap = sum(
                t.remaining_amount for t in active if t.status in ("open", "partially_saved")
            )
            total_available = sum(t.available_amount for t in active)

            response = format_message(
                "status_summary_he",
                total_income=total_income,
                total_vat=total_vat,
                total_income_tax=total_income_tax,
                total_national_insurance=total_national_insurance,
                total_social_savings=total_social_savings,
                total_to_save=total_to_save,
                total_saved=total_saved,
                total_gap=total_gap,
                total_available=total_available,
            )

        await update.message.reply_text(response)
        return

    try:
        # VAT default: VAT-exempt users never include VAT regardless of input.
        # Registered users use their profile default; "נוכה" overrides to False.
        if user and user.business_type == "vat_exempt":
            vat_included = False
        elif user:
            vat_included = user.vat_included_default
        else:
            vat_included = True

        if "נוכה" in text and (not user or user.business_type != "vat_exempt"):
            vat_included = False
            text = text.replace("נוכה", "").strip()

        text = text.replace(",", "")
        text = text.replace(" ", "")
        text = text.replace("₪", "")

        if not text:
            response = format_message("invalid_input_empty_en")
            await update.message.reply_text(response)
            return

        if text.lower().endswith("k") and text[:-1]:
            numeric_part = text[:-1].replace(".", "", 1)
            if numeric_part.isdigit():
                response = format_message("unsupported_format_en")
                await update.message.reply_text(response)
                return

        amount = float(text)

        if amount <= 0:
            response = format_message("amount_must_be_positive_en")
            await update.message.reply_text(response)
            return

        result = calculate_income_split(
            amount=amount,
            vat_included=vat_included,
            income_tax_rate=user.income_tax_rate if user else 0.20,
            national_insurance_rate=user.national_insurance_rate if user else 0.08,
            social_savings_rate=user.social_savings_rate if user else 0.05,
        )

        now = datetime.now()
        transaction = Transaction(
            amount=result["amount"],
            vat_included=vat_included,
            vat_amount=result["vat_amount"],
            base_amount=result["base_amount"],
            income_tax_amount=result["income_tax_amount"],
            national_insurance_amount=result["national_insurance_amount"],
            social_savings_amount=result["social_savings_amount"],
            total_to_save=result["total_to_save"],
            remaining_amount=result["total_to_save"],
            available_amount=result["available_amount"],
            month=now.strftime("%Y-%m"),
            created_at=now,
        )

        add_transaction(user_id, transaction)

        response = format_message(
            "transaction_success_he",
            amount=result["amount"],
            vat_amount=result["vat_amount"],
            income_tax_amount=result["income_tax_amount"],
            national_insurance_amount=result["national_insurance_amount"],
            social_savings_amount=result["social_savings_amount"],
            total_to_save=result["total_to_save"],
            available_amount=result["available_amount"],
        )

    except ValueError:
        response = format_message("invalid_number_en")

    await update.message.reply_text(response)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Missing BOT_TOKEN in .env file")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
