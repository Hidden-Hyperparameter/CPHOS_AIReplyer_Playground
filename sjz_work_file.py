from db_api.DataQueryApis.GetTeacherInfoApis import *
from gpt_utils import get_answer_from_gpt
from glm_utils import get_answer_from_glm
import os
from search_pdf_utils import SemanticSearch, load_recommender #引入相关的工具

recommender_1 = SemanticSearch()
pdf_path = os.path.join('references','marking.pdf')
load_recommender(recommender_1, pdf_path)

USE_TOPN_CHUNK = 2

GPT_API_KEY = ['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',]
GLM_API_KEY = '76ac5e2039ac8a8da4bd924957e03b20.kJAQi8ptu0ynObZr'
GLM_ENGINE = 'chatglm_std'
# GPT_ENGINE = ['gpt-4', 'gpt-4-0314', 'gpt-4-0613']
GPT_ENGINE = ['gpt-3.5-turbo']

def answer_user_question(user_wechat_nickname, user_question, llm='gpt'):
    def get_answer(prompt):
        return get_answer_from_glm(GLM_API_KEY, prompt, GLM_ENGINE) if llm == 'glm' else get_answer_from_gpt(GPT_API_KEY, prompt, GPT_ENGINE) if llm == 'gpt' else None
    try:
        from db_api import customTransaction
        user_id_returned_list = customTransaction.executeOperation(GetTeacherInfoByWechatName(user_wechat_nickname))
        user_id_to_be_verified_list = customTransaction.executeOperation(GetToBeVerifiedTeacherInfoByWechatName(user_wechat_nickname))
        
        sql_returned_str = ''
        
        if len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) == 0:
            sql_returned_str += '该用户“不在系统中”，尚未提交审核，所以没有通过。无法提交试卷、阅卷、也无法完成领队或者副领队相关操作。该用户未按要求在报名时登陆，因此尚未提交审核。'
        elif len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) == 1:
            sql_returned_str += '该用户的状态是“待审核”，需要等待审核，这也是该用户审核没有通过的原因。审核完成之后，才能提交试卷或阅卷、才能完成领队或者副领队相关操作。'
        elif len(user_id_returned_list) == 1:
            teacher_id = user_id_returned_list[0]['id']
            teacher_type = user_id_returned_list[0]['type'] # 仲裁，副领队，领队
            sql_returned_str += '该用户在系统中、已经审核通过了，而且是{}。如果用户问道关于其身份的问题，就回答：您是{}。'.format(teacher_type, teacher_type)
        
        
        prompt = "查询信息:" + sql_returned_str + "指令: 根据以上的查询信息，回答用户的问题。"\
                "不要增加额外的信息。确保回答是与查询信息一致的，而且不要输出错误或者多余的内容。"\
                    "如果用户的问题与查询到的信息无关，直接仅仅回答'未能查询到相关信息。'忽略与问题无关的查询结果。"\
                    "回答信息应当短小准确。使用中文回答，并且用“您”称呼提问者用户。"
        # prompt = "Query:"+sql_returned_str+\
		# 	"Instructions: Compose a comprehensive reply to the query and annotation using the search results given. "\
        #         "If the search results mention multiple subjects "\
        #         "with the same name, create separate answers for each. Only include information found in the results and "\
        #         "don't add any additional information. Make sure the answer is correct and don't output false content. "\
        #         "search results which has nothing to do with the question. Only answer what is asked. The "\
        #         "answer should be short and concise. Answer step-by-step, using Chinese, and use '您' to call the questioner. You should answer based on the annotation of the user if necessary."
        
        
        prompt += '用户提问: ' + user_question + '回答: '
        
        answer = get_answer_from_glm(GLM_API_KEY, prompt, GLM_ENGINE)
        # answer = get_answer_from_gpt(GPT_API_KEY, prompt, GPT_ENGINE)
        print("User",user_wechat_nickname, ", User question:", user_question)
        print("Anser", answer)
        
        # if in answer we can find the phrase '未能查询到相关信息', then we use another prompt.
        if '未能查询到' not in answer:
            return dict(
                answer = answer,
                prompt = prompt,
            )
        else:
            pass
            # then we use another prompt.
        
        topn_chunks = recommender_1(user_question)
        prompt = "查询信息："
        for idx, chunks in enumerate(topn_chunks):
            prompt += "第"+str(idx)+"条查询信息："+chunks + "。"
            prompt += "\n"
            if idx >= USE_TOPN_CHUNK - 1:
                break
        prompt += "还有一条查询信息："+sql_returned_str + "指令: 根据以上的查询信息，回答用户的问题。"\
                "不要增加额外的信息。确保回答是与查询信息一致的，而且不要输出错误或者多余的内容。"\
                    "如果用户的问题与查询到的信息无关，直接仅仅回答'未能查询到相关信息。'忽略与问题无关的查询结果。"\
                    "回答信息应当短小准确。使用中文回答，并且用“您”称呼提问者用户。"
        prompt += '用户提问: ' + user_question + '回答: '
        
        print("Prompt used: ", prompt)
        
        answer = get_answer_from_glm(GLM_API_KEY, prompt, GLM_ENGINE)
        # answer = get_answer_from_gpt(GPT_API_KEY, prompt, GPT_ENGINE)
        print("User",user_wechat_nickname, ", User question:", user_question)
        print("Anser", answer)
        
        
        
        return dict(
            answer = answer,
            prompt = prompt,
        )
        
    except Exception as e:
        print(e)
        return dict(
            answer = 'an Error of type ' + str(type(e)) + ' has occurred.',
            prompt = 'an Error of type ' + str(type(e)) + ' has occurred.',
        )