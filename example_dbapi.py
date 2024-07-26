from db_api import customTransaction
from db_api.DataQueryApis.GetTeacherInfoApis import *


user_wechat_nickname = '史景喆'
user_id_returned_list = customTransaction.executeOperation(GetTeacherInfoByWechatName(user_wechat_nickname))
user_id_to_be_verified_list = customTransaction.executeOperation(GetToBeVerifiedTeacherInfoByWechatName(user_wechat_nickname))

sql_returned_str = ''

if len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) == 0:
    sql_returned_str += '该用户“不在系统中”，尚未提交审核，所以没有通过。无法提交试卷、阅卷、也无法完成领队或者副领队、添加修改学生信息等相关操作。该用户未按要求在报名时登陆，因此尚未提交审核。'
elif len(user_id_returned_list) == 0 and len(user_id_to_be_verified_list) == 1:
    sql_returned_str += '该用户的状态是“待审核”，需要等待审核，这也是该用户审核没有通过的原因。审核完成之后，才能提交试卷或阅卷、才能完成领队或者副领队、添加修改学生信息相关操作。'
elif len(user_id_returned_list) == 1:
    teacher_id = user_id_returned_list[0]['id']
    teacher_type = user_id_returned_list[0]['type'] # 仲裁，副领队，领队
    print(user_id_returned_list)
    sql_returned_str += '该用户在系统中、已经审核通过了，而且是{}。如果用户问道关于其身份的问题，就回答：您是{}。'.format(teacher_type, teacher_type)
prompt = "查询信息:" + sql_returned_str + "指令: 根据以上的查询信息，回答用户的问题。"\
                "不要增加额外的信息。确保回答是与查询信息一致的，而且不要输出错误或者多余的内容。"\
                    "如果用户的问题与查询到的信息无关，直接仅仅回答'未能查询到相关信息。'忽略与问题无关的查询结果。"\
                    "回答信息应当短小准确。使用中文回答，并且用“您”称呼提问者用户。"


question = '我审核通过了吗？'

prompt += '用户的问题：'+question+'回答：'

print("根据阅卷系统数据库的查询，编写的prompt为：")
print(prompt)