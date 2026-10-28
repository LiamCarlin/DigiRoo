#!/usr/bin/env python3
"""Build the posting grid for a DigiRoo week.

Reads the weekly calendar (or just --days/--per-day), spreads posts inside the
posting windows from DIGIROO-brief.md (default 11:00-13:00 and 19:00-21:00 ET),
alternating midday/evening, snapped to 5 minutes, skipping slots < 20 min from
now and flagging anything past TikTok's 10-day native ceiling.

    python3 schedule_grid.py --calendar media/week-01/weekly-calendar.md
    python3 schedule_grid.py --start-date 2026-11-02 --days 5
"""
import argparse, re
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

WINDOWS = [("11:00", "13:00"), ("19:00", "21:00")]
MAX_DAYS_AHEAD = 10
MIN_LEAD_MIN = 20
SNAP = 5

def hm(s):
    h, m = s.split(":"); return int(h), int(m)

def snap(dt):
    return dt.replace(minute=(dt.minute // SNAP) * SNAP, second=0, microsecond=0)

def slot_for(day, idx, tz, seed):
    win = WINDOWS[idx % len(WINDOWS)]
    (sh, sm), (eh, em) = hm(win[0]), hm(win[1])
    start = datetime(day.year, day.month, day.day, sh, sm, tzinfo=tz)
    end = datetime(day.year, day.month, day.day, eh, em, tzinfo=tz)
    span = (end - start).total_seconds() / 60
    # centre of window, nudged by a per-day stagger so the queue isn't all on the hour
    t = start + timedelta(minutes=span * 0.5 + ((seed * 7 + day.toordinal()) % 23) - 11)
    return snap(t)

def parse_calendar(path):
    rows = []
    days = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    week_start = None
    for line in open(path, encoding="utf-8"):
        m = re.search(r"week of (\d{4}-\d{2}-\d{2})", line, re.I)
        if m: week_start = date.fromisoformat(m.group(1))
        if line.startswith("|") and line.split("|")[1].strip()[:3] in days:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append((days[cells[0][:3]], cells))
    return week_start, rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calendar")
    ap.add_argument("--start-date")
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--tz", default="America/New_York")
    a = ap.parse_args()
    tz = ZoneInfo(a.tz); now = datetime.now(tz)
    if a.calendar:
        week_start, rows = parse_calendar(a.calendar)
        items = [(week_start + timedelta(days=d), cells) for d, cells in rows]
    else:
        ws = date.fromisoformat(a.start_date) if a.start_date else now.date()
        items = [(ws + timedelta(days=i), None) for i in range(a.days)]
    cutoff = now + timedelta(minutes=MIN_LEAD_MIN); ceiling = now + timedelta(days=MAX_DAYS_AHEAD)
    print(f"Timezone {a.tz} · windows {WINDOWS} · now {now:%a %b %d %H:%M}\n")
    print(f"{'Day':<12}{'Time':<10}{'TikTok?':<10}Post")
    for i, (day, cells) in enumerate(items):
        t = slot_for(day, i, tz, i)
        flag = "past" if t < cutoff else (">10d: draft" if t > ceiling else "ok")
        label = cells[6] if cells and len(cells) > 6 else ""
        print(f"{t:%a %b %d}   {t:%I:%M %p}  {flag:<10}{label}")

if __name__ == "__main__":
    main()
