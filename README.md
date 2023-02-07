# OrderBot

Discord / Github bot to automate issue creation when a new order is placed

## Installation

### install dependancies

```bash
pip install -e .
```

### Add tokens to .env file

```bash
cp .env.example .env
```

Then add in your tokens for discord and github.
be carefull to not push those tokens to github.

### Deploy

<!-- TODO -->

## Usage

Once the bot is running, it will listen to discord channels.
When the :thread: reaction is added to a message, it will create a new thread on discord and a new issue on github. The issue number will be added to the thread name.
Then, when a message is sent in the thread, it will be added as a comment to the issue, this way, the whole conversation is kept in the issue.

*Note: for older threads (before the bot was deployed), you can rename the thread to add the issue number at the end of the name. Only the new messages will be added as comments to the issue.*

### Commands (only available to admins)

- `!ping` : pong.
- `!close` : close the thread and the issue.
- `!help` : display the available commands.
