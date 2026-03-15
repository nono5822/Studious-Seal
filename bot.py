"""
╔══════════════════════════════════════════════════════╗
║           🦭  STUDIOUS SEAL  🦭                     ║
║  A deadline-tracking Discord bot that watches your  ║
║  gaming activity and nags you to actually study.    ║
╚══════════════════════════════════════════════════════╝
"""

import discord
from discord.ext import commands, tasks
import json, re, os, random, asyncio, logging, tempfile, shutil
from datetime import datetime, date
from dateutil import parser as dateparser
from pathlib import Path
import pytz

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG  ←  only this block needs to be edited
# ──────────────────────────────────────────────────────────────────────────────
TOKEN = 'YOURTOKENHERE'

# Get this from: Discord Developer Portal → OAuth2 → Client ID
# The invite URL is printed on startup and available via !invite
BOT_CLIENT_ID = 'YOUR_CLIENT_ID'

DATA_DIR                      = Path("data")
ACTIVITY_CHECK_MINUTES        = 1      # how often to scan for gaming / VC
PERIODIC_NAG_MINUTES          = 60     # how often to fire scheduled reminders
NAG_WINDOW_DAYS               = 14     # start nagging within this many days
ACTIVITY_NAG_COOLDOWN_MINUTES = 5      # min gap between activity nags per user
VC_CRITICAL_DAYS              = 3      # VC only triggers within this many days
QUIET_HOUR_START              = 22     # 10 PM  — no nags past this hour
QUIET_HOUR_END                = 8      # 8 AM   — nags resume at this hour
GIF_CHANCE                    = 0.25   # probability a nag gets a gif (0–1)
MAX_DEADLINES_PER_USER        = 50     # hard cap — prevents data flooding
MAX_DEADLINES_PER_MESSAGE     = 10     # max parsed per single message
MAX_FAIL_STREAK               = 5      # stop trying to DM after N consecutive failures

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# ──────────────────────────────────────────────────────────────────────────────
# INVITE URL  (printed on startup, returned by !invite)
# ──────────────────────────────────────────────────────────────────────────────
INVITE_PERMISSIONS = 68608   # Send Messages + Read Message History + Add Reactions
def get_invite_url() -> str:
    if BOT_CLIENT_ID and BOT_CLIENT_ID != 'YOUR_CLIENT_ID_HERE':
        return (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={BOT_CLIENT_ID}"
            f"&permissions={INVITE_PERMISSIONS}"
            f"&scope=bot"
        )
    return "(set BOT_CLIENT_ID in config to generate invite link)"

# ──────────────────────────────────────────────────────────────────────────────
# GAME DETECTION  — allowlist of known game keywords
# ──────────────────────────────────────────────────────────────────────────────
GAME_KEYWORDS = {
    # launchers / stores
    "steam", "epic games", "battle.net", "origin", "ubisoft connect",
    "ea app", "gog galaxy", "itch.io",
    # shooters / battle royale
    "valorant", "counter-strike", "cs2", "csgo", "apex legends", "overwatch",
    "warzone", "call of duty", "cod", "rainbow six", "r6", "pubg",
    "battlegrounds", "halo", "team fortress", "tf2", "deadlock",
    "marvel rivals", "helldivers", "hunt showdown", "escape from tarkov",
    "payday", "gtfo", "back 4 blood", "left 4 dead", "l4d",
    # moba / strategy
    "league of legends", "dota", "starcraft", "age of empires", "civilization",
    "civ6", "total war", "stellaris", "hearthstone",
    # open world / rpg
    "minecraft", "roblox", "genshin", "honkai", "elden ring", "dark souls",
    "cyberpunk", "baldur's gate", "bg3", "divinity", "the witcher", "skyrim",
    "fallout", "starfield", "oblivion", "final fantasy", "ff14", "ffxiv",
    "world of warcraft", "wow", "lost ark", "path of exile", "diablo",
    "destiny", "new world", "black desert", "god of war", "ghost of tsushima",
    "assassin's creed", "red dead", "rdr", "grand theft auto", "gta",
    "horizon", "last of us", "bioshock", "borderlands", "batman", "spider-man",
    # survival / sandbox
    "rust", "ark", "terraria", "stardew valley", "the sims", "subnautica",
    "the forest", "sons of", "no man's sky", "sea of thieves", "palworld",
    "satisfactory", "factorio", "rimworld", "dwarf fortress", "cities skylines",
    # roguelikes / indie
    "hades", "dead cells", "hollow knight", "celeste", "undertale", "deltarune",
    "omori", "disco elysium", "outer wilds", "inscryption", "slay the spire",
    "vampire survivors", "brotato", "noita", "binding of isaac",
    "enter the gungeon", "geometry dash", "osu",
    # party / horror
    "among us", "fall guys", "phasmophobia", "lethal company", "content warning",
    "dead by daylight", "dbd", "friday the 13th",
    # sports / racing / fighting
    "rocket league", "fortnite", "fifa", "ea fc", "nba 2k", "madden",
    "street fighter", "mortal kombat", "tekken",
    # misc / catch-all for Steam-launched titles
    "simulator", "tycoon", "tabletop simulator",
    "deep rock galactic", "vermintide", "warhammer", "monster hunter",
    "magic the gathering", "mtga", "beat saber", "vr chat",
}

