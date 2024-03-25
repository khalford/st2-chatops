import requests
from typing import List, Dict
import sys
import json
from st2common.runners.base_action import Action
from slack_sdk import WebClient


class GetMessages:

    def __init__(self):
        self.repos = self.get_repos()
        self.secrets = self.get_secrets()

    @staticmethod
    def get_repos() -> List[str]:
        with open("/etc/repos.csv", "r") as file:
            data = file.read()
            repos = data.split(".")
        return repos

    @staticmethod
    def get_secrets() -> Dict[str:str]:
        with open("/etc/st2_tokens.json", "r") as file:
            data = file.read()
            secrets = json.loads(data)
        return secrets

    def get_http_response_github(self, url: str) -> List[Dict]:
        headers = {'Authorization': 'token ' + self.secrets['GITHUB_TOKEN']}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_raw_prs(self) -> List[List[Dict]]:
        responses = []
        for repo in self.repos:
            url = f"https://api.github.com/repos/stfc/{repo}/pulls"
            response = self.get_http_response_github(url)
            responses.append(response)
        return responses


class PostPRReminder(Action, GetMessages):

    def __init__(self):
        super().__init__()
        self.client = WebClient(token=self.secrets["SLACK_TOKEN"])

    def run(self, channel: str) -> None:
        prs = self.get_raw_prs()
        self.post_to_slack(self.secrets["SLACK_TOKEN"], prs, channel)

    def post_to_slack(self, token: str, prs: List[str], channel: str):
        reminder_message = self.post_reminder(channel)
        self.iter_prs(prs, reminder_message)


    def iter_prs(self, prs: List[str], reminder_message) -> None:
        channel = reminder_message.data["message"]["channel"]
        thread_ts = reminder_message.data["message"]["ts"]
        for pr in prs:
            message = f"{pr['user']['login']},{['html_url']}\n"
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                unfurl_links=False,
                thread_ts=thread_ts,
            )
            assert response["ok"]

    def post_reminder(self, channel: str):
        reminder = self.client.chat_postMessage(
            channel=channel,
            text="Here are the outstanding PRs as of today :",
        )
        return reminder


    def send_messages(self, prs: List[str]):
        for pr in prs:
            message = f"{pr['user']['login']},{pr['html_url']}\n"
            response = client.chat_postMessage(
                channel=self.channel,
                text=message,
                unfurl_links=False,
                thread_ts=reminder.data["message"]["ts"],
            )
            assert response["ok"]


if __name__ == '__main__':
    PostPRReminder().run("#chatops")



#
#
# def go():
#     TOKEN = ""
#     URL = "https://api.github.com/repos/stfc/st2-cloud-pack/pulls"
#     repos = [
#         "cloud-deployed-apps",
#         "st2-cloud-pack",
#         "cloud-grafana-dashboards",
#         "cloud-pe-jupyterhub",
#         "cloud-ops-tools",
#         "cloud-docker-images",
#         "cloud-capi-values",
#         "cloud-image-builders",
#         "cloud-docs",
#         "cloud-openstack-horizon",
#         "ansible-harbor",
#         "terraform-openstack",
#         "cloud-rundeck-jobs",
#         "openstack-guide",
#         "ansible-jupyter",
#         "SCD-Openstack-Utils",
#     ]
#     get_pr(TOKEN, repos)

# for arg in sys.argv:
#     if arg.startswith("--parameters"):
#         sys.stdout.write(arg+"\n")
#         dict = arg.split("=")[1]
#         sys.stdout.write(str(dict)+"\n")
#         dict = json.loads(dict)
#         sys.stdout.write(str(dict)+"\n")
#         channel = "#"+dict["chanel"]
#         sys.stdout.write(channel+"\n")
# sys.stdout.write(channel)
# client = WebClient(token=)
# reminder = client.chat_postMessage(
#     channel=channel,
#     text="Here are the outstanding PRs as of today :",
#     )
# go()
