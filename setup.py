from distutils.core import setup
from setuptools import find_packages

setup(
    name="termichat",
    packages=["termichat"],
    version="0.0",
    license="MIT",
    description="Use ChatGPT in terminal",
    author="GuoDCZ",
    author_email="guodcz@gmail.com",
    url="https://github.com/GuoDCZ/termichat",
    download_url="", # FIXME
    keywords=[
        "chat", "chatbot", "gpt", "gpt-3", "openai", "terminal", "cli"
    ],
    install_requires=find_packages(),
    entry_points={
        "console_scripts": [
            "termichat=termichat.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
