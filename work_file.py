from .utils.utils import verification, classification_question, summarization, GetUserState, add_previous_prompts, execute_instruction, mysql_execute, choose_better_ans
from .search_pdf_utils import SemanticSearch, load_recommender 
import os
from .utils.logger import logger

from .db_api import customTransaction
from .db_api.DataQueryApis.GetTeacherInfoApis import *

recommender_dict = dict(
    A = SemanticSearch(),
    B = SemanticSearch(),
    C = SemanticSearch(),
    D = SemanticSearch(),
    E = SemanticSearch(),
    F = SemanticSearch(),
)
dir_path = os.path.dirname(os.path.realpath(__file__))
load_recommender(recommender_dict['A'], os.path.join(dir_path,'references','marking'))
load_recommender(recommender_dict['B'], os.path.join(dir_path,'references','identity_change'))
load_recommender(recommender_dict['C'], os.path.join(dir_path,'references','offseason_problems'))
load_recommender(recommender_dict['D'], os.path.join(dir_path,'references','exam_related_problems'))
load_recommender(recommender_dict['E'], os.path.join(dir_path,'references','school_teacher_miniprogram_guide_230323'))
load_recommender(recommender_dict['F'], os.path.join(dir_path,'references','marking'))
def remove_others(x):
    if 'A' in x:
        return 'A'
    elif 'B' in x:
        return 'B'
    elif 'C' in x:
        return 'C'
    elif 'D' in x:
        return 'D'
    elif 'E' in x:
        return 'E'
    elif 'F' in x:
        return 'F'
    elif 'G' in x:
        return 'G'
    elif 'H' in x:
        return 'H'
    else:
        return 'aonaweofkdj'

def answer_user_question(user_wechat_nickname, user_question,max_try=3):
    # try:
        # ---------------------------------- TODO ---------------------------------------
        # TODO: fill in here to answer user's question.
        # You can make new files in the /utils folder and import them here, to make this file cleaner.
        cycle_times = 0
        print('-'*20)
        logger.info(f'[CPHOS Model], User: {user_wechat_nickname}, Question: {user_question}')
        state = GetUserState(user_wechat_nickname)
        logger.info(f'[CPHOS Model][Run] The user is {state}')
        if state == '不在系统中':
            return '您目前使用的群备注（注意是群聊备注，不是微信号）“不在系统中”，尚未提交审核，所以没有通过。无法提交试卷、阅卷、也无法完成领队或者副领队相关操作（包括添加修改学生信息等）。您未按要求在报名时登陆，因此尚未提交审核。如果您在小程序里使用的是另一个微信号，请使用该微信号向我问问题！。'
        elif state == '待审核':
            return '您的状态是“待审核”，需要等待审核，这也是该用户审核没有通过的原因。审核完成之后，才能提交试卷或阅卷、才能完成领队或者副领队相关操作（包括添加修改学生信息等）。'
        
        sql_prompt = '该用户在系统中、已经审核通过了。'
        answer_InvalidReason_list = []

        choice_for_A = 1
        choice_for_B = max_try - choice_for_A

        # first, try to interpret it as problem A
        return_value_A = None
        for cycle_time in range(choice_for_A):
            added_prompt = '注意：在数据库里，该用户的状态是：'+sql_prompt
            if len(answer_InvalidReason_list) > 0:
                added_prompt += add_previous_prompts(answer_InvalidReason_list)
            logger.info(f'[CPHOS Model][Run] Class A, Try for the {cycle_time+1}th time...')
            execution_dict = execute_instruction(user_question,added_prompt)
            answer = '执行了指令：'+execution_dict['discription']
            logger.info(f'[CPHOS Model][Run] Result for Class A round {cycle_time+1} : ' + answer)
            verifier_result, new_verifier_reason = verification(user_question, answer, added_prompt)
            if answer not in [x for x,_ in answer_InvalidReason_list]:
                answer_InvalidReason_list.append((answer, new_verifier_reason))
            if verifier_result:
                returned = ''
                if execution_dict['instruction_name'] is not None:
                    try:
                        returned = mysql_execute(execution_dict['instruction_name'],execution_dict['args'],user_wechat_nickname)
                        # print(returned)
                    except Exception as e:
                        answer = answer + '。但是执行指令时出现了错误🧐：' + str(e)        
                        return_value_A = answer; break
                    answer = '🎉🎉🎉 执行成功了如下的指令：' + execution_dict['discription'] + '，结果为：' + returned
                else:
                    answer = '我试着把你的回答理解为指令，但是发现了一个问题🧐：'+execution_dict['discription']
                return_value_A = answer; break
            
        if return_value_A is None:
            return_value_A = '很抱歉🥺，我们的AI回复系统无法回复您的问题。请您联系我们的人工客服，我们将尽力为您提供支持。感谢您的理解。'
        
        # second, try to interpret as problem B
        answer_InvalidReason_list = []
        return_value_B = None
        for cycle_time in range(choice_for_B):
            added_prompt = '注意：在数据库里，该用户的状态是：'+sql_prompt
            if len(answer_InvalidReason_list) > 0:
                added_prompt += add_previous_prompts(answer_InvalidReason_list)
            logger.info(f'[CPHOS Model][Run] Class B, Try for the {cycle_time+1}th time...')
            execution_dict = None
            question_class = classification_question(user_question,added_prompt)
            logger.info('[CPHOS Model][Run] Secondary Classifier Result: ' + question_class)
            if question_class == 'G':
                answer = '非常抱歉🥺，我们的AI客服无法回答您的问题，请您联系人工客服。'
            else:
                if question_class in recommender_dict.keys():
                    recommender_1 = recommender_dict[question_class]
                else:
                    recommender_1 = recommender_dict['B']
                topn_chunks = recommender_1(user_question) 
                answer = summarization(user_question, topn_chunks, state, added_prompt) 
            logger.info(f'[CPHOS Model][Run] Result for Class B round {cycle_times+1} : ' + answer)
            verifier_result, new_verifier_reason = verification(user_question, answer, added_prompt)
            if answer not in [x for x,_ in answer_InvalidReason_list]:
                answer_InvalidReason_list.append((answer, new_verifier_reason))
            if verifier_result:   
                return_value_B = answer; break
        if return_value_B is None:
            return_value_B = '很抱歉🥺，我们的AI回复系统无法回复您的问题。请您联系我们的人工客服，我们将尽力为您提供支持。感谢您的理解。'
        
        # finally, feed these to a model.
        return choose_better_ans(user_question, return_value_A, return_value_B)
        
        # ---------------------------------- TODO ---------------------------------------
    # except Exception as e:
    #     print(e)
    #     return 'an Error of type ' + str(type(e)) + ' has occurred.'