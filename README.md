# Market Intelligence & Decision Engine

A probabilistic decision support system that models market behavior under uncertainty, quantifies risk, and structures trade decisions with discipline. This is not a "stock prediction bot" — it's a quantitative research desk that never sleeps, never gets emotional, and always shows its reasoning.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKET DATA LAYER                        │
│  NSE/BSE Bhavcopy → Corporate Actions → Index Data          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               DATA INGESTION ENGINE                         │
│  Fetch, validate, clean, adjust for corporate actions       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            TIME-SERIES DATABASE (TimescaleDB)               │
│  OHLCV bars, derived features, trade logs                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              MARKET STRUCTURE ENGINE                        │
│  Regime classification, volatility analysis, breadth        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│           FEATURE ENGINEERING & TECHNICAL ANALYSIS          │
│  Multi-timeframe indicators, pattern recognition            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              ML PREDICTION ENGINE                           │
│  Probability distributions, confidence estimation           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            RISK MANAGEMENT ENGINE                           │
│  Trade structuring, position sizing, quality filters        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              TRADING TERMINAL UI                            │
│  Dashboard, opportunity analysis, position monitoring       │
└─────────────────────────────────────────────────────────────┘
```

## Core Philosophy

- **Probabilistic, not deterministic**: Outputs probability distributions, not price targets
- **Risk first**: Never risk >2% per trade, minimum 1:2 risk-reward ratio
- **Quality over quantity**: Rejects 80-90% of candidates
- **Regime-aware**: Adapts to market conditions (trending vs ranging, volatility levels)
- **Transparent reasoning**: Every prediction shows contributing factors

## Tech Stack

### Backend
- **FastAPI**: Async Python web framework
- **PostgreSQL + TimescaleDB**: Time-series optimized database
- **SQLAlchemy**: Async ORM with type hints
- **Pandas/NumPy**: Data processing
- **scikit-learn/LightGBM**: ML models

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **TailwindCSS**: Styling
- **TanStack Query**: Data fetching
- **Recharts**: Visualization

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for TimescaleDB)

### Database Setup

```bash
# Start TimescaleDB
docker-compose up -d db

# Wait for database to be ready
docker-compose logs -f db
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env.example .env

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
market-intelligence-engine/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   ├── config/           # Settings and configuration
│   │   ├── db/               # Database connection
│   │   ├── engines/          # Core processing engines
│   │   │   ├── data_ingestion/
│   │   │   ├── market_structure/
│   │   │   ├── technical_analysis/
│   │   │   ├── ml_prediction/
│   │   │   ├── risk_management/
│   │   │   └── ...
│   │   ├── models/           # SQLAlchemy models
│   │   └── main.py           # FastAPI application
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Market
- `GET /api/market/regime` - Current market regime
- `GET /api/market/sectors` - Sector rotation analysis

### Opportunities
- `GET /api/opportunities/` - Today's trade opportunities
- `GET /api/opportunities/{symbol}` - Detailed analysis
- `POST /api/opportunities/{symbol}/approve` - Approve for execution

### Trades
- `POST /api/trades/entry` - Log trade entry
- `POST /api/trades/exit` - Log trade exit
- `GET /api/trades/` - Trade history

### Portfolio
- `GET /api/portfolio/` - Portfolio summary
- `GET /api/portfolio/positions` - Open positions

### Performance
- `GET /api/performance/summary` - Performance metrics
- `GET /api/performance/discipline` - Behavioral analysis

## Disclaimer

This system is a decision support tool for educational and personal use only. It does not constitute financial advice. Trading involves risk of loss. Past performance does not guarantee future results. Always consult a registered financial advisor before making investment decisions.

## License

MIT
