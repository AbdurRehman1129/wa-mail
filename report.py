# report.py
import sys
from datetime import datetime, timezone, timedelta

def log_report(email, number, timestamp):
    # Convert UTC timestamp to Pakistan Standard Time
    pst_offset = timedelta(hours=5)
    pst_time = timestamp + pst_offset
    pst_time_str = pst_time.strftime("[%H:%M]")

    # Format the report entry
    report_entry = f"{pst_time_str} {email} {number}\n"

    # Write to report.txt
    with open("report.txt", "a") as report_file:
        report_file.write(report_entry)

if __name__ == "__main__":
    # Read command-line arguments (email, number, timestamp)
    if len(sys.argv) < 4:
        print("Usage: report.py <email> <number> <timestamp>")
    else:
        email = sys.argv[1]
        number = sys.argv[2]
        timestamp = datetime.fromisoformat(sys.argv[3])

        log_report(email, number, timestamp)
