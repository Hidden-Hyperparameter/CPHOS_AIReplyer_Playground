from ..glm_utils import get_answer_from_glm
from ..db_api import customTransaction
from ..db_api.DataQueryApis.GetTeacherInfoApis import *
from ..db_api.DataManagingApis.ChangeTeacherInfoApis import *
from ..db_api.DataQueryApis.GetSchoolInfoApis import *
from ..gpt_utils import get_answer_from_gpt
from ..utils.logger import logger

gpt35_api_key = 'sk-DrR13CtaC3xoCSG37c9cB1D592A146Bf94E81a6b11A4C684'
gpt4_api_key = 'sk-ixjkS5LEaPD9htwt02F28e72269d4615BdBd4b8907022624' # gpt的api key， 会发给大家
glm_api_key = '76ac5e2039ac8a8da4bd924957e03b20.kJAQi8ptu0ynObZr'

def get_answer(prompt, engine):
    if 'gpt-3.5' in engine:
        answer = get_answer_from_gpt(prompt, engine)
    elif 'glm' in engine:
        answer = get_answer_from_glm(prompt, engine)
    elif 'gpt-4' in engine:
        answer = get_answer_from_gpt(prompt, engine)
    return answer



CLASSIFIER_ENGINE = 'chatglm_turbo'
EXECUTER_ENGINE = 'gpt-3.5-turbo'
VERIFIER_ENGINE = 'gpt-3.5-turbo'



def add_previous_prompts(answer_InvalidReason_list):
    added_str = "\n注意，如下的一些该问题的参考回答因为这些原因被认为是不恰当的，所以被过滤掉了："
    for (answer, reason) in answer_InvalidReason_list:
        added_str += '\n' + '错误答案：' + answer + '错误原因：' + reason
    added_str += '\n'
    return added_str


def classification_question(question,added_prompt=''):

    my_prompt = "指令: 根据用户的问题进行分类，如果用户的问题与查询成绩、分数或排名有关，回答A;"\
                    "如果用户的问题与身份录入与添加，身份信息与审核有关，回答B;"\
                    "如果用户的问题与试卷传输有关，回答C;"\
                    "如果用户的问题与考试试题，考试报名，考试时间有关，回答D;"\
                    "如果用户的问题与小程序使用有关，回答E;"\
                    "如果用户的问题与阅卷有关，回答F;"\
                    "其余情况回答G。不要增加额外的信息。确保回答严格与指令一致，而且不要输出错误或者多余的内容，回答内容只能包含A,B,C,D,E,F,G中的一个。"
    
    my_prompt += added_prompt

    my_prompt += '用户的问题：'+question+'回答：'

    engine = CLASSIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine)

    return answer.replace('\"','').replace('\'','').replace(' ','').replace('\n','').replace('\t','').replace('  ','')

def execute_instruction(instruction, added_prompt = ''):
    my_prompt = "指令：根据用户的问题，根据如下的格式输出对应的操作以及参数。如果有参数无法给出或者指令不在如下列出的指令中，请用?代替。"\
                "Instruction==ChangeAllTypesMarkingSubject|||Args==7"\
                "Instruction==?|||Args==?"\
                "Instruction==ChangeAllTypesMarkingSubject|||Args==?"\
                "Instruction==GetTeacherNotViewedProblemNumber|||Args==?"\
                "Instruction==VerifyTeacherUserToBeSupTeacher|||Args==史景喆，华东师大二附中"\
                "Instruction==VerifyTeacherUserToBeSupTeacher|||Args==某人名，?"\
                "有如下的指令："\
                "ChangeAllTypesMarkingSubject:修改老师的批阅题目，参数：题目号(int)"\
                "GetTeacherNotViewedProblemNumber:得到老师未批的题目，参数：无"\
                "VerifyTeacherUserToBeSupTeacher:完成老师的审核，参数：姓名(str)，学校(str)"
    
    
    my_prompt += added_prompt
    my_prompt += '指令：'+instruction+'生成的命令：Instruction=='
    engine = EXECUTER_ENGINE
    answer = get_answer(my_prompt, engine)
    logger.info('[CPHOS Model][Run] '+answer)
    try:
        instruction = answer.split('|||')[0]
        args = answer.split('|||')[1].split('==')[1]
    except Exception as e:
        print(e)
        return dict(
            instruction_name = None,
            args = None,
            discription = '指令不在可执行的指令中。'
        )
    if instruction == 'ChangeAllTypesMarkingSubject':
        if args == '?':
            return dict(
                instruction_name = None,
                args = None,
                discription = '修改老师的批阅题目，但题目号未给出'
            )
        return dict(
            instruction_name = instruction,
            args = int(args),
            discription = '修改老师的批阅题目，修改为：'+args+'号题目'
        )
    elif instruction == 'GetTeacherNotViewedProblemNumber':
        return dict(
            instruction_name = instruction,
            args = None,
            discription = '得到老师未批的题目数目'
        )
    elif instruction == 'VerifyTeacherUserToBeSupTeacher':
        return dict(
            instruction_name = instruction,
            args = args,
            discription = "进行审核",   
        )
    else:
        return dict(
            instruction_name = None,
            args = None,
            discription = '指令不在可执行的指令中。'
        )
    
    
