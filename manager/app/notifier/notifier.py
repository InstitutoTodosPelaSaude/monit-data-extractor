import datetime
import sqlite3

DB_PATH = '/data/monitor.db'
MINIMUM_TIME_FOR_NOTIFICATION_IN_MINUTES = 5

# Convert the minimum notification time into a timedelta object
time_limit = datetime.timedelta(minutes=MINIMUM_TIME_FOR_NOTIFICATION_IN_MINUTES)

# Define the query to get the latest file upload for each organization and project
query_latest_file_for_each_organization = """
    SELECT 
        project, organization, filename, upload_ts
    FROM (
        SELECT
            row_number() OVER(PARTITION BY organization, project ORDER BY upload_ts DESC) AS row_id,
            project, organization, filename, upload_ts
        FROM file
    )
    WHERE row_id = 1
"""

# Function to check for organizations that haven't sent files recently
def check_notifications():
    print("Notifier Running")
    
    # Connect to the SQLite database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Execute the query to get the latest uploads
        cursor.execute(query_latest_file_for_each_organization)
        results = cursor.fetchall()

        # Get the current time
        current_time = datetime.datetime.now()

        # Iterate over the results and check the upload timestamps
        for project, organization, filename, upload_ts in results:
            # Convert the upload timestamp to a datetime object
            upload_time = datetime.datetime.fromisoformat(upload_ts)

            # Check if the upload is older than the time limit
            if current_time - upload_time > time_limit:
                print(f"Organization {organization} didn't send a file for project {project} in the last {MINIMUM_TIME_FOR_NOTIFICATION_IN_MINUTES}. Last file: '{filename}' in {upload_time}")
            else:
                print(f"Organization {organization} is on schedule for project {project}. Last file sent in {upload_time}")


# Run the notification check
check_notifications()
