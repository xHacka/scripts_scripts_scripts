from jira import JIRA
from tabulate import tabulate
from time import sleep, time
import argparse 
import logging
import json 
import random
import os
import re 

class JiraConfig:
    '''Configuration class for Jira settings.'''
    URL = os.getenv('JIRA_URL')
    USER = os.getenv('JIRA_TOKEN_OWNER')
    TOKEN = os.getenv('JIRA_TOKEN')
    COMPONENT = 'Benign Positive - Suspicious but expected'
    TIME_SPENT = 300 # 5 minutes
    STORY_POINTS = 0.005
    STORY_POINTS_FIELD = 'customfield_10024'

class JiraProcessor:
    """A class for processing Jira tickets."""

    def __init__(self):
        """Initializes the JiraProcessor with a JiraConfig instance."""
        self.jira = self._connect_to_jira()
 
    def _connect_to_jira(self):
        """Connects to Jira using environment variables."""
        try:
            return JIRA(server=JiraConfig.URL, basic_auth=(JiraConfig.USER, JiraConfig.TOKEN))
        except Exception as e:
            logging.error(f'Failed to connect to Jira: {e}')
            raise

    def get_issue(self, ticket_identifier):
        """Retrieves a Jira issue by key or URL."""
        ticket_key = ticket_identifier.split('/')[-1] if ticket_identifier.startswith('http') else ticket_identifier

        try:
            issue = self.jira.issue(ticket_key)
            logging.info(f'Retrieved issue: {ticket_key}')
            return issue
        except Exception as e:
            logging.error(f'Failed to retrieve issue {ticket_identifier}: {e}')
            raise

    def assign_issue(self, issue, user):
        """Assigns a Jira issue to a user."""
        try:
            self.jira.assign_issue(issue, user)
            logging.info(f'Assigned ticket {issue.key} to {user}')
        except Exception as e:
            logging.error(f'Failed to assign ticket {issue.key} to {user}: {e}')
            raise

    def transition_issue(self, issue, transition_name):
        """Transitions a Jira issue to a specified status."""
        transitions = {'To Do': 11, 'In Progress': 21, 'Done': 31, 'Backlog': 41, 'Canceled': 101, 'Waiting For Deployment': 111, 'Blocked': 121}

        try:
            transition = transitions.get(transition_name)
            if transition:
                self.jira.transition_issue(issue, transition)
                logging.info(f'Moved ticket {issue.key} to {transition_name} [{transition}]')
            else:
                logging.warning(f'Transition "{transition_name}" not found for ticket {issue.key}')
        except Exception as e:
             logging.error(f'Failed to transition ticket {issue.key} to {transition_name}: {e}')
             raise

    def set_story_points(self, issue, story_points):
        """Sets the story points of a Jira issue."""
        try:
            issue.update(fields={JiraConfig.STORY_POINTS_FIELD: story_points})
            logging.info(f'Set story points of {issue.key} to {story_points}')
        except Exception as e:
            logging.error(f'Failed to set story points for ticket {issue.key}: {e}')
            raise

    def set_component(self, issue, component):
        """Sets the component of a Jira issue."""
        try:
            issue.update(fields={'components': [{'name': component}]})
            logging.info(f'Set component of {issue.key} to {component}')
        except Exception as e:
            logging.error(f'Failed to set component for ticket {issue.key}: {e}')
            raise

    def set_parent(self, issue, parent_key):
        """Sets the parent of a Jira issue."""
        try:
            issue.update(fields={'parent': {'key': parent_key}})
            logging.info(f'Set parent of {issue.key} to {parent_key}')
        except Exception as e:
            logging.error(f'Failed to set parent for ticket {issue.key}: {e}')
            raise

    def add_comment(self, issue, comment):
        """Adds a comment to a Jira issue."""
        try:
            self.jira.add_comment(issue, comment)
            logging.info(f'Added comment to ticket {issue.key}')
        except Exception as e:
            logging.error(f'Failed to add comment to ticket {issue.key}: {e}')
            raise

    def add_worklog(self, issue, time_spent_seconds, comment):
        """Adds a worklog entry to a Jira issue."""
        try:
            self.jira.add_worklog(issue, timeSpentSeconds=time_spent_seconds, comment=comment)
            logging.info(f"Added worklog to ticket {issue.key}: {time_spent_seconds} seconds")
        except Exception as e:
            logging.error(f"Failed to add worklog to ticket {issue.key}: {e}")
            raise

    def process_issue(self, issue, comment, user, component, time, story, parent=None):
        """Processes a Jira ticket."""
        try:
            transition_name = issue.fields.status.name
            logging.info(f'Processing issue {issue.key} with current status: {transition_name}')
    
            # Assign the parent issue if provided
            if parent:
                self.set_parent(issue, parent)

            # Assign the issue to a user
            self.assign_issue(issue, user)
            
            # Transition the issue to Backlog
            if transition_name != 'Backlog':
                self.transition_issue(issue, 'Backlog') 

            # Set the story points
            self.set_story_points(issue, story)

            # Transition the issue to In Progress with delay~
            wait_time = random.uniform(5, 10)
            logging.info(f'Waiting for {wait_time:.5f} seconds...')
            wait_progress_bar(wait_time)
            self.transition_issue(issue, 'In Progress') 

            # Transition the issue to Done with delay~
            wait_time = random.uniform(time - 10, time + 10)
            logging.info(f'Waiting for {wait_time} seconds...')
            wait_progress_bar(wait_time, bar_length=50)

            self.set_component(issue, component)
            self.add_worklog(issue, time, comment)
            self.add_comment(issue, comment)
            self.transition_issue(issue, 'Done')
        except Exception as e:
            logging.error(f'Error processing issue: {e}')


