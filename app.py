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

def job():
    """Background job for high-precision forecasting and briefing."""
    global last_email_time
    print(f"Running high-precision job at {datetime.datetime.now()}")
    agent = GoldAgent()
    
    # 1. Institutional Grade Analysis
    precision_data = agent.institutional_grade_analysis()
    accuracy, last_correct = agent.get_model_accuracy()
    
    if precision_data:
        current_price = precision_data['price']
        
        # Update global state for API/Dashboard
        latest_data["price"] = current_price
        latest_data["prediction_raw"] = precision_data['prediction'] 
        latest_data["prediction"] = precision_data.get('predicted_price', current_price)
        latest_data["pct_change"] = ((latest_data["prediction"] - current_price) / current_price) * 100
        latest_data["accuracy"] = accuracy
        latest_data["last_correct"] = last_correct
        latest_data["trend"] = precision_data['prediction']
        latest_data["confidence"] = precision_data['confidence']
        latest_data["reasoning"] = precision_data['reasoning']
        latest_data["market_news"] = precision_data['market_news']
        latest_data["last_updated"] = datetime.datetime.now().strftime('%H:%M:%S')
        
        # Sentiment summary for frontend if needed
        latest_data["sentiment"] = precision_data['sentiment']
        latest_data["rsi"] = precision_data['rsi']

        print(f"Price: {current_price}, Prediction: {precision_data['prediction']}, RSI: {precision_data['rsi']:.1f}, Acc: {accuracy:.1f}%")
        
        # 2. Fetch history and backtest for chart
        try:
            labels, actuals, backtest_preds = agent.get_backtest_data(n_points=6)
            
            # Use the actual model predicted price for consistency
            next_pred = precision_data.get('predicted_price', current_price)
            next_label = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:00')

            latest_data["chart"] = {
                "labels": labels + [next_label],
                "prices": actuals + [None], # History stops at current
                "prediction_point": backtest_preds + [next_pred], # Backtest + Future
                "high_threshold": [current_price * 1.03] * (len(labels) + 1),
                "low_threshold": [current_price * 0.97] * (len(labels) + 1)
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
    # Update every 1 minute
    schedule.every(1).minutes.do(job)
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
    app.run(debug=True, port=5001, use_reloader=False) # use_reloader=False to avoid duplicate threads
