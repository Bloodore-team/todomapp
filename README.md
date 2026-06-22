# Bloodore-team/todom

A modern Notion-inspired todo app built with Flask, SQLite, Tailwind CSS and vanilla JavaScript.

Features:
- Add / edit / delete tasks
- Change status (todo, en_cours, done)
- Favorite tasks
- Projects and sub-projects
- Dashboard with statistics + Chart.js activity chart
- Dark mode
- Sidebar navigation (Home, Inbox, Favoris, Settings)
- Notifications (browser)
- Simple calendar view
- REST API (Flask)

Quickstart

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # mac/linux
.\.venv\Scripts\activate   # windows
pip install -r requirements.txt
```

2. Initialize the database:

```bash
python init_db.py
```

3. Run the app:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

Open http://127.0.0.1:5000

Notes

- This project is intentionally simple but structured to be extended into a SaaS product.
- See comments in code for how to extend with OAuth/Google Calendar, or production deployment.
