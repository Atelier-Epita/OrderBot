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

### add the service

```bash
systemctl enable orderbot.service
systemctl start orderbot.service
```
