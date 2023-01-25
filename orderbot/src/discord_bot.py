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

    def repr_message(self, message):
        return f"Message: {message.content} from {message.author} in {message.channel} at {message.created_at} with {message.reactions} reactions"
    
    def run(self):
        super().run(self.token)

    async def create_thread_issue(self, message):
        # create a new issue on github
        await self.github_bot.create_issue(f"{message.channel.name} - {message.author}", message.content, os.getenv("GITHUB_PROJECT_NUMBER"))

        # create thread
        thread = await message.create_thread(name=message.author.display_name)
        await thread.send("Issue created, please wait for a staff member to respond")

    async def on_ready(self, *args, **kwargs):
        logging.debug(f"We have logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        logging.debug(self.repr_message(message))

        # avoid bot replying to itself
        if message.author == self.user:
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

    # on reaction
    async def on_message_edit(self, before, after):
        logging.debug(f"Message edited: {before} -> {after}")
        await self.on_message(after)

    async def on_raw_reaction_add(self, payload):
        logging.debug(f"Raw reaction added: {payload}")

        reaction = payload.emoji
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.get_user(payload.user_id)

        print(f"Reaction: {reaction} from {user} in {channel} at {message.created_at} with {message.reactions} reactions")

        if payload.emoji.name == "🧵":
            await self.create_thread_issue(message)
