import datetime
import sqlite3

DB_PATH = '/data/monitor.db'
MINIMUM_TIME_FOR_NOTIFICATION_IN_DAYS = 5

# Convert the minimum notification time into a timedelta object
time_limit = datetime.timedelta(days=MINIMUM_TIME_FOR_NOTIFICATION_IN_DAYS)

labs_monitored = ['fleury', 'einstein',
                  'sabin' , 'hlagyn',
                  'hilab' , 'hpardini']

projects = ['arbo', 'respat']

# Define the query to get the latest file upload for each organization and project
query_latest_file_for_each_organization = f"""
    WITH last_friday AS (
        SELECT DATE('now', '-' || ((strftime('%w', 'now') + 2) % 7 ) || ' days') AS friday_date
    )
    SELECT 
        project, 
        organization, 
        filename, 
        upload_ts
    FROM 
        file, last_friday
    WHERE 
        DATE(upload_ts) >= last_friday.friday_date
    AND organization 
    IN ('fleury', 'einstein',
        'sabin' , 'hlagyn',
        'hilab' , 'hpardini')
    ;
"""

# Function to check for organizations that haven't sent files recently
def create_summary():
    """
    Generates a summary of the file uploads for each project and organization.
    
    Returns:
        str: A formatted string containing the summary report.
    """
    summary_report = []
    summary_report.append("Notifier Running\n")
    
    # Connect to the SQLite database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Execute the query to get the latest uploads
        cursor.execute(query_latest_file_for_each_organization)
        results = cursor.fetchall()
        
        # Process results
        summary = {project: {lab: {"status": "🔴", "files": []} for lab in labs_monitored} for project in projects}
        
        # Fill the summary based on query results
        for project, organization, filename, upload_ts in results:
            upload_date = datetime.datetime.fromisoformat(upload_ts)
            summary[project][organization]["status"] = "🟢"
            summary[project][organization]["files"].append((filename, upload_date.strftime("%Y-%m-%d")))

        # Generate the report
        for project, organizations in summary.items():
            summary_report.append(f"\n--- {project.upper()} ---")
            for organization, info in organizations.items():
                summary_report.append(f"{organization}: {info['status']}")
                if info["files"]:
                    for filename, date in info["files"]:
                        summary_report.append(f"  - {filename} (uploaded on {date})")
                else:
                    summary_report.append("  No files found.")
    
    # Join the summary lines into a single string
    return "\n".join(summary_report)

# Run the summary function and store the result
report = create_summary()
print(report)