# Non-game activities that contain generic words — explicitly blocked
NOT_GAMES = {
    "spotify", "youtube", "netflix", "prime video", "twitch",
    "visual studio", "vs code", "pycharm", "intellij", "eclipse",
    "chrome", "firefox", "edge", "safari",
    "word", "excel", "powerpoint", "notion", "obsidian",
    "discord", "slack", "zoom", "teams",
    "itunes", "apple music", "tidal", "soundcloud", "deezer",
    "obs", "streamlabs", "xsplit",
    "photoshop", "illustrator", "figma", "blender",
}

def is_real_game(name: str) -> bool:
    low = name.lower().strip()
    if not low:
        return False
    # Hard-block known non-games first
    if any(ng in low for ng in NOT_GAMES):
        return False
    # Then require a positive game keyword match
    return any(kw in low for kw in GAME_KEYWORDS)

# ──────────────────────────────────────────────────────────────────────────────
# INPUT SANITISATION
# ──────────────────────────────────────────────────────────────────────────────
_DISCORD_MENTIONS = re.compile(r"<[@#][!&]?\d+>|@(everyone|here)")

def sanitise(text: str, max_len: int = 32) -> str:
    """Strip Discord mention syntax and cap length."""
    text = _DISCORD_MENTIONS.sub("", text).strip()
    # Remove characters that could break Discord markdown in unexpected ways
    text = re.sub(r"[`*_~|\\]", "", text)
    return text[:max_len]

# ──────────────────────────────────────────────────────────────────────────────
# GIF CATALOGUE
# ──────────────────────────────────────────────────────────────────────────────
GIFS = {
    "bow":       "https://tenor.com/view/seal-bow-seal-gif-6926989540960313219",
    "jumpscare": "https://tenor.com/view/seal-mad-seal-pinniped-jumpscare-seal-jumpscare-gif-8856188141037886958",
    "angry1":    "https://klipy.com/gifs/seal-angry-seal",
    "angry2":    "https://klipy.com/gifs/seal-seals-17",
    "goodluck":  "https://klipy.com/gifs/gabsu-cat-1",
    "slap":      "https://tenor.com/view/mashiro-mashiro-seal-belly-slap-tokkari-tokkari-center-gif-6155972453634300407",
}

GIF_POOLS = {
    "gaming":   ["jumpscare", "angry1", "slap", "angry2"],
    "vc":       ["jumpscare", "angry1", "slap"],
    "periodic": ["bow", "angry2", "slap"],
    "critical": ["jumpscare", "slap", "angry1", "angry2"],
    "congrats": ["goodluck", "bow"],
}

def maybe_gif(mode: str) -> str | None:
    if random.random() > GIF_CHANCE:
        return None
    pool = GIF_POOLS.get(mode, list(GIFS.keys()))
    return GIFS[random.choice(pool)]

# ──────────────────────────────────────────────────────────────────────────────
# MONTH NORMALISATION  (French + short → full English)
# ──────────────────────────────────────────────────────────────────────────────
MONTH_MAP = {
    "jan": "january",  "fev": "february", "fév": "february",
    "mar": "march",    "mars": "march",   "avr": "april",
    "mai": "may",      "jun": "june",     "juin": "june",
    "jui": "july",     "jul": "july",     "juil": "july",
    "aou": "august",   "aoû": "august",   "août": "august",
    "sep": "september","oct": "october",  "nov": "november",
    "dec": "december", "déc": "december",
}

def normalise_date(raw: str) -> str:
    low = raw.lower()
    for short, full in MONTH_MAP.items():
        low = re.sub(r"\b" + re.escape(short) + r"\b", full, low)
    return low

# ──────────────────────────────────────────────────────────────────────────────
# QUIET HOURS
# ──────────────────────────────────────────────────────────────────────────────
def is_quiet_hours(tz_name: str | None) -> bool:
    try:
        tz  = pytz.timezone(tz_name) if tz_name else pytz.utc
        now = datetime.now(tz)
        h   = now.hour
        if QUIET_HOUR_START > QUIET_HOUR_END:   # crosses midnight
            return h >= QUIET_HOUR_START or h < QUIET_HOUR_END
        return QUIET_HOUR_START <= h < QUIET_HOUR_END
    except Exception:
        return False

