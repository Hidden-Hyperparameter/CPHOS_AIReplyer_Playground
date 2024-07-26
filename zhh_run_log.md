# Environment

# Run Programs

## db_api

```shell
python example_db_api.py
```

Output:

```
CustomTransaction init
Please enter the following database information:
host: 47.94.223.188
port: 3306
user: dz161_2
db: dz161_2
Connect to database successfully.
The tables in the database are:
(('cmf_admin_menu',), ('cmf_asset',), ('cmf_auth_access',), ('cmf_auth_rule',), ('cmf_comment',), ('cmf_hook',), ('cmf_hook_plugin',), ('cmf_link',), ('cmf_nav',), ('cmf_nav_menu',), ('cmf_option',), ('cmf_plugin',), ('cmf_recycle_bin',), ('cmf_role',), ('cmf_role_user',), ('cmf_route',), ('cmf_slide',), ('cmf_slide_item',), ('cmf_theme',), ('cmf_theme_file',), ('cmf_third_party_user',), ('cmf_tp_arbitrator',), ('cmf_tp_area',), ('cmf_tp_correct',), ('cmf_tp_correct_copy',), ('cmf_tp_correct_copy1',), ('cmf_tp_exam',), ('cmf_tp_grade',), ('cmf_tp_member',), ('cmf_tp_prize',), ('cmf_tp_record',), ('cmf_tp_school',), ('cmf_tp_set',), ('cmf_tp_student',), ('cmf_tp_subject',), ('cmf_tp_test_paper',), ('cmf_tp_topic',), ('cmf_user',), ('cmf_user_action',), ('cmf_user_action_log',), ('cmf_user_balance_log',), ('cmf_user_favorite',), ('cmf_user_like',), ('cmf_user_login_attempt',), ('cmf_user_score_log',), ('cmf_user_token',), ('cmf_verification_code',))
[{'id': 1601, 'p_id': 0, 'wechat_nickname': '史景喆', 'user_name': '史景喆', 'school_id': '174', 'upload_limit': 100, 'viewing_problem': 10, 'type': '领队'}]
根据阅卷系统数据库的查询，编写的prompt为：
查询信息:该用户在系统中、已经审核通过了，而且是领队。如果用户问道关于其身份的问题，就回答：您是领队。指令: 根据以上的查询信息，回答用户的问题。不要增加额外的信息。确保回答是与查询信息一致的，而且不要输出错误或者多余的内容。如果用户的问题与查询到的信息无关，直接仅仅回答'未能查询到相关信息。'忽略与问题无关的查询结果。回答信息应当短小准确。使用中文回答，并且用“您”称呼提问者用户。用户的问题：我审核通过了吗？回答：
Notice that you have not rollBack or commited the transaction yet.
Quit without commiting. Roll back.
You must call customTransaction.commit() to commit your changes
```

## search_pdf_utils

```shell
python example_search_pdf.py
```

Output:

```
(Tensorflow init logs omitted)
[2] "2 老师阅卷时的问题为什么我没上传试卷却有阅卷任务？ 这个问题的答案因为您团队中有领队或其他副领队上传了试卷，你们是共享这些阅卷 任务的。 |||"




[1] "1 以下是一些有关老师阅卷时的阅卷的问题，以及答案: 老师阅卷时的问题我该如何阅卷？ 这个问题的答案打开CPHOS 官方小程序，点击“首页”->“阅卷中心” ，请确认“当前考 试”与“批改题号”均为正确内容，未批改完毕时请为小程序中分配的试 题按照评分标准打分 评分标准: 若小问为解答题，计算结果正确，解题过程无误给满分，若 和答案方法不一致请上报组委会仲裁; 结果不正确， 若评分标准只有一 种方法，按照评分标准给出的得分方程逐个判定过程是否有效，对解 答中体现的有效方程给分，若评分标准有多种方法，取多种方法中答 题者得分最多的方法给分若小问为证明题，要求按照评分标准给出的 得分方程逐个判定过程是否有效，对解答中体现的有效方程给分，若 评分标准有多种方法， 取多种方法中答题者得分最多的方法给分; 若采 用了评分标准中没有的方法，且言之有理，也请上报组委会 对于每一题将批改分数填至“得分”一栏，然后点击“Next”将结果传至 服务器并获取下一道题目。若判卷过程中认为存在误判可点击“Back” 回到误判的题目修改“得分”中的给分并点击“Next”将结果传至服务器。 当“未批”一栏为“0”或者为“—”时，说明您这一组用户分配到的阅卷任 务已完成。 ||| 老师阅卷时的问题为什么我要批改的卷子这么多？ 这个问题的答案试卷分配是按照特定规则公平分配的，您若觉得阅卷量异常，请咨询 人工服务，及时联系CPHOS 技术组。 ||| 老师阅卷时的问题可以让学生帮我阅卷吗？ 这个问题的答案原则上阅卷工作得有领队一人完成。如果您觉得阅卷量过大，您可以 向技术组申请，我们将开放副领队的阅卷权限。问了保证公平性以及 阅卷质量，我们不建议让学生进行阅卷。如有发现，CPHOS 可能将进 行警告、禁赛处等分。 |||"



```

## glm_utils

```shell
python example_glm.py
```

Output:

```
" 您是领队。"
```

## gpt_utils

```shell
python example_gpt.py
```

Output:

```
您是领队。
```

