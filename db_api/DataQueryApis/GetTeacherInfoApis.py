#CustomOperation is defined in db_api\CustomOperation.py
from db_api import *
typedict={2:'仲裁',3:'副领队',1:'领队'}
class GetAllTeacherInfo(CustomOperation):
    def __init__(self):
        super().__init__()
        self.MySQLCommand = "select * from cmf_tp_member where status != 0"
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'p_id':item[1],'wechat_nickname':item[3],'user_name':item[-7],'school_id':item[-6],'upload_limit':item[-2],'viewing_problem':item[-5],'type':typedict[item[-3]]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e
class GetTeacherInfoByName(CustomOperation):
    def __init__(self, Name:str):
        super().__init__()
        self.MySQLCommand = "select * from cmf_tp_member where user_name = '%s' and status != 0 " % Name
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'p_id':item[1],'wechat_nickname':item[3],'user_name':item[-7],'school_id':item[-6],'upload_limit':item[-2],'viewing_problem':item[-5],'type':typedict[item[-3]]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e
class GetTeacherInfoByWechatName(CustomOperation):
    def __init__(self, Name:str):
        super().__init__()
        self.MySQLCommand = "select * from cmf_tp_member where `nickname` = '%s' and status != 0" % Name
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'p_id':item[1],'wechat_nickname':item[3],'user_name':item[-7],'school_id':item[-6],'upload_limit':item[-2],'viewing_problem':item[-5],'type':typedict[item[-3]]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e
class GetTeacherInfoByFlexibleName(CustomOperation):
    def __init__(self, Name:str):
        '''
        Name: str
        return: list, each element is a dictionary.
            item in list: dictionary with 
        '''
        super().__init__()
        self.MySQLCommand = "select * from cmf_tp_member where user_name like '%%%s%%' and status != 0" % Name
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'p_id':item[1],'wechat_nickname':item[3],'user_name':item[-7],'school_id':item[-6],'upload_limit':item[-2],'viewing_problem':item[-5],'type':typedict[item[-3]]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e

class GetTeacherInfoBySchoolId(CustomOperation):
    def __init__(self,SchoolId:int):
        self.MySQLCommand = "select * from cmf_tp_member where school_id = %d and status != 0" % SchoolId
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'p_id':item[1],'wechat_nickname':item[3],'user_name':item[-7],'school_id':item[-6],'upload_limit':item[-2],'viewing_problem':item[-5],'type':typedict[item[-3]]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e

class GetToBeVerifiedTeacherInfoByWechatName(CustomOperation):
    def __init__(self, WechatName:str):
        self.MySQLCommand = "select * from cmf_tp_member where `nickname` = \'{}\' and status = 0".format(WechatName)
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'wechat_nickname':item[3]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e

class GetToBeVerifiedTeacherInfoByFlexibleWechatName(CustomOperation):
    def __init__(self, WechatName:str):
        self.MySQLCommand = "select * from cmf_tp_member where `nickname` like \'%{}%\' and status = 0".format(WechatName)
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            returned_lst = []
            for item in returned:
                returned_lst.append({'id':item[0],'wechat_nickname':item[3]})
            return returned_lst
        except Exception as e:
            print(e)
            raise e

class GetTeacherNotViewdProblemNumber(CustomOperation):
    def __init__(self,TeacherId:int):
        self.TeacherId = TeacherId
        self.MySQLCommand = None
    def execute(self,cursor:pymysql.cursors.Cursor):
        try:
            cursor.execute("select * from cmf_tp_member where id = %i and status != 0" % self.TeacherId)
            result = cursor.fetchall()
            if len(result) == 0:
                raise Exception("No such Teacher!")
            if len(result) > 1:
                raise Exception("More than one Teacher!")
            teacher_type = result[0][-3]
            cursor.execute("select * from cmf_tp_exam where status = 2")
            exam_id = cursor.fetchall()
            if len(exam_id) >= 1:
                if len(exam_id)>1:
                    raise Exception("What is happening? Two tests are happening!")
                exam_id = exam_id[0][0]
                cursor.execute("select count(*) from cmf_tp_correct as a join cmf_tp_subject as b on a.p_id = b.id join cmf_tp_test_paper as c on b.p_id = c.id where c.p_id = {} and a.user_id = {} and a.status = 1".format(exam_id, self.TeacherId))
                returned = cursor.fetchall()
                return returned[0][0], teacher_type # This is an int number, and an int number. The first int is number of problems not viewed, the second is the teacher type.
            else:
                raise Exception("No tests are happening!")
        except Exception as e:
            print(e)
            raise e
            