# ──────────────────────────────────────────────────────────────────────────────
# NAG MESSAGES
# ──────────────────────────────────────────────────────────────────────────────
NAG_GAMING = [
    ("you're playing **{game}** right now. **{course}** ({weight}%) is in {days} days. just saying.", "jumpscare"),
    ("caught you on **{game}**. **{course}** ({weight}%) — {days} days. the seal is watching.", "jumpscare"),
    ("**{game}** can wait. **{course}** is in **{days} days** and worth **{weight}%**. close it.", "angry1"),
    ("nice **{game}** session. shame about **{course}** ({weight}%) being in {days} days though.", "angry2"),
    ("**{game}** ranked grind vs **{course}** ({weight}%) in **{days} days**. one of these matters.", "angry1"),
    ("you queued up for **{game}** with **{course}** ({weight}%) in {days} days. bold.", "slap"),
    ("seal spotted: **{game}** open, **{course}** ({weight}%) untouched, {days} days left.", "slap"),
    ("every minute on **{game}** is a minute not studying **{course}** ({weight}%). {days} days.", "angry2"),
    ("**{game}** will still be there after you study. **{course}** ({weight}%) in {days} days won't.", None),
    ("currently playing: **{game}**. currently ignoring: **{course}** ({weight}%). days left: **{days}**.", None),
]

NAG_VOICE = [
    ("you're in VC. **{course}** ({weight}%) is in **{days} days**. the seal does not approve.", "jumpscare"),
    ("vc at {days} days before **{course}** ({weight}%) is due. interesting life choice.", "slap"),
    ("hop off the call. **{course}** ({weight}%) isn't gonna study itself — **{days} days**.", "angry1"),
    ("having fun in VC while **{course}** ({weight}%) looms in {days} days. ok.", None),
    ("the seal has clocked you in VC. **{course}** ({weight}%). {days} days. leave.", "angry2"),
]

NAG_PERIODIC = [
    ("**{course}** ({weight}%) is due **{date}**. that's {days} days. just making sure you know.", "bow"),
    ("📅 {days} days until **{course}** ({weight}%). not stressing you, just… noting it.", None),
    ("**{course}** ({weight}%) — {days} days left (due {date}). where are you on this?", None),
    ("you have {days} days for **{course}** ({weight}%). use them.", "slap"),
    ("the deadline for **{course}** ({weight}%) is {date}. {days} days. the seal remembers.", "bow"),
    ("{days} days until **{course}** ({weight}%). this is your {days}-day warning.", None),
    ("quick check-in: **{course}** ({weight}%) — {days} days. you good?", None),
]

NAG_CRITICAL = [
    ("**{course}** ({weight}%) is due **tomorrow**. the seal is not happy.", "slap"),
    ("ONE day left for **{course}** ({weight}%). what are you doing on discord.", "jumpscare"),
    ("**{course}** ({weight}%) — {days} day(s). log off. study. go.", "angry1"),
    ("this is not a drill. **{course}** ({weight}%) is due in {days} day(s).", "angry2"),
    ("{days} day(s) for **{course}** ({weight}%). the seal is fully awake and watching you.", "slap"),
]

CONGRATS = [
    "**{course}** done ✅ the seal is proud of you. go touch some grass.",
    "**{course}** crossed off. good work. the seal acknowledges your effort.",
    "one less thing on the list. **{course}** ✅ rest up, you earned it.",
    "**{course}** — done. the seal approves. treat yourself.",
    "**{course}** is history. the seal bows. now get the next one.",
]

# Demo deadline used by !demo command
DEMO_DEADLINE = {"course": "DEMO101", "weight": 30.0, "date": date.today().isoformat(), "notified_days": []}

# ──────────────────────────────────────────────────────────────────────────────
# NAG BUILDER
# ──────────────────────────────────────────────────────────────────────────────
def build_nag(template: str, d: dict, game: str = "") -> str:
    dt   = date.fromisoformat(d["date"])
    days = max(0, (dt - date.today()).days)
    return template.format(
        course=d["course"],
        weight=d["weight"],
        date=dt.strftime("%b %d"),
        days=days,
        game=game or "a game",
    )

def pick_nag(d: dict, mode: str, game: str = "") -> tuple[str, str | None]:
    days = max(0, (date.fromisoformat(d["date"]) - date.today()).days)
    if days <= 1:
        template, gif_hint = random.choice(NAG_CRITICAL)
    else:
        pool = {"gaming": NAG_GAMING, "vc": NAG_VOICE, "periodic": NAG_PERIODIC}.get(mode, NAG_PERIODIC)
        template, gif_hint = random.choice(pool)

    msg = build_nag(template, d, game)
    gif = None
    if random.random() < GIF_CHANCE:
        gif = GIFS.get(gif_hint) if gif_hint else None
        if not gif:
            gif = GIFS[random.choice(GIF_POOLS.get(mode, list(GIFS.keys())))]
    return msg, gif

