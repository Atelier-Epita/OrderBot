import logging
import discord


class DiscordBot(discord.Client):
    COMMANDS = {
        "!ping": lambda message, args: message.channel.send("Pong!"),
    }

    def __init__(self, token):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.token = token

    def run(self):
        super().run(self.token)

    async def on_ready():
        logging.debug(f"We have logged in as {client.user}")

    async def on_message(message):
        # avoid bot replying to itself
        if message.author == client.user:
            return

        # check if the message is a command
        if message.content.startswith("!"):
            # split the message into command and arguments
            command = message.content.split(" ")[0]
            args = message.content.split(" ")[1:]
            channel = message.channel.name

            # check if the command is valid
            if command in COMMANDS:
                # execute the command
                await COMMANDS[command](message, args)

            else:
                # send an error message
                await message.channel.send("Invalid command")
