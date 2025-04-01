import random

from openai import OpenAI


def call_api(prompt, system_prompt="You are a helpful, respectful and honest assistant."):
    # client = OpenAI()
    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     temperature=1,
    #     top_p=1,
    #     max_completion_tokens=2048,
    #     frequency_penalty=0,
    #     presence_penalty=0,
    #     response_format={
    #         "type": "text"
    #     },
    #     messages=[
    #         {"role": "user",
    #          "content": [
    #              {
    #                  "type": "text",
    #                  "text": prompt
    #              }
    #          ]
    #          }
    #     ]
    # )
    #
    # return completion.choices[0].message.content
    return random.choice(["Yes", "No"])
