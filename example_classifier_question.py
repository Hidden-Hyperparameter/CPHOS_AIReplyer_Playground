from utils.utils import classification_question
glm_api_key = '76ac5e2039ac8a8da4bd924957e03b20.kJAQi8ptu0ynObZr'

question = '我怎么看试卷'

class1 = classification_question(question)

print(class1)