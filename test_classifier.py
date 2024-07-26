
from utils.utils import classification_whole, classification_question
TRY_NUM =2

nickname_and_question_list = []
with open('frequent_requests/questions.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        nickname_and_question_list.append(line.strip().split('|'))

print(nickname_and_question_list)

answers_for_all_nickname_and_question = []
for nickname_and_question in nickname_and_question_list:
    answers_for_this_nickname_and_question = []
    for _ in range(TRY_NUM):
        print(nickname_and_question[1])
        b = classification_question(nickname_and_question[1])
        print(b)