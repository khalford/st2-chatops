import requests
from typing import List, Dict
import sys
import json
from st2common.runners.base_action import Action
from slack_sdk import WebClient
from get_messages import GetMessages


class PostPRReminder(Action):

    def __init__(self):
        self.get_messages = GetMessages()
        self.client = WebClient(token=self.get_messages.secrets["SLACK_TOKEN"])

    def run(self, channel: str) -> None:
        prs = self.get_messages.get_raw_prs()
        self.post_to_slack(self.get_messages.secrets["SLACK_TOKEN"], prs, channel)

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


    # def send_messages(self, prs: List[str]):
    #     for pr in prs:
    #         message = f"{pr['user']['login']},{pr['html_url']}\n"
    #         response = client.chat_postMessage(
    #             channel=self.channel,
    #             text=message,
    #             unfurl_links=False,
    #             thread_ts=reminder.data["message"]["ts"],
    #         )
    #         assert response["ok"]


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
