
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

def stream_request(messages):
    return openai.ChatCompletion.create(
        model="gpt-4o",
        # model = "gpt-3.5-turbo-0301",
        # model = self.config['model'],
        # model = "gpt-4-1106-preview",
        # model = "gpt-4-32k",
        # model = "gpt-4-32k-0613",
        # model = "gpt-4-1106-preview",
        messages=messages,
        # temperature=self.config["temperature"],
        # presence_penalty=self.config["presence_penalty"],
        # frequency_penalty=self.config["frequency_penalty"],
        stream=True,
    )
