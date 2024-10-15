import os
from datetime import datetime, timedelta

# Define the base path for the logs
base_path = "data/logs"

# Create logs directory if it doesn't exist
os.makedirs(base_path, exist_ok=True)

# Generate logs for the past 35 days
for i in range(35):
    log_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

    print(log_date)
    # Define log file names
    custom_logger_file = os.path.join(base_path, f"{log_date}.customLogger_debug.log")
    debug_file = os.path.join(base_path, f"{log_date}.debug.log")

    with open(custom_logger_file, "a") as custom_log:
        custom_log.write(f"{log_date} - CUSTOM_LOGGER - Debug message for {log_date}\n")

    with open(debug_file, "a") as debug_log:
        debug_log.write(f"{log_date} - DEBUG - Debug message for {log_date}\n")

print("Log files created successfully.")