async def send_nag(channel, msg: str, gif: str | None):
    await channel.send(msg)
    if gif:
        await channel.send(gif)

# ──────────────────────────────────────────────────────────────────────────────
# URGENCY LABEL
# ──────────────────────────────────────────────────────────────────────────────
def urgency_label(days: int) -> str:
    if days <= 1:  return "🚨 CRITICAL"
    if days <= 3:  return "🔴 URGENT"
    if days <= 7:  return "🟠 SOON"
    if days <= 14: return "🟡 UPCOMING"
    return "📘"

def fmt_deadline(d: dict) -> str:
    dt   = date.fromisoformat(d["date"])
    days = (dt - date.today()).days
    lvl  = urgency_label(days)
    return f"{lvl} **{d['course']}** — {d['weight']}% — due **{dt.strftime('%b %d')}** ({days}d)"

# ──────────────────────────────────────────────────────────────────────────────
# PER-USER DATA  — atomic writes to avoid corruption
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR.mkdir(exist_ok=True)

def user_file(uid: int) -> Path:
    return DATA_DIR / f"{uid}.json"

def load_user(uid: int) -> dict:
    p = user_file(uid)
    if p.exists():
        try:
            with open(p) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupted file — start fresh but keep the file path
            data = {}
        data.setdefault("deadlines", [])
        data.setdefault("username", "unknown")
        data.setdefault("last_activity_nag", None)
        data.setdefault("timezone", None)
        data.setdefault("setup_complete", False)
        data.setdefault("dm_fail_streak", 0)   # consecutive DM failures
        return data
    return {
        "deadlines": [], "username": "unknown",
        "last_activity_nag": None, "timezone": None,
        "setup_complete": False, "dm_fail_streak": 0,
    }

def save_user(uid: int, data: dict):
    """Atomic write: write to tmp file then rename, so partial writes never corrupt."""
    target = user_file(uid)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
        shutil.move(tmp_path, target)
    except Exception as e:
        print(f"⚠️  save_user({uid}) failed: {e}")
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

def is_new_user(uid: int) -> bool:
    return not user_file(uid).exists()

def get_upcoming(data: dict, within_days: int = NAG_WINDOW_DAYS) -> list:
    today = date.today()
    return sorted(
        [d for d in data["deadlines"]
         if 0 <= (date.fromisoformat(d["date"]) - today).days <= within_days],
        key=lambda d: d["date"],
    )

# ──────────────────────────────────────────────────────────────────────────────
# DEADLINE PARSER
# ──────────────────────────────────────────────────────────────────────────────
DEADLINE_RE = re.compile(
    r"([A-Za-z]{2,6}\d{2,4})"               # course code e.g. INFO4004
    r"\s+"
    r"(\d{1,2})\s+([A-Za-zÀ-ÿ]{3,10})"      # day month
    r"(?:\s+(\d{4}))?"                        # optional year
    r"\s+(\d{1,3}(?:\.\d+)?)\s*%?",          # weight
    re.IGNORECASE,
)

def parse_deadlines_from_text(text: str) -> list[dict]:
    results = []
    for m in DEADLINE_RE.finditer(text):
        if len(results) >= MAX_DEADLINES_PER_MESSAGE:
            break
        course = sanitise(m.group(1).upper(), max_len=12)
        day    = m.group(2)
        month_raw = m.group(3)
        year   = m.group(4) or str(date.today().year)
        weight = min(float(m.group(5)), 100.0)   # cap weight at 100

        raw_date   = f"{day} {month_raw} {year}"
        normalised = normalise_date(raw_date)
        try:
            dt = dateparser.parse(normalised, dayfirst=True)
            if dt is None:
                continue
            parsed_date = dt.date()
            # Reject explicitly past dates
            if parsed_date < date.today():
                if m.group(4):
                    continue  # explicit past year → skip
                parsed_date = parsed_date.replace(year=parsed_date.year + 1)
            results.append({
                "course": course,
                "date":   parsed_date.isoformat(),
                "weight": weight,
                "notified_days": [],
            })
        except Exception:
            continue
    return results

# ──────────────────────────────────────────────────────────────────────────────
# TIMEZONE PARSER
# ──────────────────────────────────────────────────────────────────────────────
TZ_SHORTHANDS = {
    "est": "America/New_York",    "edt": "America/New_York",
    "cst": "America/Chicago",     "cdt": "America/Chicago",
    "mst": "America/Denver",      "mdt": "America/Denver",
    "pst": "America/Los_Angeles", "pdt": "America/Los_Angeles",
    "gmt": "UTC",                 "utc": "UTC",
    "cet": "Europe/Paris",        "cest": "Europe/Paris",
    "eet": "Europe/Helsinki",     "ist": "Asia/Kolkata",
    "jst": "Asia/Tokyo",          "aest": "Australia/Sydney",
    "aedt": "Australia/Sydney",   "nzst": "Pacific/Auckland",
    "et": "America/New_York",
    "toronto": "America/Toronto", "montreal": "America/Toronto",
    "montréal": "America/Toronto","vancouver": "America/Vancouver",
    "calgary": "America/Edmonton","london": "Europe/London",
    "paris": "Europe/Paris",      "berlin": "Europe/Berlin",
    "moscow": "Europe/Moscow",    "dubai": "Asia/Dubai",
    "singapore": "Asia/Singapore","sydney": "Australia/Sydney",
    "la": "America/Los_Angeles",  "ny": "America/New_York",
    "nyc": "America/New_York",    "chicago": "America/Chicago",
}

