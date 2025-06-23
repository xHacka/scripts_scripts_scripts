from datetime import datetime
from pathlib import Path
from jira import JIRA
import csv
import os

class JiraConfig:
    '''Configuration class for Jira settings.'''
    URL = os.getenv('JIRA_URL')
    USER = os.getenv('JIRA_TOKEN_OWNER')
    TOKEN = os.getenv('JIRA_TOKEN')
    JQL = 'project = "PROJECT_NAME" AND status = Done AND labels = Auto-close-ticket AND created >= startOfDay(-1) AND created <= endOfDay(-1) ORDER BY priority DESC, created DESC'

jira = JIRA(server=JiraConfig.URL, basic_auth=(JiraConfig.USER, JiraConfig.TOKEN))
issues = jira.search_issues(JiraConfig.JQL, maxResults=-1)

REASONS_SUMMARY = {
    'Reason 1': 'Reason 1 Comment',
    'Reason 2': 'Reason 2 Comment',
}
REASONS_COMMENTS = {
    'Reason 1': 'Reason 1 Comment',
}
REASONS_LABELS = {
    'Reason 1': 'Reason 1 Comment',
}

def get_reason(issue):
    summary = issue.fields.summary
    for reason, label in REASONS_SUMMARY.items():
        if reason in summary:
            return label
        
    comments = issue.fields.comment.comments
    for comment in comments:
        for reason, label in REASONS_COMMENTS.items():
            if reason in comment.body:
                return label

    component = issue.fields.components[0].name
    if component != 'Other':
        return component

    labels = issue.fields.labels
    if 'Informational' in labels:
        return 'Informational'

    return 'REVIEW REQUIRED'

review_day = datetime.now().strftime('%m_%d_%Y')
output = Path(f'Auto-closed tickets review {review_day}.csv')
headers = ['Date','Ticket ID','Ticket URL','Ticket Summary','Auto-Close Reason','Review Status','Reviewer','Review Comments','Action Taken','Reopen Reason','Task Ticket']

# with open(output, mode='w', newline='', encoding='cp1255') as file:
with open(output, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    review_day = datetime.now().strftime('%m/%d/%Y')

    for issue in issues:
        issue_url = f'{JiraConfig.URL}/browse/{issue.key}'
        summary = issue.fields.summary

        reason = get_reason(issue)
        status = 'Pending Review' if reason == 'REVIEW REQUIRED' else 'Reviewed'
        action = '' if reason == 'REVIEW REQUIRED' else 'Legitimate auto-closure'

        writer.writerow([review_day, issue.key, issue_url, summary, reason, status, 'Jira User', '', action, 'N/A', ''])

    print(f'Reviewed {len(issues)} tickets. Output saved to \n& "{output}".')
