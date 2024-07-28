import os

teacher_problem_example = '我应该怎么阅卷？' #老师的问题

from .search_pdf_utils import SemanticSearch, load_recommender #引入相关的工具
# from utils.utils import summarization
recommender_1 = SemanticSearch()
pdf_path = os.path.join('references','marking.pdf')
load_recommender(recommender_1, pdf_path)
#初始化一个recommender_1， 这个recommender_1负责这个pdf的推荐。你可以使用多个pdf，不过我认为更简单的是把不同的材料都集中到一个pdf中，然后用一个recommender.

topn_chunks = recommender_1(teacher_problem_example)
#调用recommender_1他本身的__call__方法，传入问题字符串，返回pdf中相关的一些片段字符串组成的list。

for result_str in topn_chunks:
    print(result_str)
    print("\n\n\n")
    
# answer = summarization(teacher_problem_example, topn_chunks)
# print(answer)