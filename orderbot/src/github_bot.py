import json
import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


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

    async def fetch_issue(self, repo_name, title):
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

        return issue

    async def add_issue_comment(self):
        # TODO test this
        try:
            issue_id = self.fetch_issue(self.repo, self.title)["organization"]["repository"]["issue"]["id"]
        except KeyError:
            logging.error("Issue not found")
            return

        query = gql(
            """
            mutation ($body: String!, $subjectId: ID!) {
                addComment(input: {body: $body, subjectId: $subjectId}) {
                    clientMutationId
                }
            }
            """
        )

        response = await self.client.execute_async(
            query,
            variable_values={
                "body": self.body,
                "subjectId": issue_id,
            },
        )

        return response