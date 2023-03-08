# ChatBot

This is a python based chatbot that allows interactions with different roles maintained in a JSON file. The chatbot utilizes OpenAI's *GPT-3.5-Turbo* model to generate responses to user inputs. The role can be selected as an argument at runtime. The chatbot can also generate responses based on the previous conversation if the user chooses to use the memorable argument at runtime. The model's response can be controlled by presence penalty and frequency penalty, which can be set by the user.

## Getting Started
The user needs the following to run this chatbot:
- `python 3.x`
- An OpenAI API key added to environment variables as `OPENAI_API_KEY`. You need to sign up for [OpenAI](https://beta.openai.com/signup/) to get an API key.

## Libraries
The following libraries are used in the program:
- argparse : It is used to parse the arguments passed at runtime.
- json : It is used to read the roles defined in the JSON file of the program.
- [openai](https://github.com/openai/openai-python) : It is used to access the OpenAI's GPT-3.5-Turbo model
- os : It is used to pause the system after running the program

## Usage
In the command line or terminal, navigate to the project directory and run the command `python chatbot.py [-h] [-r ROLE] [-m] [-t TEMPERATURE] [-p PRESENCE_PENALTY] [-f FREQUENCY_PENALTY] [request ...]`

### Architecture
The flow of the program is quite simple. The user inputs a message that is passed to the OpenAI model. The model returns a message as a response. If the memorable flag is present, the conversation is stored, and subsequent queries incorporate previous conversations.

### Arguments
The following optional arguments can be passed at runtime:
- `-r, --role` : Selects the role of the chatbot. It defaults to the `0th` index of the JSON file. Users can check all the roles by inspecting the `role_play_data.json` file.
- `-m, --memorable` : The chatbot remembers the previous dialogue, and a subsequent query takes into account previous dialogue
- `-t, --temperature` : Sampling temperature to use (between 0 and 2). Higher values make the output more random, while lower values make it more focused.
- `-p, --presence_penalty` : A number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text, increasing the model's likelihood to talk about new topics
- `-f, --frequency_penalty` : A number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text, decreasing the model's likelihood to repeat the same line verbatim.

### Example Run

* starts the chatbot with default arguments, starting from the role 0.
```sh
>>> python chatbot.py

@user> Hi! I would like to know about Harry Potter books!
@chatBot> Harry Potter is a famous book series written by British author J.K. Rowling...

```
* starts the chatbot with role named Harry, temperature 0.2, Presence penalty 1.5, and frequency penalty 0.5
```sh
>>> python chatbot.py -r Harry -t 0.2 -p 1.5 -f 0.5

@user> Who is your best friend?
@Harry> My best friend is Ron Weasley Hermione...
```

If you want to perform a single request and then exit the program, enter the request directly in the command line as follows:

```sh
>>> python chatbot.py Talk about OpenAI

OpenAI is an artificial intelligence research laboratory consisting of a team of researchers and engineers working on breakthroughs in machine learning and AI technology...
```
The program will reply to your request and then exit.

