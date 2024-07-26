from gpt_utils import get_answer_from_gpt

gpt_api_key = 'sk-DrR13CtaC3xoCSG37c9cB1D592A146Bf94E81a6b11A4C684' # gpt的api key， 会发给大家

question = '我是谁？'

my_prompt = "查询信息:" + '该用户是领队。' + "指令: 根据以上的查询信息，回答用户的问题。"\
                "不要增加额外的信息。确保回答是与查询信息一致的，而且不要输出错误或者多余的内容。"\
                    "如果用户的问题与查询到的信息无关，直接仅仅回答'未能查询到相关信息。'忽略与问题无关的查询结果。"\
                    "回答信息应当短小准确。使用中文回答，并且用“您”称呼提问者用户。"

my_prompt += '用户的问题：'+question+'回答：'

engine = 'gpt-3.5-turbo' # 我们就用这个，这个很便宜（乐）

answer = get_answer_from_gpt(gpt_api_key, my_prompt, engine)

print(answer)