def classification_whole(question,added_prompt):
                # retry: no C.
    my_prompt = '用户的话：'+question
    my_prompt += "指令: 根据用户的话进行分类，如果用户话是陈述句，表达的意思是要求执行某种操作或查询（注意：不是询问操作方式，而是指明了要求执行某种操作或查询），且这个操作作用在储存用户基本信息的数据库上，回答字母A;"\
                    "如果用户在询问问题，或者询问操作的方式，回答字母B。"\
                    "不要增加额外的信息。确保回答严格与指令一致，只能回答A,B中的一个，而且不要输出错误或者多余的内容。例如："\
                        "用户话：怎么添加副领队？回答：B。"\
                        "用户话：我希望添加ABC为我的副领队。回答：A"\
                        "用户话：试卷解压不了？怎么解压？回答：B"\
                        "用户话：怎么添加学生信息？为什么添加不了学生信息？回答：B"\
                        "用户话：我希望能在数据库中通过我的审核。回答：A"\
                        "用户话：请变更我的批改题号。回答：A"\
                        "用户话：我还有多少题没批？回答：A"
    my_prompt += added_prompt
    my_prompt += "回答："

    engine = CLASSIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine)

    return answer.replace('\"','').replace('\'','').replace(' ','').replace('\n','').replace('\t','').replace('  ','')

def verification(question, answer, added_prompt):

    my_prompt = f"有一组问答。问题：{question}，回答：{answer}。"\
                "指令: 请判断上述回答是否是回答者在它已知的条件下做出的合理相关的应对，回答是或否,并且给出理由。请注意，回答者并不知道全部信息，所以回答者给出一些可能性，或者仅仅是相关的信息,或者直接说不知道相关信息，建议联系人工客服，是很合理的。但如果回答者给出不相关的回复，那么就是错误的。你需要遵循以下的格式："\
                "样例1："\
                "是|||是合理的回答，因为提问者问的是为何审核没有通过，回答是状态是待审核，请等待审核即可。"\
                "样例2："\
                "是|||是合理的回答，因为提问者问的是如何添加学生信息，回答是状态是待审核，并且解释了需要审核通过才能添加学生信息。"\
                "样例3："\
                "否|||是不合理的回答，因为提问者问的是为何审核没有通过，回答却只给出了加入学生信息，这与用户的要求不符。"\
                "样例4："\
                "是|||是合理的回答，因为回答者说：非常抱歉，您的问题与我们小程序的功能无关。如果您有关于小程序的任何疑问或需要帮助，我们将尽力为您提供支持。感谢您的理解。表明回答者不知道相关情况。"\
                "是|||是合理的回答，因为回答者说：非常抱歉，您的问题与我们的AI客服无法回答，请您联系人工客服。表明回答者不知道相关情况。"\
                "是|||是合理的回答，因为问题要求对他的批阅题号做出变更，而回答者完全执行了这一操作。"\
                "请注意，如果回答者回答了审核未通过，还需要解释需要审核通过才能做一些事情；如果回答者回答了审核通过，它应该给出做这件事情的具体方式，而不仅仅是审核已通过的结果。"\
                "不要增加额外的信息。确保回答严格与指令一致，只能回答是、否的一个以及对应理由，而且不要输出错误或者多余的内容。"\

    my_prompt += added_prompt
    engine = VERIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine).replace('\"','').replace('\'','')
    logger.info('[CPHOS Model][Run] Verifier: '+answer)
    if ('不合理' not in answer.split('|||')[1])and('否' not in answer.split('|||')[0]):
        return True, answer.split('|||')[-1]
    else:
        return False, answer.split('|||')[-1]

