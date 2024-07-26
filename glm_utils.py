#调用glm使用的函数
import zhipuai
def get_answer_from_glm(AI_key,prompt,engine='chatglm_130b'):
    zhipuai.api_key=AI_key
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