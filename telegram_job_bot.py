#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import sys
import threading
from datetime import datetime, timedelta, time as dtime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return int(default)


def resolve_config():
    cfg = {}
    cfg["bot_token"] = os.environ.get("BOT_TOKEN", "").strip()
    ids = [x.strip() for x in os.environ.get("CHAT_IDS", "").split(",") if x.strip()]
    cfg["chat_ids"] = [int(x) for x in ids if x.lstrip("-").isdigit()]
    cfg["db_path"] = os.environ.get("JOB_DB_PATH", "jobs_database.json")
    cfg["state_file"] = os.environ.get("STATE_FILE", "telegram_bot_state.json")
    cfg["check_interval"] = max(1, get_int("CHECK_INTERVAL_MINUTES", 10))
    digest = os.environ.get("DIGEST_TIME", "08:00")
    try:
        hh, mm = digest.split(":")
        cfg["digest_time"] = (int(hh), int(mm))
    except (ValueError, AttributeError):
        cfg["digest_time"] = (8, 0)
    cfg["tz_name"] = os.environ.get("TZ", "").strip() or None
    cfg["tz_offset_minutes"] = get_int("TZ_OFFSET_MINUTES", 330)
    cfg["user_age_min"] = get_int("USER_AGE_MIN", 25)
    cfg["user_age_max"] = get_int("USER_AGE_MAX", 30)
    branches = [b.strip().lower() for b in os.environ.get("USER_BRANCHES", "it").split(",") if b.strip()]
    cfg["user_branches"] = branches or ["it"]
    cfg["port"] = get_int("PORT", 8080)
    return cfg


def parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_jobs(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("Database not found: {}".format(p))
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("jobs", [])


def job_matches(job, cfg):
    ef = job.get("eligibility_filters") or {}
    gate = ef.get("gate_required", bool(job.get("requires_gate", False)))
    if gate:
        return False
    level = (ef.get("max_qualification_level") or "bachelor").lower()
    if level not in ("secondary", "diploma", "bachelor"):
        return False
    branches = [b.lower() for b in ef.get("branches", ["general"])]
    user_branches = [b.lower() for b in cfg["user_branches"]]
    if (
        "general" not in branches
        and "all" not in branches
        and not any(b in branches for b in user_branches)
    ):
        return False
    min_age = ef.get("min_age", 0) or 0
    max_age = ef.get("max_age", 99) or 99
    if max_age < cfg["user_age_min"] or min_age > cfg["user_age_max"]:
        return False
    return True


def is_active(job):
    deadline = job.get("application_deadline")
    d = parse_date(deadline)
    if d:
        return d >= datetime.now()
    return True


def matching_jobs(jobs, cfg):
    return [j for j in jobs if job_matches(j, cfg) and is_active(j)]


def deadline_parts(job):
    deadline = job.get("application_deadline")
    if deadline:
        d = parse_date(deadline)
        if d:
            days = (d - datetime.now()).days
            return deadline, days
        return deadline, None
    return job.get("deadline_info", "Not specified"), None


def age_overlap(job, cfg):
    ef = job.get("eligibility_filters") or {}
    low = max(ef.get("min_age", 0) or 0, cfg["user_age_min"])
    high = min(ef.get("max_age", 99) or 99, cfg["user_age_max"])
    if low <= high:
        return "{}-{}".format(low, high)
    return "n/a"


def age_text(job, cfg):
    ef = job.get("eligibility_filters") or {}
    low = ef.get("min_age", 0) or 0
    high = ef.get("max_age", 99) or 99
    if high >= 90 and low <= 15:
        base = "No age limit"
    else:
        base = "{}-{} years".format(low, high)
    raw = job.get("eligibility", {}).get("age")
    if raw and base.lower() not in raw.lower():
        base = "{} ({})".format(base, raw)
    return "{} - your eligible part: {} yrs".format(base, age_overlap(job, cfg))


def job_card(job, cfg):
    deadline, days = deadline_parts(job)
    days_txt = ""
    if days is not None:
        if days < 0:
            days_txt = "\u274C CLOSED"
        elif days <= 7:
            days_txt = "\U0001F6A8 Only {} day{} left!".format(days, "s" if days != 1 else "")
        elif days <= 30:
            days_txt = "\u23F3 {} days remaining".format(days)
        else:
            days_txt = "\u2705 {} days to apply".format(days)
    lines = [
        "\U0001F3AF {}".format(job.get("name", "Unknown Job")),
        "",
        "\U0001F3E2 {}".format(job.get("organization", "Government")),
        "\u2705 Eligible for you: B.E.-IT / Graduate, 25-30, no GATE",
        "",
        "\u2022 Qualification: {}".format(job.get("eligibility", {}).get("qualification", "Not specified")),
        "\u2022 Age: {}".format(age_text(job, cfg)),
        "\U0001F4B0 Salary: {}".format(job.get("salary", "Not specified")),
        "\U0001F9FE Fee: {}".format(job.get("application_fee", "Not specified")),
        "\U0001F5D3 Deadline: {}{}".format(deadline, " ({})".format(days_txt) if days_txt else ""),
    ]
    pattern = job.get("exam_pattern")
    if pattern:
        lines.append("\U0001F4DD Exam: {}".format(pattern[:140]))
    link = job.get("notification_link")
    if link:
        lines.append("")
        lines.append("\U0001F517 Official link: {}".format(link))
    return "\n".join(lines)


def digest_text(jobs, cfg):
    lines = [
        "\U0001F4CB Daily Government Job Digest",
        "Matched {} active jobs for your profile (B.E.-IT / Graduate, 25-30, no GATE)".format(len(jobs)),
        "",
    ]
    for job in jobs:
        deadline, days = deadline_parts(job)
        dl = deadline
        if days is not None and days >= 0:
            dl = "{} ({} days left)".format(dl, days)
        lines.append(job.get("name", "?"))
        lines.append("   \U0001F3E2 {} | \U0001F5D3 {}".format(job.get("organization", "?"), dl))
    return "\n".join(lines)


class JobState:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def notified(self, jid):
        return str(jid) in self.data.get("notified", {})

    def mark(self, job):
        self.data.setdefault("notified", {})[str(job.get("id"))] = {
            "name": job.get("name"),
            "sent_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.save()

    def prune(self, live_jobs):
        live = {str(j.get("id")) for j in live_jobs}
        notified = self.data.get("notified", {})
        removed = [k for k in notified if k not in live]
        for k in removed:
            notified.pop(k, None)
        if removed:
            self.save()


async def send_to_all(context, text):
    cfg = context.bot_data["config"]
    sent = 0
    for cid in cfg["chat_ids"]:
        try:
            await context.bot.send_message(chat_id=cid, text=text, disable_web_page_preview=True)
            sent += 1
        except TelegramError:
            logging.exception("Send failed for chat %s", cid)
    return sent


async def check_new_jobs(context):
    cfg = context.bot_data["config"]
    bot_state = context.bot_data["state"]
    try:
        jobs = load_jobs(cfg["db_path"])
    except Exception:
        logging.exception("Database load failed")
        return
    matches = matching_jobs(jobs, cfg)
    pushed = 0
    for job in matches:
        jid = str(job.get("id"))
        if bot_state.notified(jid):
            continue
        sent = await send_to_all(context, job_card(job, cfg))
        if sent > 0:
            bot_state.mark(job)
            pushed += 1
    bot_state.prune(jobs)
    logging.info("Check: %d matching jobs, %d new notifications pushed", len(matches), pushed)


async def daily_digest(context):
    cfg = context.bot_data["config"]
    try:
        jobs = load_jobs(cfg["db_path"])
    except Exception:
        logging.exception("Database load failed for digest")
        return
    matches = matching_jobs(jobs, cfg)
    if not matches:
        await send_to_all(context, "\U0001F4CB Daily digest: No matching jobs right now. Will notify you the moment one opens.")
        return
    await send_to_all(context, digest_text(matches, cfg))
    logging.info("Daily digest sent: %d matching jobs", len(matches))


def is_authorized(update, cfg):
    if not cfg["chat_ids"]:
        return True
    chat = update.effective_chat.id
    return chat in cfg["chat_ids"]


async def cmd_start(update, context):
    cfg = context.bot_data["config"]
    chat = update.effective_chat.id
    if not is_authorized(update, cfg):
        await update.message.reply_text("Not authorized.")
        return
    try:
        jobs = load_jobs(cfg["db_path"])
    except Exception:
        jobs = []
    matches = matching_jobs(jobs, cfg)
    text = (
        "\U0001F4A1 Government Jobs Bot\n\n"
        "Profile targeted:\n"
        "\u2022 Education: B.E.-IT (or any graduate)\n"
        "\u2022 No GATE score required\n"
        "\u2022 Age: {}-{} years\n\n"
        "Currently matched: {} jobs\n\n"
        "Commands:\n"
        "/jobs \u2014 list matching jobs now\n"
        "/refresh \u2014 check for new jobs immediately\n"
        "/status \u2014 bot settings\n\n"
        "Your chat ID: {}\n"
        "Set CHAT_IDS in the bot environment to lock access to this ID.".format(
            cfg["user_age_min"], cfg["user_age_max"], len(matches), chat
        )
    )
    await update.message.reply_text(text)


async def cmd_jobs(update, context):
    cfg = context.bot_data["config"]
    if not is_authorized(update, cfg):
        await update.message.reply_text("Not authorized.")
        return
    try:
        jobs = load_jobs(cfg["db_path"])
    except Exception:
        await update.message.reply_text("Could not read the jobs database.")
        return
    matches = matching_jobs(jobs, cfg)
    if not matches:
        await update.message.reply_text("No matching jobs right now.")
        return
    await update.message.reply_text("Found {} matching jobs:".format(len(matches)))
    for job in matches:
        await update.message.reply_text(job_card(job, cfg), disable_web_page_preview=True)


async def cmd_refresh(update, context):
    cfg = context.bot_data["config"]
    if not is_authorized(update, cfg):
        await update.message.reply_text("Not authorized.")
        return
    await check_new_jobs(context)
    await update.message.reply_text("Checked for new matching jobs. New ones were pushed to the configured chat(s).")


async def cmd_status(update, context):
    cfg = context.bot_data["config"]
    if not is_authorized(update, cfg):
        await update.message.reply_text("Not authorized.")
        return
    bot_state = context.bot_data["state"]
    text = (
        "\U0001F527 Bot Status\n\n"
        "Database: {}\n"
        "Configured chats: {}\n"
        "Check interval: every {} min\n"
        "Daily digest: {:02d}:{:02d}\n"
        "Profile: B.E.-IT / Graduate, {}-{} years, no GATE\n"
        "Jobs already notified: {}".format(
            cfg["db_path"],
            cfg["chat_ids"] or "NONE - notifications disabled",
            cfg["check_interval"],
            cfg["digest_time"][0],
            cfg["digest_time"][1],
            cfg["user_age_min"],
            cfg["user_age_max"],
            len(bot_state.data.get("notified", {})),
        )
    )
    await update.message.reply_text(text)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def start_health_server(port):
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logging.info("Health server listening on port %s (for uptime keep-alive)", port)
    return server


def digest_utc_time(hh, mm, offset_minutes):
    total = (hh * 60 + mm - offset_minutes) % 1440
    return total // 60, total % 60


def build_app(cfg):
    if not cfg["bot_token"]:
        logging.error("BOT_TOKEN is required. Copy .env.example to .env and fill it in.")
        raise SystemExit(1)

    builder = ApplicationBuilder().token(cfg["bot_token"])
    effective_tz = None
    if cfg["tz_name"]:
        zone = None
        if HAS_PYTZ:
            try:
                zone = pytz.timezone(cfg["tz_name"])
            except pytz.UnknownTimeZoneError:
                zone = None
        elif ZoneInfo is not None:
            try:
                zone = ZoneInfo(cfg["tz_name"])
            except Exception:
                zone = None
        if zone is not None:
            try:
                builder = builder.timezone(zone)
                effective_tz = zone
            except Exception as exc:
                logging.warning("Could not apply timezone %s: %s", cfg["tz_name"], exc)
    app = builder.build()
    cfg["_effective_tz"] = bool(effective_tz)
    app.bot_data["config"] = cfg
    app.bot_data["state"] = JobState(cfg["state_file"])
    return app


def schedule_jobs(app, cfg):
    app.job_queue.run_repeating(
        check_new_jobs,
        interval=timedelta(minutes=cfg["check_interval"]),
        first=10,
        name="new_jobs_check",
    )
    hh, mm = cfg["digest_time"]
    if cfg["_effective_tz"]:
        app.job_queue.run_daily(daily_digest, time=dtime(hour=hh, minute=mm), name="daily_digest")
        logging.info("Daily digest scheduled at %02d:%02d in configured timezone (%s)", hh, mm, cfg["tz_name"])
    else:
        uh, um = digest_utc_time(hh, mm, cfg["tz_offset_minutes"])
        app.job_queue.run_daily(daily_digest, time=dtime(hour=uh, minute=um), name="daily_digest")
        logging.info(
            "Daily digest scheduled at %02d:%02d (converted from %02d:%02d by %d min; assumes server UTC)",
            uh, um, hh, mm, cfg["tz_offset_minutes"],
        )


def check_mode(cfg):
    jobs = load_jobs(cfg["db_path"])
    matches = matching_jobs(jobs, cfg)
    print("Profile: B.E.-IT / Graduate, age {}-{}, no GATE".format(cfg["user_age_min"], cfg["user_age_max"]))
    print("Total jobs in DB: {}".format(len(jobs)))
    print("Matching jobs: {}\n".format(len(matches)))
    for job in matches:
        print(job_card(job, cfg))
        print("-" * 50)
    print("\nRemaining jobs (excluded):")
    for job in jobs:
        if not job_matches(job, cfg):
            print("  - {}".format(job.get("name")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Print matching jobs locally and exit (no Telegram needed)")
    args = parser.parse_args()

    cfg = resolve_config()

    if args.check:
        check_mode(cfg)
        return

    print("=" * 60)
    print("Government Jobs Bot")
    print("=" * 60)
    print("Profile: B.E.-IT / Graduate, age {}-{}, no GATE".format(cfg["user_age_min"], cfg["user_age_max"]))
    print("Database: {}".format(cfg["db_path"]))

    if not cfg["chat_ids"]:
        logging.warning("CHAT_IDS not configured - notifications disabled.")
        logging.warning("Message the bot with /start, copy the chat ID it prints, then set CHAT_IDS.")

    app = build_app(cfg)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("jobs", cmd_jobs))
    app.add_handler(CommandHandler("refresh", cmd_refresh))
    app.add_handler(CommandHandler("status", cmd_status))

    schedule_jobs(app, cfg)
    start_health_server(cfg["port"])

    print("Bot started. Ctrl+C to stop.\n")
    app.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == "__main__":
    main()