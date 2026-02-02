# 🏆 Gold Price Predictive AI

> **Institutional-Grade AI/ML Predictive Analytics for Gold Market Analysis**

A sophisticated real-time gold price prediction system powered by machine learning, technical analysis, and multi-factor sentiment analysis. Built with Python, Flask, and advanced financial modeling techniques.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### 🎯 Institutional-Grade Scoring System
- **EMA Crossover Detection** (9/21 periods) - 50 points
- **RSI Alignment Analysis** (14 periods) - 20 points
- **News Sentiment Integration** - 15 points
- **DXY Correlation Tracking** - 15 points
- **Confidence Threshold**: Alerts triggered at 75-80% confidence

### 📊 Advanced Technical Analysis
- Weighted Linear Regression with recent data emphasis
- Exponential Moving Averages (9 & 21 periods)
- RSI divergence detection
- Multi-timeframe backtesting (6-hour historical accuracy)

### 🌏 Asian Market Intelligence
- PBOC (People's Bank of China) gold reserve monitoring
- Lunar New Year demand cycle analysis
- Real-time sentiment from Reuters, CNBC, Bloomberg

### 📈 Real-Time Dashboard
- Modern dark blue/purple UI with glassmorphism
- Live status indicator with pulsing animation
- Interactive Chart.js visualizations
- Confidence score breakdown
- Thai language executive insights

### 📧 Automated Reporting
- Hourly executive briefings (Thai language)
- Email notifications for high-confidence signals
- Detailed market sentiment summaries

---

## � Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager
- (Optional) Email account for notifications

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gold-price-predictive-ai.git
cd gold-price-predictive-ai
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment (Optional)**
```bash
cp .env.example .env
# Edit .env with your email credentials for notifications
```

5. **Run the application**
```bash
python app.py
```

6. **Access the dashboard**
Open your browser to: `http://localhost:5001`

---

## 📖 How It Works

### Confidence Scoring Algorithm

The system uses a **100-point weighted scoring system**:

```
Total Score = Trend (50) + RSI (20) + Sentiment (15) + DXY (15)
```

#### 1. Trend Analysis (50 points)
- Detects 9 EMA crossing 21 EMA within last 3 bars
- Awards full points only on fresh crossovers
- Identifies BULLISH or BEARISH market structure

#### 2. RSI Alignment (20 points)
- Checks for price/RSI divergence
- Confirms momentum alignment with trend
- Validates strength of directional move

#### 3. News Sentiment (15 points)
- Analyzes top financial news headlines
- Categorizes as Supportive/Neutral/Opposite
- **HARD STOP**: Score = 0 if sentiment contradicts trend

#### 4. DXY Correlation (15 points)
- Monitors US Dollar Index inverse relationship
- Gold typically rises when DXY falls
- Confirms macro environment alignment

### Alert Thresholds

| Score Range | Action | Description |
|------------|--------|-------------|
| 75-80% | 🔔 **TRADE SIGNAL** | Optimal risk/reward setup |
| 81-100% | ⚠️ High Confidence | Strong alignment, monitor |
| 60-74% | 📊 Medium | Watch for development |
| 0-59% | ⏸️ Low | Wait for clarity |

---

## 🎨 Dashboard Preview

The dashboard features a modern, executive-grade interface with:
- **Live Status Indicator**: Pulsing green dot shows system is active
- **Confidence Gauge**: Real-time score with color-coded alerts
- **Market Sentiment**: Latest news with impact analysis
- **Price Chart**: 6-hour historical + 1-hour forecast
- **Asian Market Insights**: PBOC and seasonal demand tracking

---

## � Project Structure

```
gold-price-predictive-ai/
├── app.py                  # Flask application & scheduler
├── gold_agent.py          # Core ML/AI logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── templates/
│   └── dashboard.html    # Frontend UI
├── static/
│   ├── style.css        # Modern dark blue/purple theme
│   └── script.js        # Real-time data updates
└── README.md            # This file
```

---

## 🔧 Configuration

### Email Notifications (Optional)

To enable hourly executive briefings:

1. Create a `.env` file from the template
2. Add your email credentials:
```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)

---

## 🧪 Technical Stack

- **Backend**: Python 3.9+, Flask
- **ML/Data**: scikit-learn, pandas, yfinance
- **Scraping**: BeautifulSoup4, requests
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Visualization**: Chart.js
- **Scheduling**: APScheduler

---

## 📊 Data Sources

- **Price Data**: Yahoo Finance (GC=F - Gold Futures)
- **Dollar Index**: DXY (US Dollar Index)
- **News**: CNBC Markets RSS Feed
- **Asian Markets**: World Gold Council, PBOC reports

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/latest` | GET | Latest prediction data (JSON) |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

**This software is for educational and demonstration purposes only.**

- Not financial advice
- Past performance does not guarantee future results
- Always do your own research before trading
- Use at your own risk

---

## 👨‍💻 Author

**Wittawat Lohamas**

AI/ML Predictive Analytics Demo

---

## 🙏 Acknowledgments

- Yahoo Finance for market data API
- CNBC for news feeds
- Chart.js for visualization library
- The open-source community

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**⭐ If you find this project useful, please consider giving it a star!**
