# the user_wechat_nicknames.txt file contains user_nicknames. read them into a list.

from .work_file import answer_user_question
import os
TRY_NUM = 1

nickname_and_question_list = []
with open(os.path.join(os.path.dirname(__file__),'frequent_requests/questions.txt'), 'r', encoding='utf-8') as f:
    for line in f.readlines():
        nickname_and_question_list.append(line.strip().split('|'))

print(nickname_and_question_list)

answers_for_all_nickname_and_question = []
for nickname_and_question in nickname_and_question_list:
    answers_for_this_nickname_and_question = []
    for _ in range(TRY_NUM):
        answers_for_this_nickname_and_question.append(answer_user_question(nickname_and_question[0], nickname_and_question[1]))
    answers_for_all_nickname_and_question.append(answers_for_this_nickname_and_question)
# output the result into an output_file:
# each (1+TRY_NUM) line is a group. The first line is the nickname and question, the following TRY_NUM lines are the answers.
# if not exists, create the file.
with open(os.path.join(os.path.dirname(__file__),'answers.txt'), 'w', encoding='utf-8') as f:
    for nickname_and_question, answers in zip(nickname_and_question_list, answers_for_all_nickname_and_question):
        f.write(nickname_and_question[0] + '|' + nickname_and_question[1] + '|回答为：\n')
        for answer in answers:
            f.write('\t'+answer + '\n')
        f.write('\n')
