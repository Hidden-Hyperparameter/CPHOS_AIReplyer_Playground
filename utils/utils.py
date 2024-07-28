from ..glm_utils import get_answer_from_glm
from ..db_api import customTransaction
from ..db_api.DataQueryApis.GetTeacherInfoApis import *
from ..db_api.DataManagingApis.ChangeTeacherInfoApis import *
from ..db_api.DataQueryApis.GetSchoolInfoApis import *
from ..gpt_utils import get_answer_from_gpt
from ..utils.logger import logger
import string

def get_answer(prompt, engine, role=''):
    logger.info(f'[LLM] {role}, Prompt is """'+prompt+'"""')
    if 'gpt-3.5' in engine:
        answer = get_answer_from_gpt(prompt, engine)
    elif 'glm' in engine:
        answer = get_answer_from_glm(prompt, engine)
    elif 'gpt-4' in engine:
        answer = get_answer_from_gpt(prompt, engine)
    logger.info(f'[LLM] {role}, Result is """'+answer+'"""')
    return answer



CLASSIFIER_ENGINE = 'chatglm_turbo'
EXECUTER_ENGINE = 'gpt-3.5-turbo'
VERIFIER_ENGINE = 'gpt-3.5-turbo'



def add_previous_prompts(answer_InvalidReason_list):
    added_str = "\n注意，以下是一些错误的答案，以及它们错误的原因。你必须避免这些错误。\n"
    # added_str = "\n注意，如下的一些该问题的参考回答因为这些原因被认为是不恰当的，所以被过滤掉了："
    for (answer, reason) in answer_InvalidReason_list:
        added_str += '\n' + '>>>错误答案：' + answer + '\n>>>错误原因：' + reason
    added_str += '\n'
    return added_str


def classification_question(question,added_prompt=''):

    my_prompt = """### 你的任务

请你根据用户的问题内容，给出对应的问题类别。你必须遵守以下的具体规则和格式要求。

### 具体规则

- 如果用户的问题与查询成绩、分数或排名有关，回答A;
- 如果用户的问题与身份录入与添加，身份信息与审核有关，回答B;
- 如果用户的问题与加入组织有关，或者与上一次/下一次考试有关，回答C;
- 如果用户的问题与考试试题，考试报名，考试时间有关，回答D;
- 如果用户的问题与小程序使用有关，回答E;
- 如果用户的问题与阅卷有关，回答F;
- 其余情况回答G。

### 格式要求

你的回答**必须**是A,B,C,D,E,F,G中的**一个**字母。你必须只能回答一个字母。你不能回答多余的内容。

### 下面，任务正式开始。

这里还有一些对你可能有帮助的额外信息："""
    
    my_prompt += added_prompt

    my_prompt += '\n用户的问题：'+question+'\n\n### 你的答案\n\n我选择的这一个字母是'
    engine = CLASSIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine,role='\033[32mSecondary Classifier\033[0m')
    answer = answer.replace('\"','').replace('\'','').replace(' ','').replace('\n','').replace('\t','').replace('  ','').upper()
    answer = [c for c in answer if c in 'ABCDEF']
    if len(answer): return answer[0]
    return 'G'

def execute_instruction(instruction, added_prompt = ''):
    my_prompt = """### 你的任务

根据用户的要求，输出一个Instruction和其需要的Args。你必须遵守以下的具体规则和格式要求。

### 具体规则

1. 你需要从以下的3个指令中选择最契合用户要求的指令：
    - Instruction: ChangeAllTypesMarkingSubject；功能: 修改老师的批阅题目；Args：题目号(int)。
    - Instruction: GetTeacherNotViewedProblemNumber；功能: 得到老师未批的题目；Args：无。
    - Instruction: VerifyTeacherUserToBeSupTeacher；功能: 完成老师的审核；Args：姓名(str)，学校(str)。
2. 如果有Args无法给出或者指令不在以上列出的三条指令中，请用?代替。
3. 对于Args为“无”的情形，你必须使用Args=?的格式。

### 格式要求

以下是本问题合法的的格式示例。请你尽力让你的格式和示例一致。

1. Instruction==VerifyTeacherUserToBeSupTeacher|||Args==史景喆，华东师大二附中
2. Instruction==ChangeAllTypesMarkingSubject|||Args==7
3. Instruction==?|||Args==?
4. Instruction==ChangeAllTypesMarkingSubject|||Args==?
5. Instruction==GetTeacherNotViewedProblemNumber|||Args==?
6. Instruction==VerifyTeacherUserToBeSupTeacher|||Args==李华，?

### 下面，任务正式开始。

这里还有一些对你可能有帮助的额外信息："""
    
    my_prompt += added_prompt
    my_prompt += '\n用户给出的要求：'+instruction+'\n\n### 你的答案\n\nInstruction=='
    engine = EXECUTER_ENGINE
    answer = get_answer(my_prompt, engine,role='\033[31mExecutor\033[0m')
    try:
        instruction = answer.split('|||')[0]
        i = 0
        while not instruction[i].isalpha(): i+=1
        instruction:str = instruction[i:]
        if instruction.startswith('Instruction=='):
            instruction = instruction[len('Instruction=='):]
        instruction = ''.join([c for c in instruction if c in string.ascii_letters])
        args = answer.split('|||')[1].split('==')[1]
    except Exception as e:
        logger.info(f'[CPHOS Model][Run] \033[31mError\033[0m in \033[31mExecutor\033[0m : {e}')
        return dict(
            instruction_name = None,
            args = None,
            discription = '指令不在可执行的指令中。'
        )
    logger.info(f'[CPHOS Model][Run] Instruction: {instruction} Args: {args}')
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
            discription = "审核老师是否为副领队，姓名为"+args,   
        )
    else:
        return dict(
            instruction_name = None,
            args = None,
            discription = '指令不在可执行的指令中。'
        )
    
    
