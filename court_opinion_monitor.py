#!/usr/bin/env python3
"""
Texas Court Opinion Release Monitor

Monitors 14 Texas Courts of Appeals for opinion releases during business hours.
Checks for -CV or -CR text indicating released opinions every 5 minutes from 8am-6pm on weekdays.
Records the time when opinions are first detected and stops checking that court for the day.
"""

import requests
import schedule
import time
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
import signal
import sys

# Configuration
COURTS = [f"coa{i:02d}" for i in range(1, 15)]  # coa01 through coa14
BASE_URL = "https://search.txcourts.gov/Docket.aspx"
CHECK_INTERVAL_MINUTES = 5
START_HOUR = 0  # Midnight
END_HOUR = 24   # Midnight (24/7 monitoring)
DATA_FILE = "court_release_data.json"
LOG_FILE = "court_monitor.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CourtMonitor:
    def __init__(self):
        self.data_file = Path(DATA_FILE)
        self.running = True
        self.load_data()
        
    def load_data(self):
        """Load existing monitoring data from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded existing data from {DATA_FILE}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading data file: {e}")
                self.data = {}
        else:
            self.data = {}
            logger.info("Starting with empty data file")
    
    def save_data(self):
        """Save monitoring data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            logger.debug("Data saved successfully")
        except IOError as e:
            logger.error(f"Error saving data: {e}")
    
    def get_today_key(self):
        """Get today's date as string key"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def is_business_day(self):
        """Check if today is a weekday"""
        return datetime.now().weekday() < 5  # Monday = 0, Sunday = 6
    
    def is_business_hours(self):
        """Check if current time is within business hours (now 24/7)"""
        return True  # Monitor 24/7
    
    def check_court_page(self, court_code, date_str):
        """Check a specific court's page for opinion releases"""
        url = f"{BASE_URL}?coa={court_code}&FullDate={date_str}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check for opinion indicators
            content = response.text
            has_opinions = '-CV' in content or '-CR' in content
            
            logger.debug(f"Checked {court_code}: {'Found opinions' if has_opinions else 'No opinions'}")
            return has_opinions
            
        except requests.RequestException as e:
            logger.error(f"Error checking {court_code}: {e}")
            return False
    
    def record_release(self, court_code, timestamp):
        """Record when a court released opinions"""
        today_key = self.get_today_key()
        
        if today_key not in self.data:
            self.data[today_key] = {}
        
        self.data[today_key][court_code] = {
            'release_time': timestamp.isoformat(),
            'status': 'released'
        }
        
        self.save_data()
        logger.info(f"📋 {court_code.upper()} released opinions at {timestamp.strftime('%H:%M:%S')}")
    
    def should_check_court(self, court_code):
        """Determine if we should check this court today"""
        today_key = self.get_today_key()
        
        # If no data for today, we should check
        if today_key not in self.data:
            return True
        
        # If no data for this court today, we should check
        if court_code not in self.data[today_key]:
            return True
        
        # If already found release today, don't check again
        return self.data[today_key][court_code].get('status') != 'released'
    
    def check_all_courts(self):
        """Check all courts that haven't released opinions today"""
        if not self.is_business_day():
            logger.debug("Not a business day, skipping checks")
            return
        
        # Remove business hours check - now monitoring 24/7
        
        now = datetime.now()
        date_str = now.strftime("%m/%d/%Y")
        courts_to_check = [court for court in COURTS if self.should_check_court(court)]
        
        if not courts_to_check:
            logger.debug("All courts have released opinions today")
            return
        
        logger.info(f"Checking {len(courts_to_check)} courts: {', '.join(courts_to_check)}")
        
        for court_code in courts_to_check:
            if not self.running:
                break
                
            try:
                if self.check_court_page(court_code, date_str):
                    self.record_release(court_code, now)
                time.sleep(1)  # Small delay between requests
            except Exception as e:
                logger.error(f"Unexpected error checking {court_code}: {e}")
    
    def cleanup_old_data(self, days_to_keep=30):
        """Remove data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_key = cutoff_date.strftime("%Y-%m-%d")
        
        keys_to_remove = [key for key in self.data.keys() if key < cutoff_key]
        
        for key in keys_to_remove:
            del self.data[key]
        
        if keys_to_remove:
            self.save_data()
            logger.info(f"Cleaned up {len(keys_to_remove)} old data entries")
    
    def get_status_summary(self):
        """Get summary of today's monitoring status"""
        today_key = self.get_today_key()
        today_data = self.data.get(today_key, {})
        
        released_courts = [court for court, info in today_data.items() 
                          if info.get('status') == 'released']
        pending_courts = [court for court in COURTS if court not in released_courts]
        
        return {
            'date': today_key,
            'released': len(released_courts),
            'pending': len(pending_courts),
            'released_courts': released_courts,
            'pending_courts': pending_courts
        }
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def run(self):
        """Main monitoring loop"""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🚀 Texas Court Opinion Monitor started")
        logger.info(f"Monitoring {len(COURTS)} courts: {', '.join(COURTS)}")
        logger.info("Business hours: 24/7 monitoring, weekdays only")
        logger.info(f"Check interval: {CHECK_INTERVAL_MINUTES} minutes")
        
        # Schedule the monitoring job
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.check_all_courts)
        
        # Schedule daily cleanup
        schedule.every().day.at("07:00").do(self.cleanup_old_data)
        
        # Initial status check
        self.check_all_courts()
        
        # Main monitoring loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check schedule every 30 seconds
                
                # Log status every hour during weekdays
                if datetime.now().minute == 0 and self.is_business_day():
                    status = self.get_status_summary()
                    logger.info(f"📊 Status: {status['released']}/{len(COURTS)} courts released opinions today")
                    
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    monitor = CourtMonitor()
    monitor.run() 