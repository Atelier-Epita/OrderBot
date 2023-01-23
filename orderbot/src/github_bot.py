import json
import requests
import logging

class GithubBot():
    def __init__(self, owner, repo, project_id, token):
        self.owner = owner
        self.repo = repo
        self.project_id = project_id 
        self.__headers = {"Authorization": f"Token {token}"}

    def post(self, url, data):
        ret = requests.post(url, json=data, headers=self.__headers)
        if ret.status_code != 201:
            logging.error(f"{ret.status_code} {ret.text}")
        return ret

    def get(self, url):
        ret = requests.get(url, headers=self.__headers)
        if ret.status_code != 200:
            logging.error(f"{ret.status_code} {ret.text}")
        return ret

    def get_column_id(self, column_name):
        url = f"https://api.github.com/projects/{self.project_id}/columns"
        response = self.get(url)
        columns = response.json()
        for column in columns:
            if column["name"] == column_name:
                return column["id"]
        logging.error(f"Column {column_name} not found")

    def create_issue(self, title, body, template, column_name, fields: dict):
        # Get the column id
        column_id = self.get_column_id(column_name)

        # create the issue using a template
        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        data = {"title": issue_title, "body": issue_body, "template": template}.update(fields)
        response = self.post(issue_url, data)
        issue_number = response.json()["number"]

        # Add the issue to the project column
        card_url = f"https://api.github.com/projects/columns/{column_id}/cards"
        card_data = {"content_id": issue_number, "content_type": "Issue"}
        response = self.post(card_url, card_data)

        logging.info(f"Issue {issue_number} created and inserted in column {column_id}")
