# 调用chatgpt使用的函数
# 注意，为了调用gpt，需要使用全局vpn；最好用北美的vpn。
import os
from dotenv import load_dotenv
load_dotenv()
os.environ['OPENAI_API_BASE'] = "https://oneapi.xty.app/v1"
assert os.environ.get('OPENAI_API_KEY','').startswith('sk-'),'Please set the OPENAI_API_KEY in the .env file to the secret key.'

from openai import ChatCompletion

def get_answer_from_gpt(prompt,
                        engine='gpt-3.5-turbo',
                        ):
    messages = [
        {
            'role': 'user',
            'content':prompt,
        }
    ]
    completions = ChatCompletion.create(
        model = engine,
        messages = messages,
        max_tokens = 2048,
        n=1,
        stop=None,
        temperature=0.7
    )
    # print(completions)
    message = completions.choices[-1]['message']['content']
    return message