def summarization(question, topn_chunks, state,added_prompt):
    
    my_prompt = f"用户问题：{question}，"

    for i, answer in enumerate(topn_chunks):
        my_prompt += f"人工客服给的第{i+1}个回答：{answer}"
    
    my_prompt += "用户状态是：" + state + "。"
    my_prompt += "指令: 请根据用户状态，用户问题与人工客服的回答，找出所有回答中能够有效回答用户问题的部分，然后进行总结并回复用户。"\
                "请确保不要输出根据，直接回答用户的问题，确保回答严格与指令一致，不要输出错误或者多余的内容。请不要用不确定的语气，给出你当前已知信息下确定性的回答。"
    my_prompt += added_prompt
    my_prompt += "回答："
    engine = EXECUTER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine)
    
    return answer

def GetUserState(user_wechat_nickname):
    user_id_returned_list = customTransaction.executeOperation(GetTeacherInfoByWechatName(user_wechat_nickname))
    user_id_to_be_verified_list = customTransaction.executeOperation(GetToBeVerifiedTeacherInfoByWechatName(user_wechat_nickname))
    # print(user_id_returned_list)
    # print(user_id_to_be_verified_list)
    if len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) == 0:
        state = "不在系统中"
    elif len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) >= 1:
        state = "待审核"
    elif len(user_id_returned_list) == 1:
        state = "审核通过且在系统中"
    # print(state)
    return state
def mysql_execute(instruction_name, args, user_wechat_nickname):
    # print("Here!")
    # print(instruction_name)
    # print(args)
    # print(user_wechat_nickname)
    user_id_returned_list = customTransaction.executeOperation(GetTeacherInfoByWechatName(user_wechat_nickname))
    assert len(user_id_returned_list) == 1
    user_id = user_id_returned_list[0]['id']
    if instruction_name == 'ChangeAllTypesMarkingSubject':
        customTransaction.executeOperation(ChangeAllTypesMarkingSubject(user_id, int(args)))
        customTransaction.commit_and_reconnect()
        return '成功！'
    elif instruction_name == 'GetTeacherNotViewedProblemNumber':
        number, _ = customTransaction.executeOperation(GetTeacherNotViewdProblemNumber(user_id))
        return f'还有{number}题待批改'
    elif instruction_name == 'GetTeacherNotViewedProblemNumber':
        arg_list = args.split("，")
        assert len(arg_list) == 2, '出现了问题：args是'+args+"但是理应是姓名，学校的格式"
        assert arg_list[0] != '?', '请告知您的姓名与学校'
        assert arg_list[1] != '?', '请告知您的姓名与学校'
        school_list = customTransaction.executeOperation(GetSchoolInfoByName(arg_list[1]))
        assert len(school_list) == 1,'找不到学校:'+arg_list[1]
        school_id = school_list[0]['id'], area_id = school_list[0]['area_id']
        tobeverified_list = customTransaction.executeOperation(GetToBeVerifiedTeacherInfoByWechatName(user_wechat_nickname))
        assert len(tobeverified_list) == 1,'没有提交审核或已经审核通过了！'
        teacher_id = tobeverified_list[0]['id']
        customTransaction.executeOperation(VerifyTeacherUserToBeSupTeacher(teacher_id,arg_list[0],school_id,1,1))
        return '成功！'
    