def classification_whole(question,added_prompt):
                # retry: no C.
    my_prompt = """### 你的任务

你是一个考试的数据库的管理者。你的数据库包含的内容有：
- 每一位领队和副领队批改的题目编号，已经批改和尚未批改的题目数量；
- 每一个领队具有的副领队；
- 每一个领队具有的学生信息。

同时，你还有一系列文档。这些文档包含了大量的方法（如何添加副领队，如何添加学生信息等），但不包含你的数据库内的数据。

有时，用户只是向你询问某操作的执行方式，这时你无需调用你的数据库，只需要通过文档就可以回答用户的问题；但有时，用户希望执行某操作，这时你必须调用你的数据库。

现在，你接收到一个用户的指示，你需要判断这一用户是否应该访问你的数据库。

### 具体规则

- 如果你认为用户的指示对应一个需要和你的数据库交互的具体操作，那么回答字母A；
- 如果你认为可以只通过文档解释就可以回应用户，不需要访问你的数据库，那么回答字母B；
- 如果你感到纠结，为了保护你的数据库，回答字母B。

### 技巧

以下技巧可以帮助你判断：
- 如果用户明确给出一个操作，或者作出命令，那么他需要和你的数据库交互；
- 如果用户的语气是询问的，并且不涉及数据访问，那么很有可能他不需要和你的数据库交互。

### 格式要求

你需要分两行给出你的结果：在第一行，给出“你的思考”；在第二行，给出“你的回答”。

### 示例回答

你可以参考以下的示例回答，以确保你对前面所述具体规则与格式要求的理解无误。

*** 示例1
>>> 用户：怎么添加副领队？
>>> 你的思考：用户的语气在询问：“怎么添加”。这不是一个操作，因此我无需访问数据库。
>>> 你的回答：B

*** 示例2
>>> 用户：我希望添加一位副领队。
>>> 你的思考：用户明确指出一个操作——希望添加一位副领队。这需要和我的数据库交互。
>>> 你的回答：A

*** 示例3
>>> 用户：我还有多少题没批？
>>> 你的思考：虽然用户提出了一个问题，但是这一问题对应一个数据，我无法在文档找到。因此，需要和我的数据库交互。
>>> 你的回答：A

*** 示例4
>>> 用户：怎么添加学生信息？为什么我添加不了学生信息？
>>> 你的思考：用户在询问添加学生信息的方法。这不需要和我的数据库交互，我可以通过文档回答。
>>> 你的回答：B

### 下面，任务正式开始。"""

    my_prompt += f"\n\n*** 最终问答\n>>> 用户：{question}\n>>> 你的思考："

    engine = CLASSIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine,role='\033[33mPrimary Classifier\033[0m')
    answer = answer.replace('\"','').replace('\'','').replace(' ','').replace('\n','').replace('\t','').replace('  ','')
    answer = [c for c in answer if c in 'AB']
    if len(answer): return answer[-1]
    logger.warn(f'[CPHOS Model][Run] \033[33mPrimary Classifier\033[0m cannot determine. Its output: {answer}')
    return 'B' # 'A' is more dangerous, so we choose 'B' as default.

