#!/usr/bin/env python3
"""
StreakForge — Build unbreakable habits with beautiful terminal streak tracking.

A universal CLI tool for tracking daily habits, creative streaks, and
personal challenges. Visualize your progress with fire charts, milestone
celebrations, and insightful stats — all from your terminal.

Usage:
    streak-forge start "Morning Run"
    streak-forge log "Morning Run"
    streak-forge log "Morning Run" --date 2026-06-01
    streak-forge list
    streak-forge show "Morning Run"
    streak-forge calendar "Morning Run"
    streak-forge stats
    streak-forge rename "Morning Run" "Daily Run"
    streak-forge delete "Morning Run"
    streak-forge export --format json
    streak-forge import habits.json
"""

import argparse
import calendar
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

__version__ = "1.1.0"

# ── Data storage ──────────────────────────────────────────────────────────────

DATA_DIR = Path.home() / ".streak-forge"
DATA_FILE = DATA_DIR / "habits.json"
FREEZE_FILE = DATA_DIR / "freezes.json"

# ── Habit Templates ───────────────────────────────────────────────────────────

HABIT_TEMPLATES = {
    "water": {
        "name": "Drink 8 Glasses of Water",
        "emoji": "💧",
        "target_days": 30,
        "description": "Stay hydrated — drink 8 glasses of water daily",
    },
    "read": {
        "name": "Read 30 Minutes",
        "emoji": "📚",
        "target_days": 30,
        "description": "Read for at least 30 minutes every day",
    },
    "exercise": {
        "name": "Exercise",
        "emoji": "🏋️",
        "target_days": 30,
        "description": "Get at least 30 minutes of physical activity",
    },
    "meditate": {
        "name": "Meditate",
        "emoji": "🧘",
        "target_days": 21,
        "description": "Practice mindfulness meditation for 10+ minutes",
    },
    "journal": {
        "name": "Journal",
        "emoji": "📝",
        "target_days": 30,
        "description": "Write in your journal every day",
    },
    "code": {
        "name": "Code Every Day",
        "emoji": "💻",
        "target_days": 100,
        "description": "Write code daily — even just 15 minutes counts",
    },
    "walk": {
        "name": "Take a Walk",
        "emoji": "🚶",
        "target_days": 30,
        "description": "Go for a walk outside every day",
    },
    "sleep": {
        "name": "Sleep 8 Hours",
        "emoji": "😴",
        "target_days": 30,
        "description": "Get at least 8 hours of sleep each night",
    },
    "gratitude": {
        "name": "Gratitude Practice",
        "emoji": "🙏",
        "target_days": 21,
        "description": "Write down 3 things you're grateful for",
    },
    "stretch": {
        "name": "Stretch",
        "emoji": "🤸",
        "target_days": 30,
        "description": "Do 10+ minutes of stretching every day",
    },
}


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        _save({"habits": [], "logs": {}})


def _load() -> dict:
    ensure_data_dir()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_freezes() -> dict:
    """Load freeze data: {habit_name: [date_strings]}."""
    if not FREEZE_FILE.exists():
        return {}
    with open(FREEZE_FILE, "r") as f:
        return json.load(f)


def _save_freezes(freezes: dict):
    with open(FREEZE_FILE, "w") as f:
        json.dump(freezes, f, indent=2)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()


def _parse_date(s: str) -> str:
    """Validate and normalize a date string."""
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except ValueError:
        console.print(f"[red]Invalid date format: {s}. Use YYYY-MM-DD.[/red]")
        sys.exit(1)


def _streak_for_dates(dates: list[str], freeze_dates: list[str] | None = None) -> int:
    """Calculate current streak from a sorted list of date strings (most recent first).
    
    Freeze dates count as logged days so planned rest days don't break streaks.
    """
    if not dates and not freeze_dates:
        return 0
    all_dates = set(dates) | set(freeze_dates or [])
    sorted_dates = sorted(all_dates, reverse=True)
    today = date.today()
    streak = 0
    check_date = today
    for d_str in sorted_dates:
        d = date.fromisoformat(d_str)
        if d == check_date or (streak == 0 and d == today - timedelta(days=1)):
            streak += 1
            check_date = d - timedelta(days=1)
        elif d == check_date:
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break
    return streak


