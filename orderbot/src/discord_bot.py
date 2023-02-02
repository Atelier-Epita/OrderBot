import logging
import discord
from .github_bot import GithubBot
import os


class DiscordBot(discord.Client):
    COMMANDS = {
        "!ping": lambda message, args: message.channel.send("Pong!"),
    }

    def __init__(self, token, github_bot: GithubBot):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.token = token
        self.github_bot = github_bot

    def run(self):
        super().run(self.token)

    def repr_message(self, message):
        return f"Message: {message.content} from {message.author} in {message.channel} at {message.created_at} with {message.reactions} reactions"

    async def create_thread_issue(self, message):
        # create a new issue on github
        issue = await self.github_bot.create_issue(f"{message.channel.name} - {message.author.display_name}", f"[{message.author}]" + message.content, os.getenv("GITHUB_PROJECT_NUMBER"))

        # create thread
        issue_number = issue["createIssue"]["issue"]["number"]
        thread = await message.create_thread(name=f"{message.author.display_name} #{issue.number}")
        # await thread.send("Issue created, please wait for a staff member to respond")

        logging.info(f"Created issue #{issue_number} for {message.author} in {message.channel.name}")

    async def on_ready(self, *args, **kwargs):
        logging.info(f"We have logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        logging.debug(self.repr_message(message))

        # avoid bot replying to itself
        if message.author == self.user:
            return

        # only reply to authorized users (to be defined later)
        if "Bureau" not in [r.name for r in message.author.roles]:
            return

        # check if the message is a command
        if message.content.startswith("!"):
            # split the message into command and arguments
            command = message.content.split(" ")[0]
            args = message.content.split(" ")[1:]
            channel = message.channel.name

            # check if the command is valid
            if command in DiscordBot.COMMANDS:
                # execute the command
                await DiscordBot.COMMANDS[command](message, args)

            else:
                # send an error message
                await message.channel.send("Invalid command")

        channel = message.channel.name
        if "#" in channel:
            issue_number = int(channel.split("#")[-1])
            await self.github_bot.add_issue_comment(issue_number, f"[{message.author}] - {message.content}")

    # on reaction
    async def on_message_edit(self, before, after):
        logging.debug(f"Message edited: {before} -> {after}")
        await self.on_message(after)

    async def on_raw_reaction_add(self, payload):
        reaction = payload.emoji
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.get_user(payload.user_id)

        if payload.emoji.name == "🧵":
            await self.create_thread_issue(message)
