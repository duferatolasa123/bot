import csv
import os
import re
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Get token from environment variable (with fallback for testing)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8211925477:AAF1Kh6SX26cxwAyTKIlQu3uUIuFpzWBjcg')

# Use a writable directory on Render
CSV_FILE = "/tmp/graduate_students.csv"

# Conversation states
(NAME, EMAIL, PHONE, UNIVERSITY, CGPA, SKILLS, EXPERIENCE, PROJECTS,
 GITHUB, LINKEDIN, DESIRED_ROLE, AVAILABILITY, EXPECTED_SALARY,
 RESUME_LINK, VISA_STATUS) = range(15)

def init_csv():
    headers = [
        'Timestamp', 'Name', 'Email', 'Phone', 'University', 'CGPA',
        'Technical Skills', 'Experience', 'Key Projects',
        'GitHub/Portfolio', 'LinkedIn', 'Desired Role',
        'Availability', 'Expected Salary', 'Resume Link', 'Visa Status'
    ]
    
    file_exists = os.path.exists(CSV_FILE)
    if not file_exists:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            print(f"✅ Created CSV file at {CSV_FILE}")
    else:
        print(f"📁 CSV file already exists at {CSV_FILE}")

def save_to_csv(student_data):
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + student_data)
    print(f"✅ Saved data for: {student_data[0]}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎓 *Welcome to Graduate Hire Bot by Dufera Tolasa!*\n\n"
        "I'll collect your essential information for job opportunities.\n"
        "Please answer 15 quick questions to create your profile.\n\n"
        "⚠️ Type /cancel at any time to stop.\n\n"
        "Let's begin! What is your *full name*?"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    return NAME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Send /start to begin again.")
    return ConversationHandler.END

# [Include ALL the other handler functions (get_name, get_email, etc.) 
# exactly as they were in the previous working code - they remain unchanged]
# ... (copy all the get_* functions from the previous code I provided)

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send CSV file to authorized users"""
    if not os.path.exists(CSV_FILE):
        await update.message.reply_text("📭 No data available yet.")
        return
    
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader) - 1
    
    with open(CSV_FILE, 'rb') as file:
        await update.message.reply_document(
            document=file,
            filename=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            caption=f"📊 Total candidates: {row_count}\n\nGraduate Hire Bot - Developed by Dufera Tolasa"
        )

def main():
    print("🚀 Starting Graduate Hire Bot...")
    print("👨‍💻 Developed by Dufera Tolasa")
    print(f"📁 Using CSV file: {CSV_FILE}")
    
    init_csv()
    
    # Create application
    app = Application.builder().token(TOKEN).build()

    # Conversation handler (make sure all your handlers are included here)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_university)],
            CGPA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cgpa)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            PROJECTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_projects)],
            GITHUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_github)],
            LINKEDIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_linkedin)],
            DESIRED_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_desired_role)],
            AVAILABILITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_availability)],
            EXPECTED_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expected_salary)],
            RESUME_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_resume_link)],
            VISA_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_visa_status)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("export", export_data))
    app.add_handler(conv_handler)

    print("🤖 Bot is running successfully on Python 3.11!")
    print("📱 Send /start on Telegram to begin")
    print("📤 Recruiters can use /export to download data")
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