def _longest_streak(dates: list[str]) -> int:
    if not dates:
        return 0
    sorted_dates = sorted(set(dates))
    longest = current = 1
    for i in range(1, len(sorted_dates)):
        prev = date.fromisoformat(sorted_dates[i - 1])
        curr = date.fromisoformat(sorted_dates[i])
        if (curr - prev).days == 1:
            current += 1
            longest = max(longest, current)
        elif (curr - prev).days > 1:
            current = 1
    return longest


def _fire_emoji(streak: int) -> str:
    if streak == 0:
        return "💤"
    elif streak < 3:
        return "🌱"
    elif streak < 7:
        return "🔥"
    elif streak < 30:
        return "🔥🔥"
    elif streak < 100:
        return "🔥🔥🔥"
    else:
        return "🌋"


def _milestone_message(streak: int) -> Optional[str]:
    milestones = {
        1: "🎉 First step! Every journey begins with a single day!",
        3: "🌱 3-day streak! You're building momentum!",
        7: "🏆 One week! You're on fire!",
        14: "💪 Two weeks! This is becoming a habit!",
        21: "🧠 21 days! Science says it takes 21 days to form a habit!",
        30: "🌟 One month! You're unstoppable!",
        50: "🚀 50 days! Over the moon!",
        66: "⚡ 66 days! New research says 66 days to solidify a habit!",
        100: "💯 CENTURY! You're a legend!",
        365: "🎊 ONE YEAR! You're a STREAK MASTER!",
    }
    return milestones.get(streak)


def _progress_bar(current: int, target: int, width: int = 20) -> str:
    if target <= 0:
        return "░" * width
    ratio = min(current / target, 1.0)
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(ratio * 100)
    return f"{bar} {pct}%"


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args):
    """Create a new habit to track."""
    data = _load()
    name = args.name.strip()
    # Check for duplicates
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            console.print(f"[yellow]⚠[/yellow] Habit '{name}' already exists!")
            console.print(f"   Use [bold]streak-forge log \"{name}\"[/bold] to log today's activity.")
            sys.exit(1)

    habit = {
        "name": name,
        "created_at": _today(),
        "target_days": args.target,
        "emoji": args.emoji or "⭐",
        "color": args.color or "white",
    }
    data["habits"].append(habit)
    if name not in data["logs"]:
        data["logs"][name] = []
    _save(data)

    console.print()
    console.print(Panel(
        f"[bold green]✨ New habit created![/bold green]\n\n"
        f"  {habit['emoji']} [bold]{name}[/bold]\n"
        f"  Target: {args.target} days\n"
        f"  Created: {_today()}\n\n"
        f"[dim]Log your first day with:[/dim]\n"
        f"[bold]  streak-forge log \"{name}\"[/bold]",
        title="🔥 StreakForge",
        border_style="green",
    ))


def cmd_log(args):
    """Log activity for a habit today (or a specific date)."""
    data = _load()
    name = args.name.strip()

    # Find habit (case-insensitive)
    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        console.print(f"   Create it first: [bold]streak-forge start \"{name}\"[/bold]")
        sys.exit(1)

    log_date = _parse_date(args.date) if args.date else _today()

    if habit_name not in data["logs"]:
        data["logs"][habit_name] = []

    if log_date in data["logs"][habit_name]:
        console.print(f"[yellow]⚠[/yellow] '{habit_name}' already logged for {log_date}.")
        return

    data["logs"][habit_name].append(log_date)
    _save(data)

    dates = data["logs"][habit_name]
    freezes = _load_freezes().get(habit_name, [])
    streak = _streak_for_dates(dates, freezes)
    fire = _fire_emoji(streak)

    console.print()
    console.print(f"  {fire} [bold green]Logged![/bold green] '{habit_name}' for {log_date}")
    console.print(f"  Current streak: [bold]{streak}[/bold] day{'s' if streak != 1 else ''}")

    milestone = _milestone_message(streak)
    if milestone:
        console.print()
        console.print(Panel(milestone, border_style="yellow", padding=(0, 2)))


