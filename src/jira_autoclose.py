from datetime import datetime
from jira import JIRA
import csv
import os

class JiraConfig:
    '''Configuration class for Jira settings.'''
    URL = os.getenv('JIRA_URL')
    USER = os.getenv('JIRA_TOKEN_OWNER')
    TOKEN = os.getenv('JIRA_TOKEN')
    JQL = 'project = "PROJECT_NAME" AND status = Done AND labels = Auto-close-ticket AND created >= startOfDay(-1) AND created <= endOfDay(-1) ORDER BY priority DESC, created DESC'

OUTPUT = 'auto-close.csv'
REASON_INFORMATIONAL = [
    'Reason 1',
    'Reason 2'
]
REASON_INTERNAL_PHISHING = [
    'Reason 1',
    'Reason 2'
]

jira = JIRA(server=JiraConfig.URL, basic_auth=(JiraConfig.USER, JiraConfig.TOKEN))
issues = jira.search_issues(JiraConfig.JQL, maxResults=-1)

review_day = datetime.now().strftime('%m/%d/%Y')

def get_reason(summary):
    reason = 'REVIEW REQUIRED'
    if any(substring in summary for substring in REASON_INFORMATIONAL):
        reason = 'Informational'
    elif any(substring in summary for substring in REASON_INTERNAL_PHISHING):
        reason = 'Internal Phishing Exercise'

    return reason

headers = ['Date','Ticket ID','Ticket URL','Ticket Summary','Auto-Close Reason','Review Status','Reviewer','Review Comments','Action Taken','Reopen Reason','Task Ticket']
with open(OUTPUT, mode='w', newline='', encoding='cp1255') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    for issue in issues:
        issue_url = f'{JiraConfig.URL}/browse/{issue.key}'
        summary = issue.fields.summary

        reason = get_reason(summary)
        status = 'Pending Review' if reason == 'REVIEW REQUIRED' else 'Reviewed'
        action = '' if reason == 'REVIEW REQUIRED' else 'Legitimate auto-closure'

        writer.writerow([review_day, issue.key, issue_url, summary, reason, status, 'USERNAME', '', action, 'N/A', ''])

    print(f'Reviewed {len(issues)} tickets. Output saved to {OUTPUT}.')

