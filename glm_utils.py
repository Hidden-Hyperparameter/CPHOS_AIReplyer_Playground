#调用glm使用的函数
import os
assert len(os.environ.get('API_KEY','')) > 0, 'Please set the API_KEY in the .env file to the secret key.'
import zhipuai
def get_answer_from_glm(prompt,engine='chatglm_130b'):
    messages = [
        {
            'role':'user',
            'content':prompt,
        }
    ]
    response = zhipuai.model_api.invoke(
                model = engine,
                prompt = messages,
            )
    # print(response)
    return response['data']['choices'][-1]['content']