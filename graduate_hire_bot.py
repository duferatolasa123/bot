import csv
import os
import re
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Get token from environment variable (with fallback for testing)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8211925477:AAG6qdM3VNUObFDlpS1vDIUpFdBMsF7xnmg')

# Use a writable directory on Render
CSV_FILE = "/tmp/graduate_students.csv"

# Conversation states
(NAME, EMAIL, PHONE, UNIVERSITY, CGPA, SKILLS, EXPERIENCE, PROJECTS,
 GITHUB, LINKEDIN, DESIRED_ROLE, AVAILABILITY, EXPECTED_SALARY,
 RESUME_LINK, VISA_STATUS) = range(15)

def init_csv():
    """Initialize CSV file with headers"""
    headers = [
        'Timestamp', 'Name', 'Email', 'Phone', 'University', 'CGPA',
        'Technical Skills', 'Experience', 'Key Projects',
        'GitHub/Portfolio', 'LinkedIn', 'Desired Role',
        'Availability', 'Expected Salary', 'Resume Link', 'Visa Status'
    ]
    
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            print(f"✅ Created CSV file at {CSV_FILE}")

def save_to_csv(student_data):
    """Save data to CSV file"""
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + student_data)
    print(f"✅ Saved data for: {student_data[0]}")

# ============= HANDLER FUNCTIONS =============

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

    save_to_csv(student_data)

    summary = (
        "✅ *Profile Complete! Your information has been recorded.*\n\n"
        f"📋 *Summary*\n"
        f"• Name: {context.user_data.get('name', 'N/A')}\n"
        f"• Role: {context.user_data.get('desired_role', 'N/A')}\n"
        f"• University: {context.user_data.get('university', 'N/A')}\n"
        f"• Skills: {context.user_data.get('skills', 'N/A')[:50]}...\n\n"
        "Our hiring team will review your profile and contact you soon!\n\n"
        "Best of luck! 🚀"
    )

    remove_keyboard = ReplyKeyboardMarkup([[]], resize_keyboard=True)
    await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=remove_keyboard)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Send /start to begin again.")
    return ConversationHandler.END

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send CSV file to authorized users"""
    if not os.path.exists(CSV_FILE):
        await update.message.reply_text("📭 No data available yet.")
        return
    
    # Count entries (subtract header)
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader) - 1
    
    with open(CSV_FILE, 'rb') as file:
        await update.message.reply_document(
            document=file,
            filename=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            caption=f"📊 Total candidates: {row_count}\n\nGraduate Hire Bot - Developed by Dufera Tolasa"
        )

# ============= MAIN FUNCTION =============

def main():
    print("🚀 Starting Graduate Hire Bot...")
    print("👨‍💻 Developed by Dufera Tolasa")
    print(f"📁 Using CSV file: {CSV_FILE}")
    
    # Initialize CSV
    init_csv()
    
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

    print("🤖 Bot is running successfully!")
    print("📱 Send /start on Telegram to begin")
    print("📤 Recruiters can use /export to download data")
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
