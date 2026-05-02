import csv
import os
import re
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Attempt to import Google Sheets libraries (optional)
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import json

    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets libraries not installed. Running in CSV-only mode.")

# Telegram Bot Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "8211925477:AAF1Kh6SX26cxwAyTKIlQu3uUIuFpzWBjcg")

# CSV file setup
CSV_FILE = "graduate_students.csv"


# Google Sheets setup (optional)
def setup_google_sheets():
    """Initialize Google Sheets connection (returns None if not configured)"""
    if not GOOGLE_SHEETS_AVAILABLE:
        return None

    try:
        # Try to get credentials from environment variable (for Render deployment)
        creds_json = os.getenv('GOOGLE_CREDENTIALS')

        if creds_json:
            # Use credentials from environment variable
            creds_dict = json.loads(creds_json)
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            print("✅ Google Sheets connected successfully")
            return client
        else:
            print("⚠️ No Google credentials found. Running in CSV-only mode.")
            return None
    except Exception as e:
        print(f"⚠️ Google Sheets setup error: {e}")
        return None


# Get Google Sheet URL from environment variable
SHEET_URL = os.getenv('GOOGLE_SHEET_URL', '')


def save_to_google_sheets(student_data):
    """Save data to Google Sheets (silent fail if not configured)"""
    if not GOOGLE_SHEETS_AVAILABLE or not SHEET_URL:
        return False

    try:
        client = setup_google_sheets()
        if not client:
            return False

        # Open the spreadsheet
        sheet = client.open_by_url(SHEET_URL).sheet1

        # Prepare the row with timestamp
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + student_data

        # Add row to Google Sheets
        sheet.append_row(row)
        print(f"✅ Saved to Google Sheets: {student_data[0]}")
        return True
    except Exception as e:
        print(f"⚠️ Could not save to Google Sheets: {e}")
        return False


def save_to_csv(student_data):
    """Save data to CSV file"""
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + student_data)
    print(f"✅ Saved to CSV: {student_data[0]}")


def save_data(student_data):
    """Save data to CSV and optionally Google Sheets"""
    # Always save to CSV
    save_to_csv(student_data)

    # Try to save to Google Sheets if configured
    if GOOGLE_SHEETS_AVAILABLE and SHEET_URL:
        save_to_google_sheets(student_data)


# Conversation states - 15 states (0 to 14)
(NAME, EMAIL, PHONE, UNIVERSITY, CGPA, SKILLS, EXPERIENCE, PROJECTS,
 GITHUB, LINKEDIN, DESIRED_ROLE, AVAILABILITY, EXPECTED_SALARY,
 RESUME_LINK, VISA_STATUS) = range(15)


