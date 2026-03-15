import os, json, asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
load_dotenv()
import database as db
import ai_handler

load_dotenv()
db.init_db()

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    db.upsert_user(user_id, "telegram", update.message.from_user.username)
    
    file = await update.message.document.get_file()
    file_path = f"data/{update.message.document.file_name}"
    await file.download_to_drive(file_path)
    
    await update.message.reply_text("📄 Reading syllabus with Gemini... hold on.")
    
    try:
        syllabus = ai_handler.extract_syllabus_data(file_path)
        added = 0
        for ass in syllabus.assessments:
            db.add_assessment(user_id, syllabus.course_code, ass.name, ass.date, ass.weight, ass.topics_covered)
            added += 1
        await update.message.reply_text(f"✅ Extracted {added} assessments for {syllabus.course_code}. I will begin nagging you accordingly.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to parse PDF: {e}")
    finally:
        os.remove(file_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text
    
    # Check if they are answering a quiz
    quiz = db.get_pending_quiz(user_id)
    if quiz:
        keywords = json.loads(quiz['expected_keywords'])
        is_correct, roast = ai_handler.grade_answer(quiz['question'], text, keywords)
        await update.message.reply_text(f"{'✅' if is_correct else '❌'} {roast}")
        db.clear_pending_quiz(user_id)
        return

    await update.message.reply_text("Send me a syllabus PDF to track deadlines, or answer a pending quiz.")

def main():
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Telegram bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
