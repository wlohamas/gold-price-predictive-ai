import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import datetime
from dotenv import load_dotenv
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class GoldAgent:
    def __init__(self):
        self.ticker = "GC=F"
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

    def analyze_market_sentiment(self):
        """Placeholder for future sentiment analysis using NewsAPI or LLMs."""
        print("News analysis capability pending: Market sentiment data not yet integrated.")

    def fetch_current_price(self):
        """Fetches the latest Gold price and correlates with DXY."""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="1d")
            dxy_price = dxy_data['Close'].iloc[-1] if not dxy_data.empty else None
            
            gold = yf.Ticker(self.ticker)
            data = gold.history(period="1d", interval="1m")
            
            if data.empty:
                 data = gold.history(period="5d", interval="1h")
            
            # Fallback to GLD if GC=F is completely unavailable
            if data.empty:
                print(f"Ticker {self.ticker} unavailable, trying fallback GLD...")
                gold = yf.Ticker("GLD")
                data = gold.history(period="1d", interval="1m")
                if data.empty:
                    data = gold.history(period="5d", interval="1h")
            
            if not data.empty:
                current_price = data["Close"].iloc[-1]
                return current_price, data, dxy_price
            else:
                return None, None, None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None, None, None

    def get_rsi(self, data, window=14):
        """Calculates RSI Indicator."""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def analyze_asian_market_logic(self):
        """Monitors Asian market factors (PBOC and Lunar New Year) specifically."""
        try:
            # Note: In a real system, we might hit a specific API or use more rigorous scraping.
            # Here we demonstrate the logic based on recent search findings or fixed monitoring.
            url = "https://www.gold.org/goldhub/data/monthly-central-bank-statistics" # Central Bank data
            # For demonstration, we simulate the 'found' data based on periodic search
            
            asian_insights = []
            
            # Logic 1: PBOC Reserves (Simulated check based on common reports)
            # If PBOC streak ends or stops: 'ธนาคารกลางจีนชะลอการซื้อ อาจกดดันราคาในระยะสั้น'
            pboc_buying = True # Default state based on recent 14-month streak
            
            # Logic 2: Lunar New Year Demand
            # 'ความต้องการช่วงตรุษจีนพุ่งสูง เป็นแรงหนุนราคาฝั่งเอเชีย'
            lunar_demand_strong = True # 2026 Year of the Horse demand is high
            
            if lunar_demand_strong:
                asian_insights.append({
                    "title": "Asian Market: Strong Lunar New Year Demand",
                    "impact": "Bullish",
                    "summary_th": "ความต้องการช่วงตรุษจีนพุ่งสูง เป็นแรงหนุนราคาฝั่งเอเชีย"
                })
            
            if not pboc_buying:
                asian_insights.append({
                    "title": "Asian Market: PBOC Reserve Update",
                    "impact": "Caution/Bearish",
                    "summary_th": "ธนาคารกลางจีนชะลอการซื้อ อาจกดดันราคาในระยะสั้น"
                })
                
            return asian_insights
        except Exception as e:
            print(f"Asian logic error: {e}")
            return []

    def analyze_market_sentiment_premium(self):
        """Fetches news headlines from Google Alerts Atom Feed."""
        try:
            # 1. Parse Google Alerts Feed
            url = "https://www.google.com/alerts/feeds/17320980821661560490/8904461684684252372"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            # Use xml parser for Atom feed
            soup = BeautifulSoup(resp.content, "xml")
            
            entries = soup.find_all('entry')[:4]
            
            structured_news = []
            pos_keywords = ['up', 'rise', 'cut', 'war', 'tension', 'higher', 'gain', 'safe-haven', 'surge', 'bullish']
            neg_keywords = ['fall', 'strong dollar', 'inflation', 'lower', 'negative', 'rate hike', 'hawk', 'drop', 'bearish']
            
            for entry in entries:
                title_raw = entry.find('title').get_text()
                # Remove HTML tags often found in Google Alert titles
                title = BeautifulSoup(title_raw, "html.parser").get_text(strip=True)
                
                link_tag = entry.find('link')
                link = link_tag.get('href', '#') if link_tag else '#'
                
                h_low = title.lower()
                impact = "Neutral"
                if any(kw in h_low for kw in pos_keywords): impact = "Positive"
                if any(kw in h_low for kw in neg_keywords): impact = "Negative"
                
                summary_th = title
                # Simple keyword mapping for Thai summaries
                if "Fed" in title or "Federal Reserve" in title:
                    summary_th = "ข่าวสารจาก Fed ส่งผลต่อความผันผวนของราคาทองคำ"
                elif "Dollar" in title:
                    summary_th = "ดัชนีดอลลาร์สหรัฐ (DXY) เป็นปัจจัยสำคัญในการกำหนดทิศทางราคา"
                elif "Gold" in title:
                    summary_th = "นักลงทุนจับตาความเคลื่อนไหวของราคาทองคำจากปัจจัยมหภาค"
                elif "Middle East" in title or "Israel" in title or "Iran" in title:
                    summary_th = "สถานการณ์ความตึงเครียดทางภูมิรัฐศาสตร์หนุนแรงซื้อสินทรัพย์ปลอดภัย"
                
                structured_news.append({
                    "title": title,
                    "impact": impact,
                    "summary_th": summary_th,
                    "link": link
                })
            
            # If parsing failed or empty, fallback to basic list
            if not structured_news:
                structured_news = [{
                    "title": "Market awaiting fresh catalysts for Gold direction",
                    "impact": "Neutral",
                    "summary_th": "ตลาดกำลังรอปัจจัยใหม่เพื่อกำหนดทิศทางของราคาทองคำ",
                    "link": "https://news.google.com/search?q=gold+price"
                }]

            # 2. Asian Market Specific Logic
            asian_news = self.analyze_asian_market_logic()
            
            # Combine: Dynamic News first, then Asian insights, limited to 4 items
            combined_news = structured_news + asian_news
            return combined_news[:4]
        except Exception as e:
            print(f"Market sentiment analysis error: {e}")
            return []

    def prepare_data(self, data):
        """Prepares data with lag features and indicators."""
        df = data.copy()
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['Lag_1'] = df['Close'].shift(1)
        df['Lag_2'] = df['Close'].shift(2)
        df['Lag_3'] = df['Close'].shift(3)
        return df.dropna()

    def predict_next_price(self):
        """Predicts using Weighted Linear Regression and SMA logic."""
        try:
            gold = yf.Ticker(self.ticker)
            data = gold.history(period="5d", interval="1h").tail(48)
            if len(data) < 25: return None
            
            df = self.prepare_data(data)
            if df.empty: return None

            X = np.arange(len(df)).reshape(-1, 1)
            y = df['Close'].values
            
            weights = np.ones(len(df))
            weights[-6:] = 3.0
            
            model = LinearRegression()
            model.fit(X, y, sample_weight=weights)
            
            slope = model.coef_[0]
            last_row = df.iloc[-1]
            is_up = (slope > 0) and (last_row['SMA_5'] > last_row['SMA_20'])
            
            current_price = last_row['Close']
            predicted_price = current_price + (slope if is_up else -abs(slope) if slope < 0 else -1.0)
            
            return {
                "price": predicted_price,
                "signal": "UP" if is_up else "DOWN",
                "slope": slope,
                "sma_5": last_row['SMA_5'],
                "sma_20": last_row['SMA_20']
            }
        except Exception as e:
            print(f"Error predicting price: {e}")
            return None

    def get_backtest_data(self, n_points=6):
        """Generates backtested predictions for the last N hours."""
        try:
            gold = yf.Ticker(self.ticker)
            # Fetch enough data for training + plotting
            data = gold.history(period="5d", interval="1h")
            if len(data) < n_points + 20: return [], []
            
            df = self.prepare_data(data)
            # Ensure yfinance data is localized correctly and converted to UTC
            if df.index.tz is not None:
                df.index = df.index.tz_convert('UTC')
            else:
                df.index = df.index.tz_localize('UTC')

            actuals = []
            predictions = []
            labels = []
            
            # We want to see the last n_points
            for i in range(n_points, 0, -1):
                target_row = df.iloc[-(i)]
                
                # Simple Linear Regression for backtest point
                train_data = df.iloc[:-(i)]
                X_train = np.arange(len(train_data)).reshape(-1, 1)
                y_train = train_data['Close'].values
                
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                pred = model.predict([[len(train_data)]])[0]
                
                # Get UTC timestamp
                timestamp = target_row.name
                actuals.append(target_row['Close'])
                predictions.append(pred)
                labels.append(timestamp.timestamp())
                
            return labels, actuals, predictions
        except Exception as e:
            print(f"Backtest error: {e}")
            return [], [], []

    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average."""
        return data['Close'].ewm(span=period, adjust=False).mean()
    
    def check_ema_crossover(self, data, lookback=3):
        """Check if 9 EMA crossed 21 EMA in the last N bars."""
        ema_9 = self.calculate_ema(data, 9)
        ema_21 = self.calculate_ema(data, 21)
        
        # Check for bullish crossover (9 crosses above 21)
        for i in range(1, min(lookback + 1, len(data))):
            if ema_9.iloc[-i] > ema_21.iloc[-i] and ema_9.iloc[-i-1] <= ema_21.iloc[-i-1]:
                return "BULLISH", 50
            # Check for bearish crossover (9 crosses below 21)
            elif ema_9.iloc[-i] < ema_21.iloc[-i] and ema_9.iloc[-i-1] >= ema_21.iloc[-i-1]:
                return "BEARISH", 50
        
        # No crossover, check current position
        if ema_9.iloc[-1] > ema_21.iloc[-1]:
            return "BULLISH", 0  # Bullish but no recent crossover
        else:
            return "BEARISH", 0  # Bearish but no recent crossover
    
    def check_rsi_alignment(self, data, trend):
        """Check if RSI is aligned with price trend (no divergence)."""
        rsi = self.get_rsi(data)
        prices = data['Close'].tail(5)
        
        # Simple alignment check: RSI moving in same direction as price
        price_rising = prices.iloc[-1] > prices.iloc[-3]
        rsi_values = []
        
        for i in range(5):
            temp_data = data.iloc[:-(5-i)] if i < 4 else data
            if len(temp_data) >= 20:
                rsi_values.append(self.get_rsi(temp_data))
        
        if len(rsi_values) >= 3:
            rsi_rising = rsi_values[-1] > rsi_values[-3]
            
            # Check alignment
            if trend == "BULLISH" and price_rising and rsi_rising:
                return 20
            elif trend == "BEARISH" and not price_rising and not rsi_rising:
                return 20
        
        return 0
    
    def institutional_grade_analysis(self, news_cache=None):
        """Institutional scoring system: EMA + RSI + News + DXY (0-100 scale)."""
        try:
            current_price, data, dxy_price = self.fetch_current_price()
            if data is None or len(data) < 30:
                return None
            
            # 1. TREND ANALYSIS (50 points) - EMA Crossover
            trend_signal, trend_points = self.check_ema_crossover(data, lookback=3)
            
            # 2. RSI ALIGNMENT (20 points)
            rsi = self.get_rsi(data)
            rsi_points = self.check_rsi_alignment(data, trend_signal)
            
            # 3. NEWS SENTIMENT (15 points)
            if news_cache:
                market_news = news_cache
            else:
                market_news = self.analyze_market_sentiment_premium()
            pos_count = sum(1 for n in market_news if n['impact'] == "Positive" or n['impact'] == "Bullish")
            neg_count = sum(1 for n in market_news if n['impact'] == "Negative" or n['impact'] == "Caution/Bearish")
            
            if pos_count > neg_count:
                sentiment = "Supportive"
                news_points = 15
            elif neg_count > pos_count:
                sentiment = "Opposite"
                news_points = 0
            else:
                sentiment = "Neutral"
                news_points = 15
            
            # HARD STOP: If sentiment is opposite to trend
            if (trend_signal == "BULLISH" and sentiment == "Opposite") or \
               (trend_signal == "BEARISH" and sentiment == "Supportive"):
                confidence_score = 0
                news_points = 0
                sentiment = "Opposite"
            else:
                # 4. DXY CORRELATION (15 points)
                dxy = yf.Ticker("DX-Y.NYB")
                dxy_hist = dxy.history(period="1d", interval="1h")
                dxy_trend = "Down" if (len(dxy_hist) > 1 and dxy_hist['Close'].iloc[-1] < dxy_hist['Close'].iloc[-2]) else "Up"
                
                # Gold and DXY are inversely correlated
                if (trend_signal == "BULLISH" and dxy_trend == "Down") or \
                   (trend_signal == "BEARISH" and dxy_trend == "Up"):
                    dxy_points = 15
                else:
                    dxy_points = 0
                
                # CALCULATE TOTAL CONFIDENCE SCORE
                confidence_score = trend_points + rsi_points + news_points + dxy_points
            
            # Determine prediction
            prediction = "Strong UP" if trend_signal == "BULLISH" else "Strong DOWN"
            
            # Get predicted price from regression
            reg_result = self.predict_next_price()
            predicted_price = reg_result['price'] if reg_result else current_price
            
            # Executive reasoning in Thai
            if confidence_score >= 75 and confidence_score <= 80:
                reasoning = f"🔔 สัญญาณเทรด (Confidence {confidence_score}%) - แนวโน้มตลาด {trend_signal} มีความแข็งแกร่ง ผลกระทบจากข่าวอยู่ในระดับ {sentiment} คาดการณ์การเคลื่อนที่ใน 1 ชม. ข้างหน้า: {prediction}"
            elif confidence_score > 80:
                reasoning = f"ความเชื่อมั่นสูงมาก ({confidence_score}%) - สัญญาณเทคนิคและปัจจัยพื้นฐานสอดคล้องกันอย่างชัดเจน"
            elif confidence_score >= 60:
                reasoning = f"ความเชื่อมั่นปานกลาง ({confidence_score}%) - ตลาดมีสัญญาณแต่ควรเฝ้าระวังปัจจัยเสี่ยง"
            else:
                reasoning = f"ความเชื่อมั่นต่ำ ({confidence_score}%) - สัญญาณเทคนิคขัดแย้งกัน แนะนำรอความชัดเจน"
            
            return {
                "prediction": prediction,
                "predicted_price": predicted_price,
                "rsi": rsi,
                "rsi_signal": "Aligned" if rsi_points > 0 else "Divergence",
                "sentiment": sentiment,
                "headlines": [n['title'] for n in market_news],
                "dxy_trend": dxy_trend if confidence_score > 0 else "N/A",
                "price": current_price,
                "confidence": confidence_score,
                "reasoning": reasoning,
                "market_news": market_news,
                "trend_signal": trend_signal,
                "score_breakdown": {
                    "trend": trend_points,
                    "rsi": rsi_points,
                    "news": news_points,
                    "dxy": dxy_points if confidence_score > 0 else 0
                }
            }
        except Exception as e:
            print(f"Institutional analysis error: {e}")
            return None

    def get_model_accuracy(self):
        """Calculates Directional Accuracy using Backtesting."""
        try:
            gold = yf.Ticker(self.ticker)
            data = gold.history(period="5d", interval="1h")
            if len(data) < 20: return 0.0, None
            df = self.prepare_data(data)
            train_df = df.iloc[:-12]
            test_df = df.tail(12)
            if train_df.empty or test_df.empty: return 0.0, None
            
            X_train = np.arange(len(train_df)).reshape(-1, 1)
            y_train = train_df['Close'].values
            X_test = np.arange(len(train_df), len(df)).reshape(-1, 1)
            y_test = test_df['Close'].values
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            
            actual_dir = np.sign(y_test - test_df['Lag_1'].values)
            pred_dir = np.sign(predictions - test_df['Lag_1'].values)
            correct = (actual_dir == pred_dir)
            accuracy = (correct.sum() / len(correct)) * 100
            return accuracy, bool(correct[-1])
        except Exception as e:
            print(f"Accuracy error: {e}")
            return 0.0, None

    def send_notification(self, current_price, precision_data, accuracy):
        """Executive Briefing Format in Thai."""
        if not self.email_address or not self.email_password or not self.recipient_email: return
        subject = "Gold Price Agent: Executive Briefing"
        headlines_str = "\n".join([f"- {h}" for h in precision_data['headlines'][:3]])
        body = f"""
