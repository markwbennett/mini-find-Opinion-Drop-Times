#!/usr/bin/env python3
"""
Texas Court Opinion Data Viewer

Utility script to view and analyze collected court opinion release times.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DATA_FILE = "court_release_data.json"

def load_data():
    """Load the court monitoring data"""
    data_file = Path(DATA_FILE)
    if not data_file.exists():
        print(f"❌ Data file {DATA_FILE} not found")
        return None
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Error loading data: {e}")
        return None

def format_time(iso_time):
    """Format ISO time string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S')
    except:
        return iso_time

def show_summary(data):
    """Show summary of collected data"""
    print("📊 DATA SUMMARY")
    print("=" * 50)
    
    total_days = len(data)
    total_releases = 0
    court_stats = defaultdict(int)
    
    for date, day_data in data.items():
        day_releases = len([c for c, info in day_data.items() if info.get('status') == 'released'])
        total_releases += day_releases
        
        for court, info in day_data.items():
            if info.get('status') == 'released':
                court_stats[court] += 1
    
    print(f"Total monitoring days: {total_days}")
    print(f"Total opinion releases: {total_releases}")
    print(f"Average releases per day: {total_releases/total_days:.1f}")
    print()
    
    print("📈 COURT ACTIVITY")
    print("-" * 30)
    for court in sorted(court_stats.keys()):
        count = court_stats[court]
        percentage = (count / total_days) * 100
        print(f"{court.upper()}: {count}/{total_days} days ({percentage:.1f}%)")

def show_daily_detail(data):
    """Show detailed daily breakdown"""
    print("\n📅 DAILY DETAILS")
    print("=" * 50)
    
    for date in sorted(data.keys()):
        day_data = data[date]
        released = [(c, info['release_time']) for c, info in day_data.items() 
                   if info.get('status') == 'released']
        
        print(f"\n{date} ({len(released)} releases)")
        print("-" * 30)
        
        if released:
            for court, release_time in sorted(released, key=lambda x: x[1]):
                time_str = format_time(release_time)
                print(f"  {court.upper()}: {time_str}")
        else:
            print("  No releases recorded")

def show_time_analysis(data):
    """Analyze release times"""
    print("\n⏰ TIME ANALYSIS")
    print("=" * 50)
    
    hour_counts = defaultdict(int)
    court_times = defaultdict(list)
    
    for date, day_data in data.items():
        for court, info in day_data.items():
            if info.get('status') == 'released':
                try:
                    dt = datetime.fromisoformat(info['release_time'].replace('Z', '+00:00'))
                    hour = dt.hour
                    hour_counts[hour] += 1
                    court_times[court].append(dt.time())
                except:
                    continue
    
    print("Release frequency by hour:")
    for hour in sorted(hour_counts.keys()):
        count = hour_counts[hour]
        bar = "█" * min(count, 20)
        print(f"  {hour:02d}:00 │{bar:<20}│ {count}")
    
    print("\nAverage release times by court:")
    for court in sorted(court_times.keys()):
        times = court_times[court]
        if times:
            # Convert times to minutes for averaging
            total_minutes = sum(t.hour * 60 + t.minute for t in times)
            avg_minutes = total_minutes / len(times)
            avg_hour = int(avg_minutes // 60)
            avg_min = int(avg_minutes % 60)
            print(f"  {court.upper()}: {avg_hour:02d}:{avg_min:02d} (from {len(times)} releases)")

def main():
    """Main function"""
    data = load_data()
    if not data:
        sys.exit(1)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "summary":
            show_summary(data)
        elif command == "daily":
            show_daily_detail(data)
        elif command == "times":
            show_time_analysis(data)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 view_data.py [summary|daily|times]")
    else:
        # Show everything by default
        show_summary(data)
        show_daily_detail(data)
        show_time_analysis(data)

if __name__ == "__main__":
    main() 