def time_to_seconds(time_str):
    """
    Converts a time string (e.g., "1m", "2h", "30s", "1.5h") to seconds.
    Defaults to seconds if no unit is provided.

    Args:
        time_str: The time string to convert.

    Returns:
        The time in seconds as a float, or None if the input is invalid.
    """
    time_str = time_str.lower().strip()

    match = re.match(r"([\d.]+)([smh]?)", time_str)
    if not match:
        raise Exception("Invalid time unit, must be one of 's', 'm', or 'h'.")

    value, unit = match.groups()
    value = int(value)

    if not unit or unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:
        raise Exception("Invalid time unit, must be one of 's', 'm', or 'h'.")


def validate_request(parser, args):
    table = []
    for action in parser._actions:
        if action.help == argparse.SUPPRESS:
            continue
        if action.dest == 'help':
            continue

        table.append([action.dest.replace('_',' ').title(), args.get(action.dest), action.help])

    print(tabulate(table, headers=["Argument", "Value", "Help"], tablefmt="rounded_grid"))
    if input('Proceed? [y/N]: ').lower() not in ('y', 'yes', 'uwu', '1'):
        exit(1)


def delete_null(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            processed_value = delete_null(value)
            if processed_value is not None:
                new_obj[key] = processed_value

        return new_obj if new_obj else None
    elif isinstance(obj, list):
        new_list = []
        for item in obj:
            processed_item = delete_null(item)
            if processed_item is not None:
                new_list.append(processed_item)

        return new_list if new_list else None
    else:
        return obj


def wait_progress_bar(wait_time: float, bar_length: int = 20) -> float:
    start_time = time()
    while time() - start_time < wait_time:
        progress = (time() - start_time) / wait_time
        filled_length = int(bar_length * progress)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        print(f"\rWaiting... [{bar}] {progress * 100:.1f}%", end="", flush=True)
        sleep(1/3)  # Update progress every X seconds

    print("\r", end="", flush=True) # Clear the progress bar.
    return wait_time


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='Process Jira tickets.')
    parser.add_argument('ticket_identifier', help='Jira ticket key or URL.')
    parser.add_argument('comment', help='Comment to add to the ticket.')
    parser.add_argument('-u', '--user', help='Jira username to assign the ticket to.', default=JiraConfig.USER)
    parser.add_argument('-c', '--component', help='Jira component to set.', default=JiraConfig.COMPONENT)
    parser.add_argument('-t', '--time', help='Time spent in seconds.', default=JiraConfig.TIME_SPENT)
    parser.add_argument('-s', '--story', help='Story points assigned.', default=JiraConfig.STORY_POINTS)
    parser.add_argument('-d', '--dry', help='Dry run, only show ticket data.', default=False, action='store_true')
    parser.add_argument('-p', '--parent', help='Parent ticket key to set for the issue.', default=None)

    args = parser.parse_args()

    if isinstance(args.time, str): 
        args.time = time_to_seconds(args.time)

    if not args.dry:
        validate_request(parser, args.__dict__)

    processor = JiraProcessor()

    issue = processor.get_issue(args.ticket_identifier)
    issue_json = delete_null(issue.raw)

    if args.dry:
        logging.info(f'Issue data:\n{json.dumps(issue_json, indent=2)}')
        with open('issue.json', 'w') as f:
            json.dump(issue_json, f, indent=2)
    else:
        logging.debug(f'Issue data:\n{json.dumps(issue_json, indent=2)}')
        processor.process_issue(issue, args.comment, args.user, args.component, args.time, args.story, args.parent)
