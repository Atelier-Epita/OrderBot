import json
import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

logging.getLogger("gql").setLevel(logging.WARNING)


class GithubBot():
    def __init__(self, org, repo, token):
        self.org = org
        self.repo = repo
        self.column_ids = {}
        transport = AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={
                "Authorization": f"token {token}",
            },
        )
        self.client = Client(transport=transport,
                             fetch_schema_from_transport=True)

    async def fetch_projectv2(self, number:int):
        # fetch the project in the organization
        query = gql(
            """
            query ($login: String!, $number: Int!) {
                organization(login: $login) {
                    projectV2(number: $number) {
                        id
                    }
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "login": self.org,
                "number": number,
            },
        )

        logging.info(f"Projects: {response}")

    async def fetch_projectv2_fields(self, number):
        # fetch the project in the organization and its fields and custom fields
        query = gql(
            """
            query ($login: String!, $number: Int!) {
                organization(login: $login) {
                    projectV2(number: $number) {
                        id
                        number
                        fields(first: 100) {
                            nodes { ... on ProjectV2FieldCommon {
                                name
                                dataType
                                databaseId
                                }
                            }
                        }
                    }
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "login": self.org,
                "number": int(number),
            },
        )
        return response

    async def fetch_repo(self, name):
        # fetch the repository in the organization
        query = gql(
            """
            query ($login: String!, $name: String!) {
                organization(login: $login) {
                    repository(name: $name) {
                        id
                    }
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "login": self.org,
                "name": name,
            },
        )
        return response

    async def fetch_issue_by_name(self, repo_name, title):
        # fetch the issue in the repository
        query = gql(
            """
            query ($login: String!, $name: String!, $title: String!) {
                organization(login: $login) {
                    repository(name: $name) {
                        issue(title: $title) {
                            id
                        }
                    }
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "login": self.org,
                "name": repo_name,
                "title": title,
            },
        )
        return response

    async def fetch_issue_by_number(self, repo_name, number):
        # fetch the issue in the repository
        query = gql(
            """
            query ($login: String!, $name: String!, $number: Int!) {
                organization(login: $login) {
                    repository(name: $name) {
                        issue(number: $number) {
                            id
                        }
                    }
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "login": self.org,
                "name": repo_name,
                "number": int(number),
            },
        )
        return response

    async def create_issue(self, title, body, project_number):
        project = await self.fetch_projectv2_fields(project_number)
        repo = await self.fetch_repo(self.repo)


        # create the issue
        query = gql(
            """
            mutation ($title: String!, $body: String!, $repositoryId: ID!) {
                createIssue(input: {title: $title, body: $body, repositoryId: $repositoryId}) {
                    issue {
                        id
                        number
                    }
                }
            }
            """
        )

        issue = await self.client.execute_async(
            query,
            variable_values={
                "title": title,
                "body": body,
                "repositoryId": repo["organization"]["repository"]["id"],
            }
        )

        # add the issue to the project
        query = gql(
            """
            mutation ($contentId: ID!, $projectId: ID!) {
                addProjectV2ItemById(input: {contentId: $contentId, projectId: $projectId}) {
                    clientMutationId
                }
            }
            """
        )

        # create the card associated with the issue
        card = await self.client.execute_async(
            query,
            variable_values={
                "contentId": issue["createIssue"]["issue"]["id"],
                "projectId": project["organization"]["projectV2"]["id"],
            }
        )

        logging.info(f"Created issue {issue['createIssue']['issue']['number']}")

        return issue

    async def add_issue_comment(self, number, body):
        try:
            issue = await self.fetch_issue_by_number(self.repo, number)
            issue_id = issue["organization"]["repository"]["issue"]["id"]
        except KeyError:
            logging.error(f"Issue {number} not found")
            return

        # add the comment to the issue
        query = gql(
            """
            mutation ($body: String!, $subjectId: ID!) {
                addComment(input: {body: $body, subjectId: $subjectId}) {
                    clientMutationId
                }
            }
            """
        )

        comment = await self.client.execute_async(
            query,
            variable_values={
                "body": body,
                "subjectId": issue_id,
            }
        )

        logging.info(f"Added Github comment: {body} in issue {number}")
        return comment

    async def close_issue(self, number):
        try:
            issue = await self.fetch_issue_by_number(self.repo, number)
            issue_id = issue["organization"]["repository"]["issue"]["id"]
        except KeyError:
            logging.error(f"Issue {number} not found")
            return

        # close the issue
        query = gql(
            """
            mutation ($issueId: ID!) {
                closeIssue(input: {issueId: $issueId}) {
                    clientMutationId
                }
            }
            """
        )

        close = await self.client.execute_async(
            query,
            variable_values={
                "issueId": issue_id,
            }
        )

        logging.info(f"Closed issue {number}")
        return close