def parse_timezone(raw: str) -> str | None:
    raw = raw.strip()[:64]   # length cap — prevents abuse
    low = raw.lower()
    if low in TZ_SHORTHANDS:
        return TZ_SHORTHANDS[low]
    try:
        pytz.timezone(raw)
        return raw
    except pytz.UnknownTimeZoneError:
        pass
    # UTC offset e.g. UTC+5, -04:30
    m = re.match(r"^(?:utc|gmt)?([+-]\d{1,2})(?::(\d{2}))?$", low)
    if m:
        hours   = int(m.group(1))
        minutes = int(m.group(2) or 0)
        total   = hours * 60 + (minutes if hours >= 0 else -minutes)
        try:
            offset_tz = pytz.FixedOffset(total)
            # Return a consistent string representation
            sign  = "+" if total >= 0 else "-"
            abs_h = abs(total) // 60
            abs_m = abs(total) % 60
            return f"Etc/GMT{'+' if hours <= 0 else '-'}{abs_h}"  # pytz sign convention
        except Exception:
            pass
    return None

# ──────────────────────────────────────────────────────────────────────────────
# WELCOME / HELP MESSAGES
# ──────────────────────────────────────────────────────────────────────────────
def make_welcome() -> str:
    return f"""\
🦭 **Hey, I'm Studious Seal.**

I track your deadlines and check in on you when you're supposed to be studying \
— mostly when I catch you gaming. I try not to be annoying about it.

─────────────────────────────────
**➕ Add deadlines** — just DM me naturally:

> `INFO4004 23 mars 25%`
> `[MATH101 14 april 40%, ENG202 2 mai 15%]`

Format: **`COURSECODE  Day Month  Weight%`**
French months work: mars, avr, mai, juin, juil, août, sep, oct, nov, déc

─────────────────────────────────
**📋 Commands**

`!list`                — see your upcoming deadlines
`!done COURSECODE`     — mark one as complete
`!clear`               — wipe all deadlines
`!timezone TIMEZONE`   — set your timezone (kills late-night nags)
`!nag`                 — get a reminder right now
`!demo`                — see what a nag looks like
`!invite`              — get the bot invite link
`!status`              — check cooldown / tz / next nag
`!help`                — show this message

─────────────────────────────────
**🔔 How it works**

• Checks every **{ACTIVITY_CHECK_MINUTES} min** if you're playing a game — nags you if a deadline is close
• VC only triggers within **{VC_CRITICAL_DAYS} days** of a deadline
• Scheduled nudges fire at: 🟡 14d → 🟠 7d → 🔴 3d → 🚨 1d
• No messages between **10 PM – 8 AM** once you set a timezone
• ~25% of nags include a seal gif

─────────────────────────────────
What's your timezone?
(e.g. `EST`, `America/Toronto`, `Europe/Paris`, `UTC+5`)
"""

# ──────────────────────────────────────────────────────────────────────────────
# BOT SETUP
# ──────────────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.presences       = True
intents.members         = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Users currently in the timezone-setup flow (uid → True)
# Survives only in memory — on_message re-populates on bot restart
_awaiting_tz: set[int] = set()

# DM channel cache — avoids repeated fetch_user() calls in the hot loop
_dm_cache: dict[int, discord.DMChannel] = {}

async def get_dm(uid: int) -> discord.DMChannel | None:
    """Get (cached) DM channel for a user, return None on failure."""
    if uid in _dm_cache:
        return _dm_cache[uid]
    try:
        user = await bot.fetch_user(uid)
        dm   = await user.create_dm()
        _dm_cache[uid] = dm
        return dm
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None

# ──────────────────────────────────────────────────────────────────────────────
# EVENTS
# ──────────────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    user_count  = len(list(DATA_DIR.glob("*.json")))
    invite_url  = get_invite_url()
    print(f"╔══════════════════════════════════════════╗")
    print(f"  🦭  Studious Seal is online")
    print(f"  Bot tag   : {bot.user}")
    print(f"  Bot ID    : {bot.user.id}")
    print(f"  Servers   : {', '.join(g.name for g in bot.guilds) or 'none'}")
    print(f"  Users     : {user_count} tracked")
    print(f"  Invite    : {invite_url}")
    print(f"╚══════════════════════════════════════════╝")
    if not activity_watcher.is_running():
        activity_watcher.start()
    if not periodic_nag.is_running():
        periodic_nag.start()

