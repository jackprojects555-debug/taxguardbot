import os
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from app.calculations import calculate_income_split
from app.models import Transaction
from app.storage import add_transaction, clear_transactions, get_transactions

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if text.lower() == "reset" or text in ("אפס", "נקה", "מחק"):
        clear_transactions(user_id)
        await update.message.reply_text("All data has been reset.")
        return

    if text == "מצב":
        transactions = get_transactions(user_id)
        now = datetime.now()
        transactions = [
            t
            for t in transactions
            if t.created_at.year == now.year and t.created_at.month == now.month
        ]

        if not transactions:
            response = "אין עדיין נתונים החודש."
        else:
            total_income = sum(t.amount for t in transactions)
            total_to_save = sum(t.total_to_save for t in transactions)
            total_available = sum(t.available_amount for t in transactions)

            response = (
                f"סיכום עד כה:\n\n"
                f"הכנסות: ₪{total_income:,.0f}\n"
                f"לשמירה: ₪{total_to_save:,.0f}\n"
                f"פנוי: ₪{total_available:,.0f}"
            )

        await update.message.reply_text(response)
        return

    try:
        vat_included = True

        if "נוכה" in text:
            vat_included = False
            text = text.replace("נוכה", "").strip()

        text = text.replace(",", "")
        text = text.replace(" ", "")
        text = text.replace("₪", "")

        if not text:
            response = "Invalid input. Please enter a number."
            await update.message.reply_text(response)
            return

        if text.lower().endswith("k") and text[:-1]:
            numeric_part = text[:-1].replace(".", "", 1)
            if numeric_part.isdigit():
                response = "Unsupported format. Please enter full number."
                await update.message.reply_text(response)
                return

        amount = float(text)

        if amount <= 0:
            response = "Amount must be positive."
            await update.message.reply_text(response)
            return

        result = calculate_income_split(
            amount=amount,
            vat_included=vat_included,
        )

        transaction = Transaction(
            amount=result["amount"],
            vat_included=vat_included,
            vat_amount=result["vat_amount"],
            base_amount=result["base_amount"],
            income_tax_amount=result["income_tax_amount"],
            national_insurance_amount=result["national_insurance_amount"],
            social_savings_amount=result["social_savings_amount"],
            total_to_save=result["total_to_save"],
            available_amount=result["available_amount"],
            created_at=datetime.now(),
        )

        add_transaction(user_id, transaction)

        response = (
            f"נכנסו ₪{result['amount']:,.0f}\n\n"
            f"להפרשה:\n"
            f"מע״מ: ₪{result['vat_amount']:,.0f}\n"
            f"מס הכנסה: ₪{result['income_tax_amount']:,.0f}\n"
            f"ביטוח לאומי: ₪{result['national_insurance_amount']:,.0f}\n"
            f"סוציאליות: ₪{result['social_savings_amount']:,.0f}\n\n"
            f"סה״כ להעברה עכשיו: ₪{result['total_to_save']:,.0f}\n"
            f"כסף פנוי אמיתי: ₪{result['available_amount']:,.0f}\n\n"
            f"פעולה מומלצת: העבר עכשיו ₪{result['total_to_save']:,.0f} לחשבון השמירה שלך."
        )

    except ValueError:
        response = "Invalid input. Please enter a number."

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