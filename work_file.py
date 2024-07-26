from db_api import customTransaction
from db_api.DataQueryApis.GetTeacherInfoApis import *
from utils.utils import verification, classification_whole, classification_question, summarization, GetUserState, add_previous_prompts, execute_instruction, mysql_execute
from search_pdf_utils import SemanticSearch, load_recommender 

recommender_dict = dict(
    A = SemanticSearch(),
    B = SemanticSearch(),
    C = SemanticSearch(),
    D = SemanticSearch(),
    E = SemanticSearch(),
    F = SemanticSearch(),
)
load_recommender(recommender_dict['A'], 'references\\出分相关问题.pdf')
load_recommender(recommender_dict['B'], 'references\\身份变动问题.pdf')
load_recommender(recommender_dict['C'], 'references\\试题传输问题.pdf')
load_recommender(recommender_dict['D'], 'references\\考试相关问题.pdf')
load_recommender(recommender_dict['E'], 'references\\学校老师小程序使用指南230323.pdf')
load_recommender(recommender_dict['F'], 'references\\阅卷相关问题.pdf')
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

def answer_user_question(user_wechat_nickname, user_question):
    # try:
        # ---------------------------------- TODO ---------------------------------------
        # TODO: fill in here to answer user's question.
        # You can make new files in the /utils folder and import them here, to make this file cleaner.
        cycle_times = 0
        print('')
        print('-------------------------------------------------')
        print(user_wechat_nickname+':')
        print(user_question)
        state = GetUserState(user_wechat_nickname)
        if state == '不在系统中':
            sql_prompt = '该用户“不在系统中”，尚未提交审核，所以没有通过。无法提交试卷、阅卷、也无法完成领队或者副领队相关操作。该用户未按要求在报名时登陆，因此尚未提交审核。'
        elif state == '待审核':
            sql_prompt = '该用户的状态是“待审核”，需要等待审核，这也是该用户审核没有通过的原因。审核完成之后，才能提交试卷或阅卷、才能完成领队或者副领队相关操作。'
        elif state == '审核通过且在系统中':
            sql_prompt = '该用户在系统中、已经审核通过了。'
        answer_InvalidReason_list = []
        while(True):
            added_prompt = '注意：在数据库里，该用户的状态是：'+sql_prompt
            if len(answer_InvalidReason_list) > 0:
                added_prompt += add_previous_prompts(answer_InvalidReason_list)
            print("-=-=-=")
            print(cycle_times)
            if state == '不在系统中':
                answer = '您目前这个微信号“不在系统中”，尚未提交审核，所以没有通过。无法提交试卷、阅卷、也无法完成领队或者副领队相关操作（包括添加修改学生信息等）。您未按要求在报名时登陆，因此尚未提交审核。如果您在小程序里使用的是另一个微信号，请使用该微信号向我问问题！。'
                # return answer_added
                return answer
            elif state == '待审核':
                answer = '您的状态是“待审核”，需要等待审核，这也是该用户审核没有通过的原因。审核完成之后，才能提交试卷或阅卷、才能完成领队或者副领队相关操作（包括添加修改学生信息等）。'
                # return answer_added
                return answer
            else:
                answer_added = ''
            class_ = classification_whole(user_question,added_prompt).replace(' ','').replace('。','')
            class_ = remove_others(class_)
            print('Classifier (Whole): '+class_)
            execution_dict = None
            if class_ == 'A':
                # answer = '您当前微信号的审核应当已经通过了！'
                execution_dict = execute_instruction(user_question,added_prompt)
                answer = '执行了指令：'+execution_dict['discription']
                
                # class_ = 'B'
            if class_ == 'B':
                question_class = classification_question(user_question,added_prompt)
                print('Classifier (Question): ' + question_class)
                if question_class == 'G':   
                    answer = '非常抱歉，您的问题与我们的AI客服无法回答，请您联系人工客服。'
                else:
                    
                    if question_class in recommender_dict.keys():
                        recommender_1 = recommender_dict[question_class]
                    else:
                        recommender_1 = recommender_dict['B']
                    
                    topn_chunks = recommender_1(user_question) 
                    answer = summarization(user_question, topn_chunks, state, added_prompt) 
                           
            if class_ == 'C':
                answer = '非常抱歉，您的问题与我们小程序的功能无关。如果您有关于小程序的任何疑问或需要帮助，我们将尽力为您提供支持。感谢您的理解。'
            print('Executer: ' + answer)
            verifier_result, new_verifier_reason = verification(user_question, answer, added_prompt)
            answer_InvalidReason_list.append((user_question, new_verifier_reason))
            answer = answer_added + answer
            if verifier_result:   
                if execution_dict is not None:
                    if execution_dict['instruction_name'] is not None:
                        try:
                            returned = mysql_execute(execution_dict['instruction_name'],execution_dict['args'],user_wechat_nickname)
                            # print(returned)
                        except Exception as e:
                            answer = answer + '。但是执行指令时出现了错误：' + str(e)        
                            print('answer is: ', answer)
                            return answer
                    answer = '执行成功了如下的指令：' + execution_dict['discription'] + '，结果为：' + returned
                print('answer is: ', answer)
                return answer
            print('answer is: ', answer)
            
            cycle_times += 1
            if cycle_times >= 10:
                return '很抱歉，我们的AI回复系统无法回复您的问题。请您联系我们的人工客服，我们将尽力为您提供支持。感谢您的理解。'
        # ---------------------------------- TODO ---------------------------------------
    # except Exception as e:
    #     print(e)
    #     return 'an Error of type ' + str(type(e)) + ' has occurred.'