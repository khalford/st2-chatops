from typing import Union, List, Dict
import json
import requests

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