from typing import List, Dict, Union
import json
import requests
from st2common.runners.base_action import Action
from slack_sdk import WebClient


class PRReminder(Action):
    """
    This class is the entry point for StackStorm and handles the Slack posting.
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.get_messages = GetGitHubPRs()
        self.client = WebClient(token=self.get_messages.secrets["SLACK_TOKEN"])
        self.slack_ids = {

        }

    def run(self) -> None:
        """
        This method is the entry point for StackStorm.
        """
        prs = self.get_messages.get_prs()
        self.post_to_slack(prs)

    def post_to_slack(self, prs: List[Dict]) -> None:
        """
        This method calls the functions to post the reminder message and subsequent PR messages.
        :param prs: A list of PRs from GitHub
        """
        reminder_message = self.post_reminder_message()
        self.post_thread_messages(prs, reminder_message)

    def post_reminder_message(self) -> WebClient.chat_postMessage:
        """
        This method posts the main reminder message to start the thread if PR notifications.
        :return: The reminder message return object
        """
        reminder = self.client.chat_postMessage(
            channel="pull-requests",
            text="Here are the outstanding PRs as of today :",
        )
        return reminder

    def post_thread_messages(
        self, prs: List[Dict], reminder_message: WebClient.chat_postMessage
    ) -> None:
        """
        This method posts each individual PR reminder message to the thread mentioning each user.
        :param prs: A list of PRs from GitHub
        :param reminder_message: The reminder message object
        """
        channel = reminder_message.data["channel"]
        thread_ts = reminder_message.data["ts"]
        for pr in prs:
            user = self.get_username(pr["user"]["login"])
            message = f"<@{user}>: {pr['html_url']}"
            response = self.client.chat_postMessage(
                channel=channel, text=message, thread_ts=thread_ts, unfurl_links=False
            )
            assert response["ok"]

    def get_username(self, user: str) -> str:
        """
        This method checks if we have a Slack id for the GitHub user and returns it.
        :param user: GitHub username to check for
        :return: Slack ID or GitHub username
        """
        if user in self.slack_ids:
            return self.slack_ids[user]
        return user


class GetGitHubPRs:
    """
    This class handles getting the PRs from the GitHub Rest API.
    """

    def __init__(self):
        self.repos = self.get_repos()
        self.secrets = self.get_secrets()

    @staticmethod
    def get_repos() -> List[str]:
        with open("/etc/repos.csv", "r", encoding="utf-8") as file:
            data = file.read()
            repos = data.split(",")
        return repos

    @staticmethod
    def get_secrets() -> Dict[str, str]:
        with open("/etc/st2_tokens.json", "r", encoding="utf-8") as file:
            data = file.read()
            secrets = json.loads(data)
        return secrets

    def get_http_response_github(self, url: str) -> List[Dict]:
        """
        This method sends a HTTP request to the GitHub Rest API endpoint and returns all open PRs from that repository.
        :param url: The URL to make the request to
        :return: The response in JSON form
        """
        headers = {"Authorization": "token " + self.secrets["GITHUB_TOKEN"]}
        response = requests.get(url, headers=headers, timeout=60)
        return response.json()

    def get_prs(self) -> List[Dict]:
        """
        This method starts a request for each repository and returns a list of those PRs.
        :return: A list of PRs
        """
        responses = []
        for repo in self.repos:
            url = f"https://api.github.com/repos/stfc/{repo}/pulls"
            response = self.get_http_response_github(url)
            responses += self.expand_prs(response)
        return responses

    @staticmethod
    def expand_prs(response: Union[List[Dict], List[List[Dict]]]) -> List[Dict]:
        """
        This method checks if the response returned a list of PRs (where a single repo has multiple PRs)
        or if a response returned a single PR (where a single repo has one PR). Then returns them in a list.
        :param response: GitHub's response of a list of PRs or single PR
        :return: A list of PRs
        """
        if isinstance(response, dict) and len(response) != 2:
            return [response]
        elif isinstance(response, list):
            return [pr for pr in response if len(pr) != 2]
        else:
            raise Exception(f"An unexpected HTTP response was found: {response}\n")
