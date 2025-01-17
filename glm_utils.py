#调用glm使用的函数
import os
key = os.environ.get('API_KEY','')
assert len(key) > 0, 'Please set the API_KEY in the .env file to the secret key.'

print('proxy:',os.environ.get('HTTP_PROXY',''))

# print('key:',key)

from zhipuai import ZhipuAI
client = ZhipuAI(api_key=key)  # Please fill in your own APIKey

def get_answer_from_glm(prompt,engine='chatglm_130b'):
    messages = [
        {
            'role':'user',
            'content':prompt,
        }
    ]
    response = client.chat.completions.create(
        model=engine,
        messages=messages
    )
    return response.choices[0].message.content