def cmd_list(args):
    """List all tracked habits with their streaks."""
    data = _load()
    habits = data["habits"]

    if not habits:
        console.print(Panel(
            "[dim]No habits tracked yet.[/dim]\n\n"
            "Start your first streak:\n"
            "[bold]  streak-forge start \"My Habit\"[/bold]",
            title="🔥 StreakForge",
            border_style="dim",
        ))
        return

    table = Table(
        title="🔥 StreakForge — Your Habits",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold magenta",
    )
    table.add_column("Emoji", justify="center", width=4)
    table.add_column("Habit", style="bold", min_width=20)
    table.add_column("Streak", justify="right", width=8)
    table.add_column("Longest", justify="right", width=8)
    table.add_column("Total", justify="right", width=6)
    table.add_column("Progress", min_width=28)
    table.add_column("Status", width=6, justify="center")

    total_streaks = 0
    all_freezes = _load_freezes()
    for h in habits:
        name = h["name"]
        dates = data["logs"].get(name, [])
        freezes = all_freezes.get(name, [])
        streak = _streak_for_dates(dates, freezes)
        longest = _longest_streak(dates)
        total = len(dates)
        target = h.get("target_days", 30)
        emoji = h.get("emoji", "⭐")
        fire = _fire_emoji(streak)
        progress = _progress_bar(total, target)

        status = "✅" if total >= target else fire if streak > 0 else "💤"
        total_streaks += streak

        table.add_row(
            emoji,
            name,
            f"[bold]{streak}[/bold]",
            str(longest),
            str(total),
            progress,
            status,
        )

    console.print(table)
    console.print(f"\n  [dim]Total active streaks: [bold]{total_streaks}[/bold] days across {len(habits)} habit{'s' if len(habits) != 1 else ''}[/dim]")
    console.print(f"  [dim]Keep going! Every day counts! 🚀[/dim]\n")


def cmd_show(args):
    """Show detailed info for a specific habit."""
    data = _load()
    name = args.name.strip()

    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            habit = h
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        sys.exit(1)

    dates = sorted(data["logs"].get(habit_name, []))
    freezes = _load_freezes().get(habit_name, [])
    streak = _streak_for_dates(dates, freezes)
    longest = _longest_streak(dates)
    total = len(dates)
    target = habit.get("target_days", 30)
    emoji = habit.get("emoji", "⭐")
    fire = _fire_emoji(streak)

    # Build info panel
    info_lines = [
        f"  {emoji} [bold]{habit_name}[/bold]",
        f"",
        f"  Current Streak:  [bold]{streak}[/bold] days  {fire}",
        f"  Longest Streak:  [bold]{longest}[/bold] days",
        f"  Total Logs:      [bold]{total}[/bold] days",
        f"  Target:          [bold]{target}[/bold] days",
        f"  Progress:        {_progress_bar(total, target)}",
        f"  Created:         {habit.get('created_at', 'N/A')}",
    ]

    if dates:
        info_lines.append(f"  First Log:       {dates[0]}")
        info_lines.append(f"  Last Log:        {dates[-1]}")

    # Recent activity (last 14 days)
    info_lines.append("")
    info_lines.append("  [bold]Recent Activity (last 14 days):[/bold]")
    today = date.today()
    recent = ""
    for i in range(13, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        if d in dates:
            recent += " 🟢"
        else:
            recent += " ⬜"
    info_lines.append(f"  {recent}")
    info_lines.append(f"  [dim]{' '.join(str(i).rjust(2) for i in range(13, -1, -1))}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(info_lines),
        title=f"🔥 StreakForge — {habit_name}",
        border_style="cyan",
    ))


