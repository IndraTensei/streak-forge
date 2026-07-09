# 🔥 StreakForge

> Build unbreakable habits with beautiful terminal streak tracking.

StreakForge is a CLI tool that helps you track daily habits, creative streaks, and personal challenges — all from your terminal. Visualize your progress with fire charts, milestone celebrations, GitHub-style calendars, and insightful stats.

Whether you're writing every day, exercising, learning a language, or building a side project, StreakForge keeps you motivated with beautiful visuals and encouraging milestone messages.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-cross--platform-lightgrey)

## Features

- Habit Tracking - Create named habits with custom emojis and day targets
- Streak Visualization - Fire emoji indicators that grow with your streak
- Contribution Calendar - GitHub-style calendar showing your activity over the last 52 weeks
- Milestone Celebrations - Special messages at 1, 3, 7, 14, 21, 30, 50, 66, 100, and 365 days
- Global Stats - See your best streaks, total logs, and overall progress
- Export & Import - Export to JSON/CSV, import from JSON files
- Beautiful Terminal UI - Rich tables, panels, and progress bars
- Local Storage - All data stored locally in `~/.streak-forge/habits.json`
- Fully CLI - No dependencies on external services, works offline
- Streak Freeze - Mark planned rest days without breaking your streak
- Habit Templates - 10 pre-built habit templates for common goals
- Summary Reports - Weekly and monthly completion reports with progress bars
- Habit Categories - Organize habits into custom categories
- Log Notes - Add optional notes to log entries to track details
- Category View - List all habits organized by category

## 🚀 Installation

### From Source

```bash
git clone https://github.com/IndraTensei/streak-forge.git
cd streak-forge
pip install -r requirements.txt
pip install -e .
```

### Quick Run (No Install)

```bash
git clone https://github.com/IndraTensei/streak-forge.git
cd streak-forge
pip install rich
python streak_forge.py start "My Habit"
```

### Requirements

- Python 3.8+
- [rich](https://github.com/Textualize/rich) library

## 📖 Usage

### Create a New Habit

```bash
streak-forge start "Morning Run"
streak-forge start "Write 500 Words" --target 66 --emoji ✍️
streak-forge start "Meditate" --target 30 --emoji 🧘
```

### Log Your Progress

```bash
# Log today
streak-forge log "Morning Run"

# Log a specific date
streak-forge log "Morning Run" --date 2026-06-01
```

### View Your Habits

```bash
# List all habits with streaks
streak-forge list

# Detailed view of one habit
streak-forge show "Morning Run"

# GitHub-style calendar
streak-forge calendar "Morning Run"
```

### Check Stats

```bash
# Global statistics across all habits
streak-forge stats
```

### Manage Habits

```bash
# Rename a habit
streak-forge rename "Morning Run" "Daily Run"

# Delete a habit (requires --force)
streak-forge delete "Morning Run" --force
```

### Export & Import

```bash
# Export to JSON
streak-forge export --format json > my-habits.json

# Export to CSV
streak-forge export --format csv > my-habits.csv

# Import from JSON
streak-forge import my-habits.json
```

### Streak Freeze (Rest Days)

```bash
# Freeze today (planned rest day — won't break your streak)
streak-forge freeze "Morning Run"

# Freeze a specific date
streak-forge freeze "Morning Run" --date 2026-06-20

# Unfreeze if you change your mind
streak-forge unfreeze "Morning Run" --date 2026-06-20
```

### Habit Templates

```bash
# List available templates
streak-forge template list

# Create a habit from a template
streak-forge template use water
streak-forge template use code --target 365
streak-forge template use meditate --emoji 🌸
```

Available templates: `water`, `read`, `exercise`, `meditate`, `journal`, `code`, `walk`, `sleep`, `gratitude`, `stretch`

### Summary Reports

```bash
# Weekly summary for all habits
streak-forge summary --period weekly

# Monthly summary for a specific habit
streak-forge summary --period monthly --habit "Morning Run"
```

### Habit Categories

```bash
# Create a habit with a category
streak-forge start "Morning Run" --category health

# Create a habit from a template with a category
streak-forge template use exercise --category fitness

# List all habits organized by category
streak-forge categories
```

### Log Notes

```bash
# Log with an optional note
streak-forge log "Morning Run" --note "Ran 5km in 25 minutes"

# View notes in habit details
streak-forge show "Morning Run"
```

## 🎮 Example Session

```bash
$ streak-forge start "Morning Run" --target 30 --emoji 🏃

  ✨ New habit created!

  🏃 Morning Run
  Target: 30 days
  Created: 2026-06-02

  Log your first day with:
    streak-forge log "Morning Run"

$ streak-forge log "Morning Run"

  🌱 Logged! 'Morning Run' for 2026-06-02
  Current streak: 1 day

  🎉 First step! Every journey begins with a single day!

$ streak-forge list

  🔥 StreakForge — Your Habits
  ┌──────┬──────────────┬─────────┬─────────┬───────┬──────────────────────────────┬────────┐
  │ 🏃   │ Morning Run  │    1    │    1    │   1   │ █░░░░░░░░░░░░░░░░░░░  3%    │  🌱    │
  └──────┴──────────────┴─────────┴─────────┴───────┴──────────────────────────────┴────────┘

$ streak-forge calendar "Morning Run"

  📅 StreakForge Calendar — Morning Run
  Last 52 weeks

  Mon 🟢⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
  Wed ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛
  Fri ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛

  ⬛ No activity  🟢 Logged  ⬜ Future
```

## 🏗️ Project Structure

```
streak-forge/
├── streak_forge.py      # Main CLI application
├── setup.py             # Package setup
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── LICENSE              # MIT License
└── .gitignore           # Git ignore rules
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests if applicable
4. Commit: `git commit -m "Add amazing feature"`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Ideas for Contributions

- [x] Weekly/monthly summary reports
- [x] Habit templates (common habits with preset targets)
- [x] Streak freeze/skip days (for planned rest days)
- [x] Habit categories and tags
- [x] Log notes/comments for entries
- [ ] Reminder notifications
- [ ] ASCII art streak visualizations
- [ ] Integration with cron for daily reminders
- [ ] Habit chaining (link habits together)

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Inspired by GitHub's contribution graph and the power of showing up every day
- Remember: *"You don't have to be extreme, just consistent."*
