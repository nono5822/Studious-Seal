# 📚 Studious Seal Premium

An AI-powered study enforcer for Discord and Telegram. It reads your syllabus PDFs, tracks your deadlines, and aggressively quizzes you on your class notes so you don't fail. Powered by **Gemini 2.5 Flash** and a local SQLite database.

## ✨ Features
* **AI Syllabus Parsing:** Drag and drop a PDF syllabus. The bot automatically extracts the course code, dates, and weights.
* **Grounded Pop Quizzes:** Upload your professor's exact PowerPoint slides or PDF notes. The AI will strictly base its quizzes on that material to prevent hallucinations.
* **Brutal Grading:** Reply to a quiz, and the AI will evaluate your answer. If you miss key concepts, it will roast you.
* **Relentless Reminders:** Runs a background loop every 5 minutes to check for upcoming exams and ambush you with questions.

---

## 🚀 Setup & Installation

**1. Prepare your environment**
Ensure you have Python 3.10+ installed. Navigate to the project directory and create a fresh virtual environment:

python3 -m venv venv
source venv/bin/activate

**2. Install dependencies**
Install the required packages from the requirements.txt file:

pip install -r requirements.txt

**3. Set up your .env file (CRITICAL)**
The bot relies on API keys to function, which must be kept secret. You need to create a file named exactly .env in the main folder of the project. 

Create the file and paste the following, replacing the placeholders with your actual tokens:

DISCORD_TOKEN=your_discord_bot_token_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_google_gemini_api_key_here

*(Warning: Never commit your .env file to GitHub!)*

**4. Run the bots**
You can run the bots directly in your terminal, or set them up as background systemd services. Because they share a SQLite database, they can safely run at the same time:

In terminal 1:
python discord_bot.py

In terminal 2:
python telegram_bot.py

---

## 💻 Discord Commands

All commands should be sent via **Direct Message** to the bot.

| Command | Action |
| :--- | :--- |
| **!help** | Displays the welcome message and basic instructions. |
| **!list** | Shows all your currently tracked upcoming deadlines and exams. |
| **!syllabus** + [PDF Attached] | Upload a syllabus. The AI will extract the course code, dates, and weights automatically. |
| **!notes COURSECODE** + [PDF Attached] | Upload class slides/notes (e.g., !notes INFO3221). The AI will use this file to generate highly accurate pop quizzes. |
| **!topics COURSECODE topic1, topic2** | If the syllabus didn't list exam topics, use this to manually tell the bot what to quiz you on. |
| *(Answering a Quiz)* | Just type your answer normally in the DM. No command needed. |

---

## 📱 Telegram Commands

* **/start** - Initializes the bot and registers your Telegram ID.
* **File Upload** - Simply send a PDF syllabus directly to the bot. It will automatically parse it and add the deadlines to your database.
* *(Answering a Quiz)* - Reply directly to the quiz message.

---

## 📂 Architecture
* database.py: Handles the shared SQLite database (data/nagger.db).
* ai_handler.py: Manages all interactions with the Google GenAI SDK (parsing PDFs and generating/grading quizzes).
* discord_bot.py: The Discord client and the background timer loop for sending scheduled quizzes.
* telegram_bot.py: The Telegram client interface.