def cmd_calendar(args):
    """Show a GitHub-style contribution calendar for a habit."""
    data = _load()
    name = args.name.strip()

    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        sys.exit(1)

    dates = set(data["logs"].get(habit_name, []))
    today = date.today()

    # Show last 52 weeks
    weeks = 52
    start = today - timedelta(weeks=weeks, days=today.weekday())

    console.print()
    console.print(f"  📅 [bold]StreakForge Calendar — {habit_name}[/bold]")
    console.print(f"  [dim]Last {weeks} weeks[/dim]\n")

    # Month labels
    month_row = "    "
    prev_month = ""
    for w in range(weeks):
        d = start + timedelta(weeks=w)
        month = d.strftime("%b")
        if month != prev_month:
            month_row += month
            prev_month = month
        else:
            month_row += "   "
    console.print(f"  [dim]{month_row}[/dim]")

    # Days: Mon=0 through Sun=6
    day_labels = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    for day in range(7):
        label = f"  {day_labels[day]} "
        row = label
        for w in range(weeks):
            d = start + timedelta(weeks=w, days=day)
            if d > today:
                row += " ⬜"
            elif d.isoformat() in dates:
                row += " 🟢"
            else:
                row += " ⬛"
        console.print(row)

    console.print()
    console.print("  [dim]⬛ No activity  🟢 Logged  ⬜ Future[/dim]")
    console.print()


def cmd_stats(args):
    """Show overall statistics across all habits."""
    data = _load()
    habits = data["habits"]

    if not habits:
        console.print("[dim]No habits to show stats for.[/dim]")
        return

    total_logs = 0
    total_streak = 0
    best_streak = 0
    best_habit = ""
    best_longest = 0
    best_longest_habit = ""
    all_freezes = _load_freezes()

    for h in habits:
        name = h["name"]
        dates = data["logs"].get(name, [])
        freezes = all_freezes.get(name, [])
        streak = _streak_for_dates(dates, freezes)
        longest = _longest_streak(dates)
        total_logs += len(dates)
        total_streak += streak
        if streak > best_streak:
            best_streak = streak
            best_habit = name
        if longest > best_longest:
            best_longest = longest
            best_longest_habit = name

    today = date.today()
    days_since_epoch = (today - date(2025, 1, 1)).days

    console.print()
    console.print(Panel(
        f"  📊 [bold]StreakForge Global Stats[/bold]\n\n"
        f"  Habits Tracked:     [bold]{len(habits)}[/bold]\n"
        f"  Total Active Streaks: [bold]{total_streak}[/bold] days\n"
        f"  Total Logs:         [bold]{total_logs}[/bold]\n"
        f"  Best Active Streak: [bold]{best_streak}[/bold] days"
        f" ({best_habit})\n"
        f"  Best All-Time:      [bold]{best_longest}[/bold] days"
        f" ({best_longest_habit})\n",
        title="🔥 StreakForge",
        border_style="magenta",
    ))


def cmd_rename(args):
    """Rename a habit."""
    data = _load()
    old_name = args.old_name.strip()
    new_name = args.new_name.strip()

    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == old_name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{old_name}' not found.")
        sys.exit(1)

    # Check new name doesn't exist
    for h in data["habits"]:
        if h["name"].lower() == new_name.lower() and h["name"] != habit_name:
            console.print(f"[red]✗[/red] Habit '{new_name}' already exists.")
            sys.exit(1)

    for h in data["habits"]:
        if h["name"] == habit_name:
            h["name"] = new_name
            break

    if habit_name in data["logs"]:
        data["logs"][new_name] = data["logs"].pop(habit_name)

    _save(data)
    console.print(f"  ✏️  Renamed '{habit_name}' → [bold]{new_name}[/bold]")