@bot.event
async def on_message(message: discord.Message):
    # Ignore all bots
    if message.author.bot:
        return

    # Only handle DMs in this block — pass guild messages straight to commands
    if not isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return

    uid     = message.author.id
    content = message.content.strip()

    # ── First-time welcome ────────────────────────────────────────
    if is_new_user(uid):
        await message.channel.send(make_welcome())
        save_user(uid, {
            "deadlines": [], "username": str(message.author),
            "last_activity_nag": None, "timezone": None,
            "setup_complete": False, "dm_fail_streak": 0,
        })
        _awaiting_tz.add(uid)
        print(f"📁 New user: {message.author} ({uid})")
        return

    data = load_user(uid)

    # ── Re-add to tz flow if setup never completed (e.g. after bot restart) ──
    if not data.get("setup_complete") and uid not in _awaiting_tz and not content.startswith("!"):
        _awaiting_tz.add(uid)

    # ── Timezone capture flow ─────────────────────────────────────
    if uid in _awaiting_tz and not content.startswith("!"):
        tz = parse_timezone(content)
        if tz:
            data["timezone"]       = tz
            data["setup_complete"] = True
            save_user(uid, data)
            _awaiting_tz.discard(uid)
            try:
                local_now = datetime.now(pytz.timezone(tz)).strftime("%I:%M %p")
                await message.channel.send(
                    f"✅ Timezone set to **{tz}** (your time: **{local_now}**).\n"
                    f"I'll stay quiet between 10 PM and 8 AM.\n\n"
                    f"Now send me your deadlines — e.g. `INFO4004 23 mars 25%`"
                )
            except Exception:
                await message.channel.send(
                    f"✅ Timezone set to **{tz}**.\n\n"
                    f"Now send me your deadlines — e.g. `INFO4004 23 mars 25%`"
                )
        else:
            await message.channel.send(
                f"I don't recognise `{content[:50]}` as a timezone.\n"
                f"Try: `EST` · `America/Montreal` · `Europe/Paris` · `UTC-5`\n"
                f"Or skip it with `!timezone skip` and set it later with `!timezone`."
            )
        return

    # ── Keep username current ─────────────────────────────────────
    if data.get("username") != str(message.author):
        data["username"] = str(message.author)
        save_user(uid, data)

    # ── Parse deadlines from free-form text ──────────────────────
    if not content.startswith("!"):
        parsed = parse_deadlines_from_text(content)
        if parsed:
            existing_courses = {d["course"] for d in data["deadlines"]}
            # Enforce per-user deadline cap
            slots_left = MAX_DEADLINES_PER_USER - len(data["deadlines"])
            added = []
            for d in parsed:
                if slots_left <= 0:
                    break
                if d["course"] not in existing_courses:
                    data["deadlines"].append(d)
                    added.append(d)
                    existing_courses.add(d["course"])
                    slots_left -= 1
            save_user(uid, data)

            if added:
                lines = "\n".join(fmt_deadline(d) for d in added)
                extra = ""
                if len(data["deadlines"]) >= MAX_DEADLINES_PER_USER:
                    extra = f"\n⚠️ You've hit the {MAX_DEADLINES_PER_USER}-deadline limit. Use `!done` to free up space."
                await message.channel.send(
                    f"✅ Added **{len(added)}** deadline(s):\n{lines}\n\n"
                    f"I'll check in as they get close.{extra}"
                )
            else:
                await message.channel.send(
                    "those courses are already tracked. "
                    "`!done COURSECODE` to remove one, `!list` to see your list."
                )
            return

    await bot.process_commands(message)

# ──────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────────────────────────────────────
@bot.command(name="list", aliases=["show"])
async def cmd_list(ctx):
    uid  = ctx.author.id
    data = load_user(uid)
    today = date.today()
    upcoming = sorted(
        [d for d in data["deadlines"] if (date.fromisoformat(d["date"]) - today).days >= 0],
        key=lambda d: d["date"],
    )
    if not upcoming:
        await ctx.send("no deadlines tracked. send me one like `INFO4004 23 mars 25%`")
        return
    lines = "\n".join(fmt_deadline(d) for d in upcoming)
    await ctx.send(f"📋 **your deadlines:**\n{lines}")

