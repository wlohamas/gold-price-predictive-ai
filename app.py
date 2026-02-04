import threading
import time
import schedule
from flask import Flask, render_template, jsonify
from gold_agent import GoldAgent
import datetime
import os
import yfinance as yf

app = Flask(__name__)

# Global storage for latest data to serve via API
latest_data = {
    "price": None,
    "prediction": None,
    "last_updated": None,
    "trend": None
}

# Track last email time
last_email_time = None

# Add locked forecast storage (to fix prediction for the entire hour)
locked_forecast = {
    "price": None,
    "target_hour": None,
    "raw_trend": None,
    "confidence": None  # Add confidence locking
}

# Add news caching globals (1 minute refresh)
news_cache = []
last_news_refresh = 0

# Add hourly snapshots storage (locked values at top of each hour)
import json

SNAPSHOTS_FILE = "snapshots.json"

def load_snapshots():
    if os.path.exists(SNAPSHOTS_FILE):
        try:
            with open(SNAPSHOTS_FILE, "r") as f:
                data = json.load(f)
                # Convert string keys back to floats (timestamps)
                return {float(k): v for k, v in data.items()}
        except:
            return {}
    return {}

def save_snapshots(snapshots):
    try:
        # Convert float keys to strings for JSON
        data = {str(k): v for k, v in snapshots.items()}
        with open(SNAPSHOTS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving snapshots: {e}")

hourly_snapshots = load_snapshots()

# Add locked forecast persistence
FORECAST_FILE = "locked_forecast.json"

def load_forecast():
    if os.path.exists(FORECAST_FILE):
        try:
            with open(FORECAST_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "price": None,
        "target_hour": None,
        "raw_trend": None,
        "confidence": None
    }

def save_forecast(forecast):
    try:
        with open(FORECAST_FILE, "w") as f:
            json.dump(forecast, f)
    except Exception as e:
        print(f"Error saving forecast: {e}")

locked_forecast = load_forecast()

def job():
    global last_email_time, locked_forecast, news_cache, last_news_refresh, hourly_snapshots
    print(f"[{datetime.datetime.now()}] Running high-precision job...")
    agent = GoldAgent()
    
    # Force fresh news fetch every time to satisfy user request for frequent updates
    current_news = None
    now_ts = time.time()
    print("Refreshing NEWS from Data Source...")

    # 1. Institutional Grade Analysis
    try:
        precision_data = agent.institutional_grade_analysis(news_cache=current_news)
        if precision_data and current_news is None: # We fetched fresh news
            news_cache = precision_data['market_news']
            last_news_refresh = now_ts
            # Use standard 12h format: e.g. "1:26 PM"
            bangkok_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            latest_data["news_last_updated"] = bangkok_now.strftime('%-I:%M %p')
    except Exception as e:
        print(f"Institutional analysis error in job: {e}")
        return

    accuracy, last_correct = agent.get_model_accuracy()
    
    if precision_data:
        current_price = precision_data['price']
        
        # Calculate Bangkok Time (UTC+7)
        bangkok_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        target_hour = (bangkok_now + datetime.timedelta(hours=1)).hour
        
        # HOURLY LOCK LOGIC: 
        # Only update the 'predicted_price', 'trend', and 'confidence' once per hour
        if locked_forecast["target_hour"] != target_hour or locked_forecast["price"] is None:
            # When we transition to a new hour (e.g., from 12:59 to 13:00)
            # 1. Snapshot the hour that just FINISHED (e.g., the 12:00 PM to 1:00 PM period)
            if locked_forecast["target_hour"] is not None:
                # The hour that just finished started 1 hour ago
                finished_hour_dt = bangkok_now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
                finished_hour_utc = (finished_hour_dt - datetime.timedelta(hours=7)).replace(tzinfo=datetime.timezone.utc)
                finished_hour_ts = finished_hour_utc.timestamp()
                
                # We compare the current_price (at 1:00 PM) to the forecast we had for 1:00 PM
                if finished_hour_ts not in hourly_snapshots:
                    hourly_snapshots[finished_hour_ts] = {
                        "actual": current_price,
                        "predicted": locked_forecast["price"]
                    }
                    save_snapshots(hourly_snapshots)
                    print(f"🔒 HOUR COMPLETED & LOCKED: {finished_hour_dt.strftime('%H:%M')} -> Actual=${current_price:.2f}, Predicted=${locked_forecast['price']:.2f}")

            # 2. Lock the NEW forecast for the upcoming hour (e.g., the 1:00 PM to 2:00 PM period)
            locked_forecast["price"] = precision_data.get('predicted_price', current_price)
            locked_forecast["target_hour"] = target_hour
            locked_forecast["raw_trend"] = precision_data['prediction']
            locked_forecast["confidence"] = precision_data['confidence']
            save_forecast(locked_forecast)
            print(f">>> [{bangkok_now}] New Hourly Forecast LOCKED: {target_hour}:00 Target = ${locked_forecast['price']:.2f}")

        # Use the locked values for the dashboard
        final_prediction_price = locked_forecast["price"]
        final_trend = locked_forecast["raw_trend"]
            
        # Update global state for API/Dashboard
        # Calculate overall accuracy based on the last 6 LOCKED snapshots (Performance 6H)
        recent_snapshots = sorted(hourly_snapshots.items(), key=lambda x: x[0], reverse=True)[:6]
        if len(recent_snapshots) > 0:
            total_acc = 0
            for ts, snap in recent_snapshots:
                act = snap["actual"]
                pre = snap["predicted"]
                diff = abs(act - pre)
                total_acc += max(0, 100 - (diff / act * 100))
            avg_accuracy = total_acc / len(recent_snapshots)
            last_correct = abs(recent_snapshots[0][1]["actual"] - recent_snapshots[0][1]["predicted"]) < (recent_snapshots[0][1]["actual"] * 0.005) # Within 0.5%
        else:
            # Fallback to model backtest if no snapshots yet
            avg_accuracy, last_correct = agent.get_model_accuracy()

        latest_data["price"] = current_price
        latest_data["prediction_raw"] = final_trend 
        latest_data["prediction"] = final_prediction_price
        latest_data["pct_change"] = ((final_prediction_price - current_price) / current_price) * 100
        latest_data["accuracy"] = avg_accuracy
        latest_data["last_correct"] = last_correct
        
        # Performance Reasoning Logic
        if accuracy >= 90:
            latest_data["accuracy_reason"] = "โมเดลจับทิศทางตลาดได้แม่นยำสูงในสภาวะแนวโน้มชัดเจน"
        elif accuracy >= 70:
            latest_data["accuracy_reason"] = "โมเดลทำงานได้ดีท่ามกลางความผันผวนปกติของตลาด"
        elif accuracy >= 50:
            latest_data["accuracy_reason"] = "ตลาดมีความผันผวนสูงกว่าปกติ กระทบต่อความแม่นยำรายชั่วโมง"
        else:
            latest_data["accuracy_reason"] = "ตลาดอยู่ในช่วงเปลี่ยนเทรดรวดเร็ว โมเดลอยู่ระหว่างการเรียนรู้รูปแบบใหม่"

        latest_data["trend"] = precision_data['prediction']
        latest_data["confidence"] = locked_forecast.get("confidence", precision_data['confidence'])  # Use locked confidence
        latest_data["reasoning"] = precision_data['reasoning']
        latest_data["market_news"] = precision_data['market_news']
        latest_data["last_updated"] = bangkok_now.strftime('%H:%M:%S')
        
        # Calculate next hour for forecast display (Bangkok Time)
        next_hour_dt = (bangkok_now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        latest_data["forecast_time"] = next_hour_dt.strftime('%-I %p') # e.g. "10 PM"
        
        # Sentiment summary for frontend if needed
        latest_data["sentiment"] = precision_data['sentiment']
        latest_data["rsi"] = precision_data['rsi']

        print(f"Updated at {latest_data['last_updated']}: Price={current_price}, Prediction={precision_data['prediction']}")
        
        # 2. Fetch history and backtest for chart
        try:
            labels, actuals, backtest_preds = agent.get_backtest_data(n_points=12)
            # Use the LOCKED model predicted price for consistency
            next_pred = locked_forecast["price"]
            
            # Current UTC epoch
            now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
            
            # Forecast UTC epoch (Next top of the hour)
            forecast_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            forecast_ts = forecast_dt.replace(minute=0, second=0, microsecond=0).timestamp()

            # Filter yf labels to only those strictly before 'now'
            valid_indices = [i for i, ts in enumerate(labels) if ts < now_ts - 10] 
            f_labels = [labels[i] for i in valid_indices]
            f_actuals = [actuals[i] for i in valid_indices]
            f_backtest_preds = [backtest_preds[i] for i in valid_indices]

            # HOURLY SNAPSHOT FETCH (Keep it consistent with our manual snapshots)
            # We still fetch backtest for the chart points that aren't in our locked snapshots
            for i in range(len(f_labels)):
                label_dt = datetime.datetime.fromtimestamp(f_labels[i], tz=datetime.timezone.utc)
                hour_ts = label_dt.replace(minute=0, second=0, microsecond=0).timestamp()
                
                # If we have a manually locked snapshot (more accurate for what user saw), use it
                if hour_ts in hourly_snapshots:
                    f_actuals[i] = hourly_snapshots[hour_ts]["actual"]
                    f_backtest_preds[i] = hourly_snapshots[hour_ts]["predicted"]
                else:
                    # Otherwise, if we haven't locked it yet but it's clearly passed, 
                    # we can use the backtest but we should really trust our snapshots more.
                    pass


            # Get the locked forecast for the CURRENT hour (not next hour)
            current_hour_dt = bangkok_now.replace(minute=0, second=0, microsecond=0)
            current_hour_utc = (current_hour_dt - datetime.timedelta(hours=7)).replace(tzinfo=datetime.timezone.utc)
            current_hour_ts = current_hour_utc.timestamp()
            
            # Use locked forecast for current hour if available, otherwise use current price as fallback
            current_hour_prediction = hourly_snapshots.get(current_hour_ts, {}).get("predicted", current_price)

            latest_data["chart"] = {
                "labels": f_labels + [now_ts, forecast_ts],
                "prices": f_actuals + [current_price, None], 
                "prediction_point": f_backtest_preds + [current_hour_prediction, next_pred], 
                "high_threshold": [current_price * 1.03] * (len(f_labels) + 2),
                "low_threshold": [current_price * 0.97] * (len(f_labels) + 2)
            }
        except Exception as e:
            print(f"Chart history error: {e}")

        # 3. Executive Briefing Email
        current_time = datetime.datetime.now()
        if last_email_time is None or (current_time - last_email_time).total_seconds() >= 3600:
            agent.send_notification(current_price, precision_data, accuracy)
            last_email_time = current_time
    else:
        print("High-precision job failed (Insufficient data or fetch error)")

def run_schedule():
    """Runs the schedule loop."""
    # Run once on startup
    job()
    # Update every 10 seconds for real-time feel
    schedule.every(10).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/latest')
def get_latest():
    # If no data yet (e.g. very first start), try to fetch immediately without waiting for scheduler
    if latest_data["price"] is None:
         # Quick fetch for immediate UI responsiveness (blocking but safe for first load)
        job() 
        
    return jsonify(latest_data)

if __name__ == '__main__':
    # Start scheduler in a separate thread
    t = threading.Thread(target=run_schedule)
    t.daemon = True
    t.start()
    
    # Start Flask server
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