def cmd_delete(args):
    """Delete a habit and all its logs."""
    data = _load()
    name = args.name.strip()

    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        sys.exit(1)

    if not args.force:
        console.print(f"  [yellow]⚠[/yellow] This will permanently delete '{habit_name}' and all its logs.")
        console.print(f"  Use [bold]--force[/bold] to confirm: streak-forge delete \"{habit_name}\" --force")
        sys.exit(1)

    data["habits"] = [h for h in data["habits"] if h["name"] != habit_name]
    data["logs"].pop(habit_name, None)
    _save(data)
    console.print(f"  🗑️  Deleted '{habit_name}'")


def cmd_freeze(args):
    """Freeze a habit for a specific date (planned rest day that doesn't break streak)."""
    data = _load()
    name = args.name.strip()

    habit_name = None
    for h in data["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        sys.exit(1)

    freeze_date = _parse_date(args.date) if args.date else _today()
    freezes = _load_freezes()

    if habit_name not in freezes:
        freezes[habit_name] = []

    if freeze_date in freezes[habit_name]:
        console.print(f"[yellow]⚠[/yellow] '{habit_name}' is already frozen for {freeze_date}.")
        return

    # Check if already logged on this date
    if freeze_date in data["logs"].get(habit_name, []):
        console.print(f"[yellow]⚠[/yellow] '{habit_name}' is already logged for {freeze_date}.")
        console.print(f"   A freeze is not needed — you've already completed it!")
        return

    freezes[habit_name].append(freeze_date)
    freezes[habit_name].sort()
    _save_freezes(freezes)

    console.print()
    console.print(Panel(
        f"[bold blue]🥅 Day Frozen![/bold blue]\n\n"
        f"  Habit: [bold]{habit_name}[/bold]\n"
        f"  Date:  {freeze_date}\n\n"
        f"  [dim]This day won't break your streak.[/dim]\n"
        f'  [dim]Use [bold]streak-forge unfreeze "{habit_name}" {freeze_date}[/bold] to undo.[/dim]',
        title="🔥 StreakForge",
        border_style="blue",
    ))


def cmd_unfreeze(args):
    """Remove a freeze for a habit on a specific date."""
    name = args.name.strip()
    freezes = _load_freezes()

    habit_name = None
    for h in _load()["habits"]:
        if h["name"].lower() == name.lower():
            habit_name = h["name"]
            break

    if habit_name is None:
        console.print(f"[red]✗[/red] Habit '{name}' not found.")
        sys.exit(1)

    freeze_date = _parse_date(args.date) if args.date else _today()

    if habit_name not in freezes or freeze_date not in freezes[habit_name]:
        console.print(f"[yellow]⚠[/yellow] '{habit_name}' is not frozen for {freeze_date}.")
        return

    freezes[habit_name].remove(freeze_date)
    if not freezes[habit_name]:
        del freezes[habit_name]
    _save_freezes(freezes)

    console.print(f"  🧊 Unfroze '{habit_name}' for {freeze_date}.")


def cmd_templates(args):
    """List available habit templates or create a habit from a template."""
    if args.action == "list":
        table = Table(
            title="🔥 StreakForge — Habit Templates",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold magenta",
        )
        table.add_column("ID", style="bold cyan", width=12)
        table.add_column("Emoji", justify="center", width=4)
        table.add_column("Habit Name", min_width=22)
        table.add_column("Target", justify="right", width=7)
        table.add_column("Description", min_width=30)

        for tid, tpl in sorted(HABIT_TEMPLATES.items()):
            table.add_row(
                tid,
                tpl["emoji"],
                tpl["name"],
                f"{tpl['target_days']}d",
                tpl["description"],
            )

        console.print(table)
        console.print(f"\n  [dim]Use [bold]streak-forge template use <id>[/bold] to create a habit from a template.[/dim]")
        console.print(f"  [dim]Use [bold]streak-forge template use <id> --emoji 🎯[/bold] to customize.[/dim]\n")

    elif args.action == "use":
        template_id = args.template_id.lower().strip()
        if template_id not in HABIT_TEMPLATES:
            console.print(f"[red]✗[/red] Unknown template: '{template_id}'.")
            console.print(f"  Available templates: {', '.join(sorted(HABIT_TEMPLATES.keys()))}")
            sys.exit(1)

        tpl = HABIT_TEMPLATES[template_id]
        data = _load()
        name = tpl["name"]

        # Check for duplicates
        for h in data["habits"]:
            if h["name"].lower() == name.lower():
                console.print(f"[yellow]⚠[/yellow] Habit '{name}' already exists!")
                sys.exit(1)

        habit = {
            "name": name,
            "created_at": _today(),
            "target_days": args.target if args.target else tpl["target_days"],
            "emoji": args.emoji if args.emoji else tpl["emoji"],
            "color": args.color or "white",
            "template": template_id,
        }
        data["habits"].append(habit)
        if name not in data["logs"]:
            data["logs"][name] = []
        _save(data)

        console.print()
        console.print(Panel(
            f"[bold green]✨ Habit created from template![/bold green]\n\n"
            f"  {habit['emoji']} [bold]{name}[/bold]\n"
            f"  Target: {habit['target_days']} days\n"
            f"  Created: {_today()}\n\n"
            f"  [dim]{tpl['description']}[/dim]\n\n"
            f'  [dim]Log your first day with:[/dim]\n'
            f'  [bold]  streak-forge log "{name}"[/bold]',
            title="🔥 StreakForge",
            border_style="green",
        ))


def cmd_summary(args):
    """Show weekly and monthly summary reports for all habits or a specific habit."""
    data = _load()
    habits = data["habits"]
    today = date.today()
    freezes = _load_freezes()

    if not habits:
        console.print("[dim]No habits to summarize.[/dim]")
        return

    # Filter to specific habit if requested
    target_habits = habits
    if args.habit:
        target_habits = []
        for h in habits:
            if h["name"].lower() == args.habit.lower():
                target_habits.append(h)
                break
        if not target_habits:
            console.print(f"[red]✗[/red] Habit '{args.habit}' not found.")
            sys.exit(1)

    period = args.period  # weekly or monthly

    for h in target_habits:
        name = h["name"]
        dates = set(data["logs"].get(name, []))
        habit_freezes = set(freezes.get(name, []))

        if period == "weekly":
            # Show last 8 weeks
            weeks_back = 8
            console.print()
            console.print(f"  📊 [bold]Weekly Summary — {name}[/bold]")
            console.print(f"  [dim]Last {weeks_back} weeks (Mon–Sun)[/dim]\n")

            table = Table(box=box.SIMPLE, show_lines=False, padding=(0, 1))
            table.add_column("Week", style="bold", width=14)
            table.add_column("Logs", justify="right", width=6)
            table.add_column("Freezes", justify="right", width=8)
            table.add_column("Completion", min_width=24)
            table.add_column("Status", width=4, justify="center")

            for w in range(weeks_back - 1, -1, -1):
                week_start = today - timedelta(days=today.weekday() + 7 * w)
                week_end = week_start + timedelta(days=6)
                week_label = f"{week_start.strftime('%b %d')}–{week_end.strftime('%b %d')}"
                if w == 0:
                    week_label += " (this)"
                elif w == 1:
                    week_label += " (last)"

                week_dates = set()
                for i in range(7):
                    d = (week_start + timedelta(days=i)).isoformat()
                    week_dates.add(d)

                logged = len(dates & week_dates)
                frozen = len(habit_freezes & week_dates)
                active = logged + frozen
                pct = min(active / 7, 1.0)
                bar_width = 16
                filled = int(pct * bar_width)
                bar = "█" * filled + "░" * (bar_width - filled)
                status = "✅" if active >= 7 else "🔥" if active >= 4 else "🌱" if active > 0 else "💤"

                table.add_row(
                    week_label,
                    str(logged),
                    str(frozen),
                    f"{bar} {active}/7",
                    status,
                )

            console.print(table)

        elif period == "monthly":
            # Show last 6 months
            months_back = 6
            console.print()
            console.print(f"  📊 [bold]Monthly Summary — {name}[/bold]")
            console.print(f"  [dim]Last {months_back} months[/dim]\n")

            table = Table(box=box.SIMPLE, show_lines=False, padding=(0, 1))
            table.add_column("Month", style="bold", width=14)
            table.add_column("Logs", justify="right", width=6)
            table.add_column("Freezes", justify="right", width=8)
            table.add_column("Completion", min_width=26)
            table.add_column("Status", width=4, justify="center")

            for m in range(months_back - 1, -1, -1):
                # Calculate target month
                month_num = today.month - m
                year_num = today.year
                while month_num <= 0:
                    month_num += 12
                    year_num -= 1

                days_in_month = calendar.monthrange(year_num, month_num)[1]
                month_start = date(year_num, month_num, 1)
                month_end = date(year_num, month_num, days_in_month)
                month_label = month_start.strftime("%b %Y")
                if m == 0:
                    month_label += " (cur)"
                elif m == 1:
                    month_label += " (last)"

                month_dates = set()
                for i in range(days_in_month):
                    d = (month_start + timedelta(days=i)).isoformat()
                    month_dates.add(d)

                logged = len(dates & month_dates)
                frozen = len(habit_freezes & month_dates)
                active = logged + frozen
                pct_min = min(active / days_in_month, 1.0)
                bar_width = 16
                filled = int(pct_min * bar_width)
                bar = "█" * filled + "░" * (bar_width - filled)
                status = "✅" if active >= days_in_month * 0.9 else "🔥" if active >= days_in_month * 0.5 else "🌱" if active > 0 else "💤"

                table.add_row(
                    month_label,
                    str(logged),
                    str(frozen),
                    f"{bar} {active}/{days_in_month}",
                    status,
                )

            console.print(table)

        # Yearly overview streak (total active days this year)
        year_start = date(today.year, 1, 1)
        year_dates = set()
        d = year_start
        while d <= today:
            year_dates.add(d.isoformat())
            d += timedelta(days=1)
        year_logged = len(dates & year_dates)
        year_freezes = len(habit_freezes & year_dates)
        total_days = (today - year_start).days + 1
        year_pct = (year_logged + year_freezes) / total_days * 100 if total_days > 0 else 0
        console.print(f"\n  📈 Year {today.year}: {year_logged} logged + {year_freezes} frozen = "
                       f"{year_logged + year_freezes}/{total_days} days ({year_pct:.0f}%)")
        console.print()


def cmd_export(args):
    """Export all data to JSON or CSV."""
    data = _load()
    fmt = args.format.lower()

    if fmt == "json":
        output = json.dumps(data, indent=2, default=str)
        console.print(output)
    elif fmt == "csv":
        console.print("habit,date")
        for h in data["habits"]:
            name = h["name"]
            for d in sorted(data["logs"].get(name, [])):
                console.print(f"{name},{d}")
    else:
        console.print(f"[red]Unknown format: {fmt}. Use 'json' or 'csv'.[/red]")
        sys.exit(1)


def cmd_import(args):
    """Import habits from a JSON file."""
    filepath = Path(args.filepath)
    if not filepath.exists():
        console.print(f"[red]File not found: {filepath}[/red]")
        sys.exit(1)

    with open(filepath) as f:
        import_data = json.load(f)

    data = _load()
    imported = 0
    for h in import_data.get("habits", []):
        name = h["name"]
        exists = any(existing["name"].lower() == name.lower() for existing in data["habits"])
        if not exists:
            data["habits"].append(h)
            if name not in data["logs"]:
                data["logs"][name] = []
            imported += 1

    for habit_name, dates in import_data.get("logs", {}).items():
        if habit_name in data["logs"]:
            existing = set(data["logs"][habit_name])
            existing.update(dates)
            data["logs"][habit_name] = sorted(existing)
        else:
            data["logs"][habit_name] = sorted(dates)

    _save(data)
    console.print(f"  📥 Imported {imported} habit(s) with their logs.")


# ── CLI Setup ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="streak-forge",
        description="🔥 StreakForge — Build unbreakable habits with beautiful terminal tracking.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"StreakForge {__version__}")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # start
    p_start = sub.add_parser("start", help="Create a new habit to track")
    p_start.add_argument("name", help="Name of the habit")
    p_start.add_argument("--target", type=int, default=30, help="Target days (default: 30)")
    p_start.add_argument("--emoji", default="⭐", help="Emoji for the habit (default: ⭐)")
    p_start.add_argument("--color", default="white", help="Color for display")

    # log
    p_log = sub.add_parser("log", help="Log activity for a habit")
    p_log.add_argument("name", help="Habit name")
    p_log.add_argument("--date", help="Date to log (YYYY-MM-DD, default: today)")

    # list
    sub.add_parser("list", help="List all habits with streaks")

    # show
    p_show = sub.add_parser("show", help="Show detailed info for a habit")
    p_show.add_argument("name", help="Habit name")

    # calendar
    p_cal = sub.add_parser("calendar", help="Show contribution calendar for a habit")
    p_cal.add_argument("name", help="Habit name")

    # stats
    sub.add_parser("stats", help="Show global statistics")

    # rename
    p_rename = sub.add_parser("rename", help="Rename a habit")
    p_rename.add_argument("old_name", help="Current name")
    p_rename.add_argument("new_name", help="New name")

    # delete
    p_del = sub.add_parser("delete", help="Delete a habit")
    p_del.add_argument("name", help="Habit name")
    p_del.add_argument("--force", action="store_true", help="Confirm deletion")

    # freeze
    p_freeze = sub.add_parser("freeze", help="Freeze a habit for a date (planned rest day)")
    p_freeze.add_argument("name", help="Habit name")
    p_freeze.add_argument("--date", help="Date to freeze (YYYY-MM-DD, default: today)")

    # unfreeze
    p_unfreeze = sub.add_parser("unfreeze", help="Unfreeze a habit for a date")
    p_unfreeze.add_argument("name", help="Habit name")
    p_unfreeze.add_argument("--date", help="Date to unfreeze (YYYY-MM-DD, default: today)")

    # template
    p_tpl = sub.add_parser("template", help="Habit templates — list or use")
    tpl_sub = p_tpl.add_subparsers(dest="action", help="Template action")
    tpl_list = tpl_sub.add_parser("list", help="List available templates")
    tpl_use = tpl_sub.add_parser("use", help="Create a habit from a template")
    tpl_use.add_argument("template_id", help="Template ID (e.g., water, read, code)")
    tpl_use.add_argument("--emoji", help="Override emoji")
    tpl_use.add_argument("--target", type=int, help="Override target days")
    tpl_use.add_argument("--color", default="white", help="Color for display")

    # summary
    p_summary = sub.add_parser("summary", help="Show weekly or monthly summary reports")
    p_summary.add_argument("--period", choices=["weekly", "monthly"], default="weekly",
                            help="Summary period (default: weekly)")
    p_summary.add_argument("--habit", help="Filter to a specific habit (default: all)")

    # export
    p_export = sub.add_parser("export", help="Export data (JSON or CSV)")
    p_export.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")

    # import
    p_import = sub.add_parser("import", help="Import habits from JSON file")
    p_import.add_argument("filepath", help="Path to JSON file")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "start": cmd_start,
        "log": cmd_log,
        "list": cmd_list,
        "show": cmd_show,
        "calendar": cmd_calendar,
        "stats": cmd_stats,
        "rename": cmd_rename,
        "delete": cmd_delete,
        "freeze": cmd_freeze,
        "unfreeze": cmd_unfreeze,
        "template": cmd_templates,
        "summary": cmd_summary,
        "export": cmd_export,
        "import": cmd_import,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
