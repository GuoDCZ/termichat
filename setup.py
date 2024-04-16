from distutils.core import setup

setup(
    name="termichat",
    packages=["termichat", "termichat.lib"],
    version="0.0.5",
    license="MIT",
    description="Use ChatGPT in terminal",
    author="GuoDCZ",
    author_email="guodcz@gmail.com",
    url="https://github.com/GuoDCZ/termichat",
    download_url="", # FIXME
    keywords=[
        "chat", "chatbot", "gpt", "gpt-3", "openai", "terminal", "cli"
    ],
    install_requires=[
        "openai==0.27.0",
    ],
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
