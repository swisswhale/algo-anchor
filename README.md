# 📈 AlgoAnchor
### Trading Strategy Backtesting Platform
![Built With](https://img.shields.io/badge/built%20with-Django-blue)
![Status](https://img.shields.io/badge/status-production--ready-green)
![Python Version](https://img.shields.io/badge/python-3.13+-green)
![Deployment](https://img.shields.io/badge/deploy-Replit-orange)

A comprehensive Django-based web application for creating, backtesting, and analyzing trading strategies. Features a complete dashboard for strategy management, detailed performance analytics, and automated backtesting with real-world financial data integration.

---

## 🚀 Features

- 🔐 **Complete User Management**: Registration, authentication, profile management
- 📊 **Interactive Dashboard**: Strategy overview with performance metrics and management tools
- 🎯 **Strategy Builder**: Create custom strategies with configurable parameters:
  - Lookback periods (20-200 days)
  - Entry thresholds (Z-score based)
  - Exit rules (profit target, stop loss, time-based)
  - Multi-ticker support
- 📈 **Advanced Backtesting Engine**: 
  - Comprehensive performance metrics (Sharpe ratio, max drawdown, win rate)
  - Risk analytics (VaR, Alpha, Beta, volatility)
  - Trade-by-trade analysis
- 📋 **Detailed Results**: Performance charts, trade logs, and comparative analysis
- 🔄 **Real-time Data**: Yahoo Finance integration for live market data
- � **Responsive Design**: Bootstrap-powered UI with mobile support
- 🚀 **Cloud Ready**: Configured for Replit deployment

---

## 🛠 Tech Stack

| Layer         | Technologies                          |
|---------------|---------------------------------------|
| **Backend**   | Django 5.2, Python 3.13, SQLite     |
| **Frontend**  | Django Templates, Bootstrap 5, Font Awesome |
| **Data**      | Pandas, NumPy, yfinance              |
| **Analytics** | Custom backtesting engine            |
| **Auth**      | Django built-in authentication       |
| **Deployment**| Replit, with local development support |

---

## 📂 Project Structure
```
algo-anchor/
├── core/                          # Main Django application
│   ├── models.py                  # Database models (Strategy, BacktestResult, Security, etc.)
│   ├── forms.py                   # Django forms for strategy creation/editing
│   ├── admin.py                   # Django admin configuration
│   ├── urls.py                    # App URL routing
│   ├── views/                     # Organized view modules
│   │   ├── dashboard_views.py     # Dashboard and home views
│   │   ├── strategy_views.py      # Strategy CRUD operations
│   │   ├── backtest_views.py      # Backtest results and analysis
│   │   ├── auth_views.py          # User authentication
│   │   └── profile_views.py       # User profile management
│   ├── services/                  # Business logic services
│   │   ├── backtest_engine.py     # Core backtesting algorithms
│   │   ├── data_loader.py         # Data processing utilities
│   │   └── yahoo_fetcher.py       # Yahoo Finance API integration
│   ├── management/commands/       # Django management commands
│   │   └── run_backtests.py       # Batch backtest execution
│   ├── templatetags/              # Custom template filters
│   │   └── math_filters.py        # Mathematical operations for templates
│   ├── templates/                 # HTML templates
│   │   ├── base.html              # Base template with Bootstrap
│   │   ├── dashboard.html         # Main dashboard
│   │   ├── home.html              # Landing page
│   │   ├── strategies/            # Strategy-related templates
│   │   │   ├── create.html        # Strategy creation form
│   │   │   ├── detail.html        # Strategy details view
│   │   │   ├── edit.html          # Strategy editing form
│   │   │   └── delete.html        # Delete confirmation
│   │   ├── backtests/             # Backtest result templates
│   │   │   └── detail.html        # Detailed backtest results
│   │   ├── registration/          # Authentication templates
│   │   │   ├── login.html         # Login form
│   │   │   ├── logout.html        # Logout confirmation
│   │   │   └── register.html      # User registration
│   │   └── profile/               # User profile templates
│   │       └── edit.html          # Profile editing
│   └── static/                    # Static assets
│       ├── css/                   # Custom stylesheets
│       ├── js/                    # JavaScript files
│       └── images/                # Image assets
├── algoanchor_app/                # Django project settings
│   ├── settings.py                # Main configuration
│   ├── urls.py                    # Root URL configuration
│   ├── wsgi.py                    # WSGI configuration
│   └── asgi.py                    # ASGI configuration
├── dataset/                       # Sample data files
│   └── spy.csv                    # Sample market data
├── depcode/                       # Development/deprecated files
├── db.sqlite3                     # SQLite database
├── main.py                        # Replit deployment entry point
├── requirements.txt               # Python dependencies
├── replit.nix                     # Replit configuration
├── .replit                        # Replit deployment settings
├── .gitignore                     # Git ignore rules
└── manage.py                      # Django management script
```
---

## 📦 Installation & Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/algo-anchor.git
cd algo-anchor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Load sample securities data
python manage.py shell -c "
from core.models import Security
# Add sample securities if needed
Security.objects.get_or_create(symbol='AAPL', defaults={'name': 'Apple Inc.'})
Security.objects.get_or_create(symbol='GOOGL', defaults={'name': 'Alphabet Inc.'})
Security.objects.get_or_create(symbol='MSFT', defaults={'name': 'Microsoft Corp.'})
"

# Create superuser (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

### Replit Deployment

1. Fork this repository to your GitHub account
2. Import the repository into Replit
3. Replit will automatically:
   - Install dependencies from `requirements.txt`
   - Run database migrations
   - Start the Django server on `0.0.0.0:8000`

The application includes configuration for Replit deployment with proper `ALLOWED_HOSTS` settings.

### Running Backtests

```bash
# Run backtests for all strategies
python manage.py run_backtests

# Run backtest for specific strategy
python manage.py run_backtests --strategy-id 1

# Force re-run existing backtests
python manage.py run_backtests --force
```
---

## 🎯 Usage

### Creating a Strategy
1. Register/login to your account
2. Navigate to the dashboard
3. Click "New Strategy"
4. Configure strategy parameters:
   - **Name**: Descriptive strategy name
   - **Lookback Days**: Historical period for analysis (20-200 days)
   - **Entry Threshold**: Z-score threshold for trade signals
   - **Exit Rule**: Profit target, stop loss, or time-based exits
   - **Tickers**: Select securities to trade

### Analyzing Results
- **Dashboard Overview**: Quick performance summary of all strategies
- **Detailed Results**: Click "Results" to view comprehensive backtest analysis
- **Performance Metrics**: Returns, Sharpe ratio, max drawdown, win rate
- **Risk Analytics**: Volatility, VaR, Alpha, Beta
- **Trade History**: Complete trade-by-trade breakdown

### Key Performance Metrics
- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Alpha/Beta**: Performance vs. market benchmark

---

## 🔧 Key Features in Detail

### Backtesting Engine
- **Signal Generation**: Z-score based mean reversion signals
- **Position Management**: Automated entry/exit based on defined rules
- **Risk Management**: Stop-loss and profit-taking mechanisms
- **Performance Calculation**: Comprehensive metrics and analytics

### Data Integration
- **Yahoo Finance API**: Real-time market data fetching
- **Historical Data**: Extensive backtesting periods
- **Multiple Securities**: Support for stocks, ETFs, and indices
- **Data Validation**: Robust error handling and data quality checks

### User Interface
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Interactive Dashboard**: Real-time strategy monitoring
- **Intuitive Forms**: Easy strategy creation and editing
- **Visual Feedback**: Clear performance indicators and status updates

---

## 📌 Current Status

### ✅ Completed Features
- ✅ Complete user authentication system
- ✅ Strategy CRUD operations with validation
- ✅ Advanced backtesting engine with 15+ metrics
- ✅ Interactive dashboard with performance overview
- ✅ Detailed backtest results and analysis
- ✅ Yahoo Finance data integration
- ✅ Responsive UI with Bootstrap 5
- ✅ Cloud deployment ready (Replit)
- ✅ Multi-ticker strategy support
- ✅ Trade logging and analysis
- ✅ Risk management and analytics

### 🔄 In Progress
- Performance charting and visualizations
- Strategy comparison tools
- Advanced filtering and search
- Export functionality for results

### 🎯 Future Enhancements
- Additional strategy types (momentum, arbitrage)
- Real-time paper trading
- Portfolio optimization
- Machine learning integration
- Advanced charting with Plotly

---

## 👤 Author & Contributing

**Developed by J. Paul**

Contributions welcome! Please feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests
- Improve documentation

For questions or collaboration, reach out via GitHub issues.

---

## 📄 License

This project is available under the MIT License. See LICENSE file for details.