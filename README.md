# 📈 AlgoAnchor
### Mean Reversion App
![Built With](https://img.shields.io/badge/built%20with-Django-blue)
![Status](https://img.shields.io/badge/status-in--development-yellow)
![Python Version](https://img.shields.io/badge/python-3.10+-green)

A Django-based web app for backtesting mean reversion trading strategies using historical price data. Users can create strategies, view backtest results, and analyze trades — with full CRUD functionality and optional live data via Yahoo Finance.

---

## 🚀 Features

- 🔐 Full user authentication (register, login, logout, profile management)
- 🧠 Strategy builder (lookback period, z-score threshold, exit rules)
- 🗂️ Preloaded CSV or live Yahoo Finance integration (`yfinance`)
- 📉 Mean reversion logic with signal generation
- 📊 Trade logs, backtest summaries, and performance metrics
- 📈 Optional visualizations with Plotly and Matplotlib
- 🔧 Built with modular Django architecture for easy extensibility

---

## 🛠 Tech Stack

| Layer         | Tools Used                           |
|---------------|---------------------------------------|
| **Backend**   | Django, PostgreSQL                    |
| **Frontend**  | Django Templates, Bootstrap (basic)   |
| **Data Tools**| Pandas, NumPy, yfinance               |
| **Visualization** | Matplotlib, Plotly               |
| **Auth**      | Django built-in auth (with AllAuth optional) |
| **Config**    | python-decouple for env vars          |

---

## 📂 Project Structure
```
meanreversion_app/
├── core/                          # Main Django app
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py                  # All DB models (UserProfile, Strategy, etc.)
│   ├── signals.py                 # Auto-create UserProfile
│   ├── tests.py
│   ├── urls.py                    # App-specific URL routes
│   ├── views/
│   │   ├── init.py
│   │   ├── auth_views.py
│   │   ├── dashboard_views.py
│   │   ├── strategy_views.py
│   │   └── profile_views.py
│   ├── services/
│   │   ├── init.py
│   │   ├── data_loader.py         # Load from CSV
│   │   └── yahoo_fetcher.py       # Pull from Yahoo Finance
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── profile/
│   │   │   └── edit_profile.html
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   ├── logout.html
│   │   │   └── register.html
│   │   └── strategy/
│   │       ├── strategy_list.html
│   │       ├── strategy_create.html
│   │       └── strategy_detail.html
│   └── static/
│       ├── css/
│       └── js/
├── dataset/                       # Local test datasets
│   └── spy.csv
├── scripts/                       # Utility scripts
│   └── load_data.py
├── meanreversion_app/             # Project settings
│   ├── init.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py                    # Global URL routing
│   └── wsgi.py
├── db.sqlite3                     # Local dev DB (or connect PostgreSQL)
├── requirements.txt
├── README.md
└── manage.py
```
---

## 📦 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/meanreversion-app.git
cd meanreversion-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL (or use sqlite3 for testing)
# Edit .env or settings.py as needed

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run the server
python manage.py runserver

# dataset/spy.csv
Date,Close
2023-01-01,392.45
2023-01-02,395.30
...
```
---
## 📌 Status
### ✅ MVP Goals
- User auth & profile setup
- Strategy CRUD
- Backtest engine with CSV support
- Chart visualizations
- Yahoo Finance integration (toggle on/off
- UI polish & responsive layout
---
## 👤 Author
Developed by J. Paul — feel free to reach out or contribute!