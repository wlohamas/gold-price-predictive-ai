import schedule
import time
from gold_agent import GoldAgent
import datetime

def job():
    print(f"Starting job at {datetime.datetime.now()}")
    agent = GoldAgent()
    
    current_price, _ = agent.fetch_current_price()
    if current_price:
        predicted_price = agent.predict_next_price()
        if predicted_price:
            print(f"Price: {current_price}, Prediction: {predicted_price}")
            agent.send_notification(current_price, predicted_price)
        else:
            print("Could not make a prediction.")
    else:
        print("Could not fetch current price.")
    print("Job finished.")

def main():
    print("Gold Price Agent Started...")
    print("Scheduling job every 1 hour.")
    
    # Run immediately once on startup
    job()
    
    # Schedule every hour
    schedule.every(1).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