# Initialize CSV file with headers
def init_csv():
    headers = [
        'Timestamp', 'Name', 'Email', 'Phone', 'University', 'CGPA',
        'Technical Skills', 'Experience (Years & Roles)', 'Key Projects',
        'GitHub/Portfolio', 'LinkedIn', 'Desired Role',
        'Availability (Join/Interview)', 'Expected Salary', 'Resume/CV Link', 'Visa Status'
    ]

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            print(f"✅ Created CSV file: {CSV_FILE}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎓 *Welcome to Graduate Hire Bot!*\n\n"
        "I'll collect your essential information for job opportunities.\n"
        "Please answer 15 quick questions to create your profile.\n\n"
        "⚠️ Type /cancel at any time to stop.\n\n"
        "Let's begin! What is your *full name*?"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    return NAME


async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the CSV file to authorized users"""
    if not os.path.exists(CSV_FILE):
        await update.message.reply_text("📭 No data available yet.")
        return

    # Count entries
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader) - 1

    # Send CSV file
    with open(CSV_FILE, 'rb') as file:
        await update.message.reply_document(
            document=file,
            filename=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            caption=f"📊 Total candidates: {row_count}"
        )


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("What's your *email address*?", parse_mode='Markdown')
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await update.message.reply_text("⚠️ Invalid email format. Please enter a valid email:")
        return EMAIL
    context.user_data['email'] = email
    await update.message.reply_text("Your *phone number* (with country code):", parse_mode='Markdown')
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("🎓 *Education*\n\nWhat's your *University name*?", parse_mode='Markdown')
    return UNIVERSITY


async def get_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['university'] = update.message.text
    await update.message.reply_text("What's your *CGPA*? (e.g., 3.8/4.0)", parse_mode='Markdown')
    return CGPA


async def get_cgpa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cgpa'] = update.message.text
    await update.message.reply_text(
        "💻 *Technical Skills*\n\nList your *key technical skills* (comma-separated):\n"
        "Example: Python, JavaScript, React, AWS, SQL",
        parse_mode='Markdown')
    return SKILLS


async def get_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['skills'] = update.message.text
    await update.message.reply_text(
        "💼 *Experience*\n\nDescribe your *work experience* (years & roles):\n"
        "Example: 2 years as Software Developer at XYZ Corp",
        parse_mode='Markdown')
    return EXPERIENCE


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['experience'] = update.message.text
    await update.message.reply_text(
        "🚀 *Projects*\n\nDescribe your *best 1-2 projects* (max 2-3 lines):",
        parse_mode='Markdown')
    return PROJECTS


async def get_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['projects'] = update.message.text
    await update.message.reply_text("🔗 *GitHub/Portfolio link*:", parse_mode='Markdown')
    return GITHUB


async def get_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['github'] = update.message.text
    await update.message.reply_text("🔗 *LinkedIn profile URL*:", parse_mode='Markdown')
    return LINKEDIN


async def get_linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['linkedin'] = update.message.text
    await update.message.reply_text("🎯 *Desired role* (e.g., Software Engineer, Data Scientist):",
                                    parse_mode='Markdown')
    return DESIRED_ROLE


async def get_desired_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['desired_role'] = update.message.text
    await update.message.reply_text(
        "📅 *Availability*\n\nWhen can you start? (e.g., Immediate, 2 weeks, July 2024)\n"
        "Also mention interview availability (e.g., Weekdays after 5PM)",
        parse_mode='Markdown')
    return AVAILABILITY


async def get_availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['availability'] = update.message.text
    await update.message.reply_text("💰 *Expected salary* (or 'Negotiable'):", parse_mode='Markdown')
    return EXPECTED_SALARY


async def get_expected_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['expected_salary'] = update.message.text
    await update.message.reply_text("📄 *Resume/CV link* (Google Drive, Dropbox, etc.):", parse_mode='Markdown')
    return RESUME_LINK


async def get_resume_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['resume_link'] = update.message.text

    keyboard = [['Need Visa Sponsorship', 'No Sponsorship Needed', 'Have Valid Work Visa']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🛂 *Visa Status*\n\nWhat's your work authorization status?",
                                    reply_markup=reply_markup, parse_mode='Markdown')
    return VISA_STATUS


async def get_visa_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['visa_status'] = update.message.text

    # Prepare data for CSV (15 fields)
    student_data = [
        context.user_data.get('name', ''),
        context.user_data.get('email', ''),
        context.user_data.get('phone', ''),
        context.user_data.get('university', ''),
        context.user_data.get('cgpa', ''),
        context.user_data.get('skills', ''),
        context.user_data.get('experience', ''),
        context.user_data.get('projects', ''),
        context.user_data.get('github', ''),
        context.user_data.get('linkedin', ''),
        context.user_data.get('desired_role', ''),
        context.user_data.get('availability', ''),
        context.user_data.get('expected_salary', ''),
        context.user_data.get('resume_link', ''),
        context.user_data.get('visa_status', '')
    ]

    # Save data
    save_data(student_data)

    summary = (
        "✅ *Profile Complete! Your information has been recorded.*\n\n"
        f"📋 *Summary*\n"
        f"• Name: {context.user_data.get('name', 'N/A')}\n"
        f"• Role: {context.user_data.get('desired_role', 'N/A')}\n"
        f"• University: {context.user_data.get('university', 'N/A')} (CGPA: {context.user_data.get('cgpa', 'N/A')})\n"
        f"• Skills: {context.user_data.get('skills', 'N/A')[:50]}...\n"
        f"• Experience: {context.user_data.get('experience', 'N/A')}\n\n"
        "Our hiring team will review your profile and contact you soon!\n\n"
        "Best of luck with your job search! 🚀"
    )

    remove_keyboard = ReplyKeyboardMarkup([[]], resize_keyboard=True)
    await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=remove_keyboard)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Send /start to begin again.")
    return ConversationHandler.END


def main():
    print("🚀 Starting Graduate Hire Bot...")
    print(f"📁 CSV will be saved to: {CSV_FILE}")

    # Initialize CSV
    init_csv()

    # Check Google Sheets configuration
    if GOOGLE_SHEETS_AVAILABLE and SHEET_URL:
        print("📊 Google Sheets integration ENABLED")
    else:
        print("⚠️ Google Sheets integration DISABLED (running in CSV-only mode)")

    # Create application
    app = Application.builder().token(TOKEN).build()

    # Conversation handler
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

    # Add handlers
    app.add_handler(CommandHandler("export", export_data))
    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    print("📱 Send /start on Telegram to begin.")
    print("📤 Recruiters can use /export to download data")

    # Start the bot
    app.run_polling()


if __name__ == "__main__":
    main()