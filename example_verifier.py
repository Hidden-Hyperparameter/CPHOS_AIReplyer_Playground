from utils.utils import verification
glm_api_key = '76ac5e2039ac8a8da4bd924957e03b20.kJAQi8ptu0ynObZr'

question = '我想吃饭'
answer = '我在上课'
Is_reasonable = verification(question, answer)

print(Is_reasonable)