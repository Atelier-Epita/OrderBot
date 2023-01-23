from setuptools import setup

setup(
    name='orderbot',
    version='0.1',
    description="Discord / Github bot to automate issue creation when a new order is placed",
    author="atelier-epita",
    packages=["orderbot"],
    install_requires=[
        "discord.py",
        "requests",
        "python-dotenv",
    ],
    extras_require={
        "dev": ["pytest", "black"],
    },
)
