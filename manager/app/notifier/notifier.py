from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3

import json
import requests
from http import HTTPStatus

DB_PATH = '/data/monitor.db'
MANAGER_API_URL = "http://manager:8000"

labs_monitored = ['fleury', 'einstein',
                  'sabin' , 'hlagyn',
                  'hilab' , 'hpardini',
                  'dbmol', ]

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
    IN ('{"','".join(labs_monitored)}')
    ;
"""

# Function to check for organizations that haven't sent files recently
def create_summary():
    """
    Generates a summary of the file uploads for each project and organization.
    Built with help of https://app.slack.com/block-kit-builder.
    
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
        summary = {
            project: {lab: {"status": "🔴", "files": []} for lab in labs_monitored} 
            for project in projects
        }
        
        # Fill the summary based on query results
        for project, organization, filename, upload_ts in results:
            summary[project][organization]["status"] = "🟢"
            summary[project][organization]["files"].append(filename.split('__')[-1])

        # Generate the Slack report
        current_ts = datetime.now(tz= ZoneInfo("America/Sao_Paulo")).strftime('%d %b %Y - %H:%M')
        slack_summary_report = {
            'blocks':[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Arquivos enviados pelos laboratórios\nResumo Diário - {current_ts}"
                    }
                },
                {
                    "type": "divider"
                },
            ]
        }

        for project, organizations in summary.items():
            slack_summary_report['blocks'].append(
                {'type': 'header', 'text':{'type': 'plain_text', 'text': project.capitalize()}}
            )
            
            for organization, info in organizations.items():
                files = '\n'.join(info['files'])
                slack_summary_report['blocks'].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{info['status']} *{organization.upper()}* \n {files}"
                        }
                    }
                )

            slack_summary_report['blocks'].append(
                {'type': 'divider'}
            )  
    
    return slack_summary_report


if __name__ == "__main__":

    slack_summary = create_summary()
    slack_summary_json = json.dumps(slack_summary)
    slack_summary_json = str(slack_summary_json)

    try:
        response = requests.post(
            F"{MANAGER_API_URL}/notify/slack",
            params={
                "message": slack_summary_json
            }
        )
        response.raise_for_status()
        print(f"File summary successfully sent.")
    except Exception as e:
        print(f"Error sending daily summary. {e}")
        print(slack_summary_json)
