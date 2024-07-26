from db_api import *
class GetExamInfo(CustomOperation):
    def __init__(self):
        self.MySQLCommand = "select * from cmf_tp_exam where `status` = 2 ; "
    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            returned = cursor.fetchall()
            if len(returned) >= 2:
                raise Exception("There are more than one activated exam in the database.")
            elif len(returned) == 0:
                return None
            else:
                return returned[0][1], '已分配' if returned[0][3] == 2 else '未分配'
            
        except Exception as e:
            print(e)
            raise e