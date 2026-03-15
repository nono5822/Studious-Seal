# 🦭 Studious Seal — MTAHacks Submission

> A Discord bot that tracks your academic deadlines and **calls you out** when it catches you gaming or sitting in voice chat instead of studying. The seal does not forgive. The seal does not forget.

---

## ⚡ Try It Right Now (Judges)

**The bot is already running.** You don't need to set anything up.

### Step 1 — Join the demo server
> https://discord.gg/STMK9Qfh 

### Step 2 — DM the bot
Once you're in the server, find **Studious Seal** in the member list and send it a DM. Any message works — it will introduce itself.

### Step 3 — Watch it work
Type `!demo` in the DM to instantly see a nag message + gif without needing to add real deadlines.

To see the full flow, add a deadline:
```
INFO4004 16 mars 25%
```
Then type `!list` to confirm it was added.

---

## Bot Invite Link

To add the bot to your **own** server:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=68608&scope=bot
```
*(Replace `YOUR_CLIENT_ID` with your bot's application ID from the Developer Portal)*

Or DM the bot `!invite` once you've joined the demo server.

---

## Running It Yourself

### Prerequisites
- Python 3.10+

### Install
```bash
pip install -r requirements.txt
python bot.py
```

### Enable Required Intents
In the [Discord Developer Portal](https://discord.com/developers/applications):
- Select your app → **Bot** tab → scroll to **Privileged Gateway Intents**
- Enable all three:
  - **Presence Intent** — detects what games you're playing and if your in a voice chatpoppooooooooo
  - **Server Members Intent** — finds you in the server
  - **Message Content Intent** — reads DMs

### Run
```bash
python bot.py
```

The console will print the bot's tag, invite link, and how many users are tracked.

> **Note:** The bot must share at least one server with the user to see their gaming activity. It communicates exclusively via DMs.

---

## Feature Walkthrough

### Natural language deadline input
No slash commands needed. Just DM the bot in plain text:
```
INFO4004 23 mars 25%
MATH101 14 april 40%, ENG202 2 mai 15%
add PHYS301 7 june 30% please
```
French months are supported. The bot extracts deadlines from whatever you write.

### Smart game detection
The bot only nags you for **real games** — it ignores Spotify, VS Code, YouTube, OBS, and other non-game activities. It recognises 100+ popular titles and generic Steam/launcher patterns.

### Quiet hours
Set your timezone once (`!timezone EST`) and the bot won't message you between 10 PM and 8 AM.

### VC monitoring (critical only)
Voice chat only triggers a nag when a deadline is **3 days or less** away — not for every casual hangout.

### Seal gifs (~25% of nags)
Each nag message has a matched gif mood (angry, jumpscare, belly slap, bow). The gif fires randomly about 1 in 4 times.

### Congrats on completion
Marking a deadline done (`!done INFO4004`) triggers a congratulations message, also with a chance of a gif.

### Per-user persistence
Every user gets their own `data/<user_id>.json` file. Cooldowns, timezone, and deadline state all survive bot restarts.

---

## All Commands

| Command | Description |
|---------|-------------|
| `!list` | Show all upcoming deadlines |
| `!done COURSE` | Mark a deadline complete (triggers congrats) |
| `!clear` | Wipe all your deadlines |
| `!timezone EST` | Set your timezone for quiet hours |
| `!nag` | Get an immediate reminder |
| `!demo` | **See what a nag looks like** (great for judges) |
| `!invite` | Get the bot's invite link |
| `!status` | Check cooldown timer, timezone, deadline count |
| `!help` | Show the welcome message |

---

## Security & Reliability

- **Atomic file writes** — JSON files are written via temp-file + rename, so a crash mid-write can't corrupt user data
- **Input sanitisation** — course codes are stripped of Discord mentions and markdown characters
- **Deadline cap** — max 50 deadlines per user, max 10 per message, weight capped at 100%
- **Past date rejection** — deadlines with explicit past years are rejected
- **DM failure tracking** — after 5 consecutive failed DMs (e.g. user blocked the bot), that user is skipped in background loops
- **DM channel caching** — `fetch_user()` results are cached to avoid hitting Discord's rate limits in the activity scan loop
- **Quiet hours** — timezone-aware, handles midnight crossover correctly
- **Timezone input** — capped at 64 chars and sanitised before passing to pytz

---

## Project Structure

```
deadline_bot/
├── bot.py           ← the entire bot (single file)
├── requirements.txt ← dependencies
├── data/            ← created automatically on first run
│   └── <user_id>.json  ← one file per user
└── discord.log      ← debug log (created on run)
```

---

## Tech Stack

- **discord.py 2.x** — bot framework, background tasks, presence detection
- **python-dateutil** — flexible date parsing (handles French month names)
- **pytz** — timezone-aware quiet hours

---