def verification(question, answer, added_prompt):

    ans_in_one_line = answer.replace('\n','')
    my_prompt = f"""### 你的任务

你将被给予一对问题和回答。你需要判断此回答(A)是否很恰当的回答了该问题(Q)。你必须遵循以下的具体规则和格式要求。

### 具体规则

- 如果回答包含相关的信息，或者指明因为回答者不知道相关的信息所以建议联系人工客服，那么回答“是”，并给出你的理由；
- 如果回答和问题不相关，那么回答“否”，并给出你的理由。

### 格式要求

你的回答由X和Y两部分组成，中间用|||分割。也就是说，你的答案是X|||Y。
- X是一个汉字，“是”或“否”，不需要加入双引号；
- Y是一段文字，也就是你的理由。

### 示例回答

你可以参考以下的示例回答，以确保你对前面所述具体规则与格式要求的理解无误。

*** 样例1
Q: 为什么审核没有通过？
A: 你现在的状态是待审核，请等待审核即可。
你的答案: 是|||这是合理的回答，因为提问者问的是为何审核没有通过，回答是状态是待审核，请等待审核即可。

*** 样例2
Q: 为什么审核没有通过？
A: 只有审核通过之后，您才可以添加学生信息。
你的答案：否|||这是不合理的回答，因为提问者问的是为何审核没有通过，回答却只给出了加入学生信息，这与用户的要求不符。

*** 样例3
Q: 我还有多少没批的题目？
A: 执行成功了如下的指令：得到老师未批的题目数目，结果为：10。
你的答案: 是|||这是合理的回答，因为提问者问的是如何添加学生信息，回答是状态是待审核，并且解释了需要审核通过才能添加学生信息。

*** 样例4
Q: 把我换成第四题阅卷人。
A: 根据您的状态和问题，以下是有效回答您问题的部分总结：1. 如果您没有上传试卷却收到阅卷任务，这是因为您的团队中有领队或其他副领队已经上传了试卷，阅卷任务是共享的。
你的答案：否|||这是不合理的回答，因为提问者问的是要对他的批阅题号做出变更，而回答者完全没有提及这一操作。

### 下面，任务正式开始。

***最终问答
Q: {question}
A: {ans_in_one_line}
你的答案：
"""
    # my_prompt += added_prompt
    engine = VERIFIER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine,role='\033[34mVerifier\033[0m').replace('\"','').replace('\'','')
    if ('不合理' not in answer.split('|||')[1])and('否' not in answer.split('|||')[0]):
        return True, answer.split('|||')[-1]
    else:
        return False, answer.split('|||')[-1]

def process_one_chunk(chunk:str):
    """extract the quotation"""
    try:
        s = chunk[chunk.find('"')+1:chunk.rfind('"')]
    except:
        s = chunk
    i = 0
    while s[i] in ' 1234567890': i+=1
    return s[i:]

def summarization(question, topn_chunks, state,added_prompt):

    my_prompt = f"""
### 你的任务
    
你收到了一个来自用户的问题，并看到了若干位人工客服给出的回答。你的任务是根据用户的问题，以及人工客服们的回答，总结出一个能够有效回答用户问题的回答。
必须注意，你不得利用你自己的知识忽略人工客服们的回答而直接回答用户的问题。相反，你必须利用人工客服们的回答。

### 回答的要求

你的回答必须具体，避免出现空泛的介绍性语句。比如如下的两个回答，一个是好的，一个是不好的：

>>> 问题：为什么我无法添加学生信息？
>>> 第1个人工客服的回答：您还没有通过审核，需要等待审核通过之后才能添加学生信息。
>>> 不好的回答：学生的信息安全至关重要。为了保护每一位学生的安全，人们广泛地采取了各种措施，比如等待审核通过之后才能添加学生信息。
>>> 好的回答：因为您还没有通过审核，只有在等待审核通过之后才能添加学生信息。

在接下来的任务中，你必须输出一份好的回答，并且不可以输出上述不好的回答。你的回答不应该以“好的回答”这四个汉字开始。

### 建议

你可以参考以下的建议，但不能为了它们而不遵守上述回答要求：

1. 恰当地使用换行符。在同一行书写太长会使人不适。
2. 你的回答要全面。比如，如果人工客服给出了三个解决方案，你需要同时汇报这三个方案。

### 问题

{question}"""
    
    # my_prompt = f"用户问题：{question}，"

    for i, answer in enumerate(topn_chunks):
        my_prompt += f"\n\n### 第{i+1}个人工客服的回答\n\n{process_one_chunk(answer)}"
    
    my_prompt += "\n\n### 额外信息\n\n提出问题的用户当前的状态是：" + state + "。\n"
    my_prompt += added_prompt
    my_prompt += "\n\n### 你的回答\n\n我的总结如下："
    engine = EXECUTER_ENGINE # or 'chatglm_6b'
    answer = get_answer(my_prompt, engine,role='Summarizer')
    
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
    