@bot.command(name="done", aliases=["remove", "rm", "complete"])
async def cmd_done(ctx, course: str = ""):
    if not course:
        await ctx.send("usage: `!done COURSECODE`")
        return
    uid   = ctx.author.id
    data  = load_user(uid)
    clean = sanitise(course.upper(), max_len=12)
    before            = len(data["deadlines"])
    data["deadlines"] = [d for d in data["deadlines"] if d["course"] != clean]
    save_user(uid, data)
    removed = before - len(data["deadlines"])
    if removed:
        msg = random.choice(CONGRATS).format(course=clean)
        gif = maybe_gif("congrats")
        await ctx.send(msg)
        if gif:
            await ctx.send(gif)
    else:
        await ctx.send(f"**{clean}** not found. try `!list`.")

@bot.command(name="clear")
async def cmd_clear(ctx):
    uid  = ctx.author.id
    data = load_user(uid)
    data["deadlines"] = []
    save_user(uid, data)
    await ctx.send("cleared. fresh slate.")

@bot.command(name="timezone", aliases=["tz", "settz"])
async def cmd_timezone(ctx, *, raw: str = ""):
    if not raw:
        await ctx.send(
            "usage: `!timezone TIMEZONE`\n"
            "examples: `EST` · `America/Toronto` · `Europe/Paris` · `UTC+5`\n"
            "type `!timezone skip` to opt out of quiet hours"
        )
        return
    if raw.strip().lower() == "skip":
        uid  = ctx.author.id
        data = load_user(uid)
        data["timezone"]       = None
        data["setup_complete"] = True
        _awaiting_tz.discard(uid)
        save_user(uid, data)
        await ctx.send("ok, no quiet hours set. I might message you at weird times.")
        return
    tz = parse_timezone(raw)
    if not tz:
        await ctx.send(
            f"I don't recognise `{raw[:50]}`. try:\n"
            "`EST` · `America/Montreal` · `Europe/Paris` · `UTC-5`"
        )
        return
    uid  = ctx.author.id
    data = load_user(uid)
    data["timezone"]       = tz
    data["setup_complete"] = True
    _awaiting_tz.discard(uid)
    save_user(uid, data)
    try:
        local_now = datetime.now(pytz.timezone(tz)).strftime("%I:%M %p")
        await ctx.send(
            f"✅ timezone set to **{tz}** (your time: **{local_now}**).\n"
            "I'll stay quiet between 10 PM and 8 AM."
        )
    except Exception:
        await ctx.send(f"✅ timezone set to **{tz}**.")

@bot.command(name="nag")
async def cmd_nag(ctx):
    uid  = ctx.author.id
    data = load_user(uid)
    upcoming = sorted(
        [d for d in data["deadlines"] if (date.fromisoformat(d["date"]) - date.today()).days >= 0],
        key=lambda d: d["date"],
    )
    if not upcoming:
        await ctx.send("nothing coming up. enjoy it.")
        return
    msg, gif = pick_nag(upcoming[0], "periodic")
    await send_nag(ctx, msg, gif)

@bot.command(name="demo")
async def cmd_demo(ctx):
    """Show judges / new users what a nag looks like — no deadline needed."""
    modes   = ["gaming", "vc", "periodic"]
    mode    = random.choice(modes)
    game    = random.choice(["Valorant", "Minecraft", "League of Legends", "CS2"])
    d       = DEMO_DEADLINE.copy()
    d["date"] = (date.today() + __import__("datetime").timedelta(days=random.randint(1, 7))).isoformat()
    msg, gif = pick_nag(d, mode, game=game)
    await ctx.send("**(demo — this is what a nag looks like)**")
    await send_nag(ctx, msg, gif)

@bot.command(name="invite")
async def cmd_invite(ctx):
    """Return the bot's invite link."""
    url = get_invite_url()
    await ctx.send(
        f"🦭 **Invite Studious Seal to your server:**\n{url}\n\n"
        f"Once it's in your server, just DM the bot to get started."
    )

@bot.command(name="help")
async def cmd_help(ctx):
    await ctx.send(make_welcome())

@bot.command(name="status")
async def cmd_status(ctx):
    uid  = ctx.author.id
    data = load_user(uid)

    tz_name   = data.get("timezone") or "not set"
    quiet     = is_quiet_hours(data.get("timezone"))
    quiet_str = "🔕 quiet hours active" if quiet else "✅ active"

    last_nag_str = data.get("last_activity_nag")
    if last_nag_str:
        try:
            last_nag  = datetime.fromisoformat(last_nag_str)
            elapsed   = (datetime.utcnow() - last_nag).total_seconds() / 60
            remaining = max(0, ACTIVITY_NAG_COOLDOWN_MINUTES - elapsed)
            cd_str = (
                f"last nag **{int(elapsed)} min ago** — next in **{int(remaining)} min**"
                if remaining > 0 else
                "cooldown expired — will nag on next detection ✅"
            )
        except ValueError:
            cd_str = "no data"
    else:
        cd_str = "no activity nag sent yet"

    upcoming = get_upcoming(data, within_days=365)
    await ctx.send(
        f"**📊 status**\n"
        f"deadlines tracked: **{len(upcoming)}** / {MAX_DEADLINES_PER_USER}\n"
        f"timezone: **{tz_name}**\n"
        f"right now: {quiet_str}\n"
        f"activity cooldown: {cd_str}\n"
        f"check interval: every **{ACTIVITY_CHECK_MINUTES} min**"
    )

# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND TASK — activity watcher
# ──────────────────────────────────────────────────────────────────────────────
@tasks.loop(minutes=ACTIVITY_CHECK_MINUTES)
async def activity_watcher():
    now = datetime.utcnow()

    for json_path in DATA_DIR.glob("*.json"):
        # Skip temp files left by atomic writes
        if json_path.suffix == ".tmp":
            continue
        try:
            uid = int(json_path.stem)
        except ValueError:
            continue

        data = load_user(uid)

        # Skip users who have blocked DMs too many times
        if data.get("dm_fail_streak", 0) >= MAX_FAIL_STREAK:
            continue

        upcoming = get_upcoming(data)
        if not upcoming:
            continue

        # Quiet hours
        if is_quiet_hours(data.get("timezone")):
            continue

        # Cooldown
        last_nag_str = data.get("last_activity_nag")
        if last_nag_str:
            try:
                last_nag = datetime.fromisoformat(last_nag_str)
                if (now - last_nag).total_seconds() < ACTIVITY_NAG_COOLDOWN_MINUTES * 60:
                    continue
            except ValueError:
                pass

        # Find member across all guilds
        member = None
        for guild in bot.guilds:
            m = guild.get_member(uid)
            if m:
                member = m
                break
        if member is None:
            continue

        # Detect real game
        game_name = None
        for activity in member.activities:
            aname = getattr(activity, "name", "") or ""
            if not aname:
                continue
            if isinstance(activity, discord.Game) and is_real_game(aname):
                game_name = aname
                break
            if (isinstance(activity, discord.Activity)
                    and activity.type == discord.ActivityType.playing
                    and is_real_game(aname)):
                game_name = aname
                break

        # VC only within VC_CRITICAL_DAYS
        is_in_vc  = member.voice is not None
        days_left = (date.fromisoformat(upcoming[0]["date"]) - date.today()).days
        vc_active = is_in_vc and days_left <= VC_CRITICAL_DAYS

        if not game_name and not vc_active:
            continue

        mode     = "gaming" if game_name else "vc"
        msg, gif = pick_nag(upcoming[0], mode, game=game_name or "")

        dm = await get_dm(uid)
        if dm is None:
            data["dm_fail_streak"] = data.get("dm_fail_streak", 0) + 1
            save_user(uid, data)
            continue

        try:
            await send_nag(dm, msg, gif)
            data["last_activity_nag"] = now.isoformat()
            data["dm_fail_streak"]    = 0
            save_user(uid, data)
            print(f"🔔 [{mode}] → {data.get('username', uid)} ({game_name or 'vc'})")
        except (discord.Forbidden, discord.HTTPException) as e:
            data["dm_fail_streak"] = data.get("dm_fail_streak", 0) + 1
            save_user(uid, data)
            print(f"⚠️  DM failed for {uid}: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND TASK — periodic reminders
# ──────────────────────────────────────────────────────────────────────────────
@tasks.loop(minutes=PERIODIC_NAG_MINUTES)
async def periodic_nag():
    THRESHOLDS = [14, 7, 3, 1]
    today = date.today()

    for json_path in DATA_DIR.glob("*.json"):
        if json_path.suffix == ".tmp":
            continue
        try:
            uid = int(json_path.stem)
        except ValueError:
            continue

        data = load_user(uid)

        if data.get("dm_fail_streak", 0) >= MAX_FAIL_STREAK:
            continue
        if is_quiet_hours(data.get("timezone")):
            continue

        changed = False
        for d in data["deadlines"]:
            days = (date.fromisoformat(d["date"]) - today).days
            if days < 0:
                continue
            notified = set(d.get("notified_days", []))
            for threshold in THRESHOLDS:
                if days <= threshold and threshold not in notified:
                    msg, gif = pick_nag(d, "periodic")
                    label    = urgency_label(days)
                    dm = await get_dm(uid)
                    if dm is None:
                        data["dm_fail_streak"] = data.get("dm_fail_streak", 0) + 1
                        break
                    try:
                        await dm.send(label)
                        await send_nag(dm, msg, gif)
                        notified.add(threshold)
                        d["notified_days"] = list(notified)
                        data["dm_fail_streak"] = 0
                        changed = True
                    except (discord.Forbidden, discord.HTTPException):
                        data["dm_fail_streak"] = data.get("dm_fail_streak", 0) + 1
                    break

        if changed:
            save_user(uid, data)

@activity_watcher.before_loop
@periodic_nag.before_loop
async def _before():
    await bot.wait_until_ready()

# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG, reconnect=True)
