from typing import List, Dict
from st2common.runners.base_action import Action
from slack_sdk import WebClient
from temp import GetGitHubPRs

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



