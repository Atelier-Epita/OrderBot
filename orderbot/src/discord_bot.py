import logging
import discord
from .github_bot import GithubBot
import os


class DiscordBot(discord.Client):
    COMMANDS = {
        "!ping": lambda self, message: self.on_ping(message),
        "!close": lambda self, message: self.on_close(message),
        "!help": lambda self, message: self.on_help(message),
    }

    def __init__(self, token, github_bot: GithubBot):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.token = token
        self.github_bot = github_bot

    def run(self):
        super().run(self.token)

    def repr_message(self, message: discord.Message):
        # remove emojis
        return f"Message: {message.content} from {message.author} in {message.channel} at {message.created_at} with {message.reactions} reactions".encode("ascii", "ignore").decode()

    async def on_ping(self, message: discord.Message):
        message.channel.send("Pong!")

    async def on_close(self, message: discord.Message):
        thread = message.channel
        assert type(thread) == discord.Thread

        # try to get issue number from thread name
        issue_number = thread.name.split("#")[-1]
        if issue_number.isnumeric():
            issue_number = int(issue_number)
            await thread.send(f"Closing issue #{issue_number}")
            await self.github_bot.add_issue_comment(issue_number, f"Issue closed by {message.author}")
            await self.github_bot.close_issue(issue_number)

        else:
            await thread.send("Could not find issue number in thread name")
            logging.error(f"Could not find issue number in thread name {thread.name}")

        # archive thread
        await thread.send("Closing thread")
        await thread.edit(archived=True, locked=True)

    async def on_help(self, message):
        message.channel.send("Commands: " + ", ".join(self.COMMANDS.keys()))

    async def on_ready(self, *args, **kwargs):
        logging.info(f"We have logged in as {self.user}")

    async def create_thread_issue(self, message: discord.Message):
        # create a new issue on github
        issue = await self.github_bot.create_issue(f"{message.channel.name} - {message.author.display_name}", f"[{message.author}]" + message.content, os.getenv("GITHUB_PROJECT_NUMBER"))

        # create thread
        issue_number = issue["createIssue"]["issue"]["number"]
        thread = await message.create_thread(name=f"{message.author.display_name} #{issue.number}")

        logging.info(
            f"Created issue #{issue_number} for {message.author} in {message.channel.name}")

    async def on_message(self, message: discord.Message):
        logging.debug(self.repr_message(message))

        # avoid bot replying to itself
        if message.author == self.user:
            return

        channel_name = message.channel.name

        # check if the message is a command
        if message.content.startswith("!"):

            # only reply to authorized users (to be defined later)
            if "Bureau" not in [r.name for r in message.author.roles]:
                await message.channel.send("You are not authorized to use this command")
                return

            # split the message into command and arguments
            command = message.content.split(" ")[0]
            args = message.content.split(" ")[1:]

            # check if the command is valid
            if command in DiscordBot.COMMANDS:
                # execute the command
                await DiscordBot.COMMANDS[command](self, message, *args)

            else:
                # send an error message
                await message.channel.send("Invalid command")

        elif "#" in channel_name:
            issue_number = int(channel_name.split("#")[-1])
            await self.github_bot.add_issue_comment(issue_number, f"[{message.author}] - {message.content}")

    async def on_raw_reaction_add(self, payload):
        reaction = payload.emoji
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.get_user(payload.user_id)

        if payload.emoji.name == "🧵":
            await self.create_thread_issue(message)
