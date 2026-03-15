import discord, os, json, random, traceback
from discord.ext import commands, tasks
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

# LOAD THIS BEFORE IMPORTING YOUR OWN FILES
load_dotenv() 

import database as db
import ai_handler

db.init_db()

# Ensure the data directory exists so downloads don't crash
os.makedirs("data", exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Discord logged in as {bot.user}")
    activity_watcher.start()
    periodic_nag_and_quiz.start()

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    is_dm = isinstance(message.channel, discord.DMChannel)
    
    # Process commands first (!syllabus, !notes, !list, etc.)
    await bot.process_commands(message)
    
    # If it wasn't a command, check if they are answering a pending quiz in DMs
    if is_dm and not message.content.startswith('!'):
        user_id = str(message.author.id)
        quiz = db.get_pending_quiz(user_id)
        if quiz and not message.attachments:
            keywords = json.loads(quiz['expected_keywords'])
            is_correct, roast = ai_handler.grade_answer(quiz['question'], message.content, keywords)
            await message.channel.send(f"{'✅' if is_correct else '❌'} {roast}")
            db.clear_pending_quiz(user_id)

# --- COMMANDS ---

@bot.command(name="syllabus")
async def cmd_syllabus(ctx):
    """Upload a syllabus PDF to extract deadlines."""
    if not ctx.message.attachments or not ctx.message.attachments[0].filename.endswith('.pdf'):
        await ctx.send("❌ You need to attach a PDF syllabus to this command. Usage: `!syllabus` (with file attached)")
        return
        
    user_id = str(ctx.author.id)
    db.upsert_user(user_id, "discord", str(ctx.author))
    
    await ctx.send("📄 Reading syllabus with Gemini... hold on.")
    file_path = f"data/temp_{ctx.message.attachments[0].filename}"
    await ctx.message.attachments[0].save(file_path)
    
    try:
        syllabus = ai_handler.extract_syllabus_data(file_path)
        for ass in syllabus.assessments:
            db.add_assessment(user_id, syllabus.course_code, ass.name, ass.date, ass.weight, ass.topics_covered)
        await ctx.send(f"✅ Extracted {len(syllabus.assessments)} assessments for {syllabus.course_code}.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Failed to parse PDF:\n```python\n{str(e)}\n```")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@bot.command(name="notes")
async def cmd_notes(ctx, course_code: str = None):
    """Upload class notes/slides for a specific course to fuel the quizzes."""
    if not course_code or not ctx.message.attachments or not ctx.message.attachments[0].filename.endswith('.pdf'):
        await ctx.send("❌ Usage: `!notes INFO3221` (with a PDF file attached).")
        return
        
    course_code = course_code.upper()
    file_path = f"data/notes_{course_code}.pdf"
    await ctx.message.attachments[0].save(file_path)
    
    await ctx.send(f"📚 Received notes for **{course_code}**. Quizzes will now be generated directly from this material.")

# --- BACKGROUND TASKS ---
@tasks.loop(minutes=5)
async def periodic_nag_and_quiz():
    today = date.today()
    assessments = db.get_all_assessments()
    
    for ass in assessments:
        try:
            ass_date = date.fromisoformat(ass['date'])
        except ValueError:
            continue
            
        days_until = (ass_date - today).days
        if days_until < 0: continue
        
        user_id = ass['user_id']
        topics = json.loads(ass['topics']) if ass['topics'] else []
        course_code = ass['course_code'].upper()
        
        # Missing Topics Prompt
        if not topics and days_until <= 21:
            last_prompt = datetime.fromisoformat(ass['last_topic_prompt']) if ass['last_topic_prompt'] else datetime.min
            if (datetime.utcnow() - last_prompt).days >= 1:
                try:
                    user = await bot.fetch_user(int(user_id))
                    dm = await user.create_dm()
                    await dm.send(f"🚨 I don't know what's on your {ass['name']} for {course_code} ({days_until} days). Use `!topics {course_code} topic1, topic2` so I can quiz you.")
                    db.update_last_topic_prompt(ass['id'])
                except: pass
                continue

        # GUARANTEED Quiz Generator (Every 5 mins if within 14 days)
        if 0 < days_until <= 14 and topics:
            if not db.get_pending_quiz(user_id):
                
                # Check if we have notes saved for this course
                notes_path = f"data/notes_{course_code}.pdf"
                actual_notes_path = notes_path if os.path.exists(notes_path) else None
                
                quiz = ai_handler.generate_quiz(course_code, topics, notes_path=actual_notes_path)
                
                try:
                    user = await bot.fetch_user(int(user_id))
                    dm = await user.create_dm()
                    await dm.send(f"😤 POP QUIZ for {course_code} - {ass['name']} ({days_until} days left):\n\n**{quiz.question}**\n\n*Reply with your answer.*")
                    db.set_pending_quiz(user_id, quiz.question, quiz.expected_answer_keywords)
                except: pass
                continue

bot.run(os.environ["DISCORD_TOKEN"])
