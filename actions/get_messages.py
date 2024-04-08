import requests
from typing import List, Dict
import json

import sys
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
    def get_secrets() -> Dict[str,str]:
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
            sys.stdout.write(str(repo))
            url = f"https://api.github.com/repos/stfc/{repo}/pulls"
            response = self.get_http_response_github(url)
            responses.append(response)
        return responses