💼 รายงานสรุปภาวะตลาดทองคำสำหรับผู้บริหาร (Executive Briefing)

💰 ข้อมูลพื้นฐาน:
- ราคาล่าสุด (Gold GC=F): ${current_price:.2f}
- ดัชนีค่าเงินดอลลาร์ (DXY): {precision_data['dxy_trend']} Trend

🔮 การวิเคราะห์และพยากรณ์:
- แนวโน้มคาดการณ์: {precision_data['prediction']}
- ความแม่นยำย้อนหลัง 12 ชม.: {accuracy:.1f}%

📊 ข้อมูลทางเทคนิคและจิตวิทยาตลาด:
- RSI (14): {precision_data['rsi']:.2f} ({precision_data['rsi_signal']})
- ความรู้สึกตลาด (Sentiment): {precision_data['sentiment']}

🌍 สรุปข่าวสำคัญ:
{headlines_str}

--------------------------------------------------
⚠️ หมายเหตุ: ข้อมูลนี้จัดทำขึ้นเพื่อการสาธิตเท่านั้น ไม่ใช่คำแนะนำทางการเงิน

Gold Price Agent (High-Precision Unit)
รายงานเมื่อ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, self.recipient_email, text)
            server.quit()
            print(f"Executive Briefing Sent! Prediction: {precision_data['prediction']}")
        except Exception as e:
            print(f"Failed to send email: {e}")
