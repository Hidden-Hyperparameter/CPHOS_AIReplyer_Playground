# 使用一个google训练的语言模型，在文档中搜索匹配相应的段落。
# 匹配时会使用语义信息，比较复杂。
import fitz
# import re
import numpy as np
import sys,os
from .utils.logger import logger
import tensorflow_hub as hub
import tensorflow_text
import yaml
# import gradio as gr
import os
import regex as re
from sklearn.neighbors import NearestNeighbors
from typing import List
class SemanticSearch:
    def __init__(self):
        try_dirs = os.walk('..')
        names = [i[0] for i in try_dirs]
        found = any(['universal-sentence-encoder-multilingual' in n for n in names])
        if found:
            use_path = [n for n in names if n.strip('/').endswith('universal-sentence-encoder-multilingual')][0]
            self.use = hub.load(use_path)
        else:
            logger.warn('Directly download from web. If this is not your intention, please place the model at ./universal-sentence-encoder-multilingual')
            self.use = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
        self.fitted = False
    
    def fit(self, data, batch=600, n_neighbors=2):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors,metric='cosine')
        self.nn.fit(self.embeddings)
        self.fitted = True
    
    
    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]
        
        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors
    
    
    def get_text_embedding(self, texts:List[str], batch=600):
        embeddings = []
        emb_batch = self.use(texts)
        embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings
# print("Loading model...")
# recommender = SemanticSearch()
# print("Loading data...")
def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text
def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page-1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list

def yml_to_chunks(path, word_length=40) -> List[str]:
    dic = yaml.load(open(path, 'r'), Loader=yaml.FullLoader)
    content = dic['content']
    return ['Q:'+x['Q'] + 'A:' + x['A'] for x in content]
    pass

def text_to_chunks(texts, word_length=40, start_page=1) -> List[str]:
    text_toks = [t.split(' ') for t in texts]
    page_nums = []
    chunks = []
    
    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i:i+word_length]
            if (i+word_length) > len(words) and (len(chunk) < word_length) and (
                len(text_toks) != (idx+1)):
                text_toks[idx+1] = chunk + text_toks[idx+1]
                continue
            chunk = ' '.join(chunk).strip()
            # chunk = f'[{idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks
def load_recommender(recommender, file_name_without_suffix, start_page=1):
    # global recommender
    chunks = None
    if os.path.exists(file_name_without_suffix + '.yml'):
        chunks = yml_to_chunks(file_name_without_suffix + '.yml')
    elif os.path.exists(file_name_without_suffix + '.pdf'):
        texts = pdf_to_text(file_name_without_suffix + '.pdf', start_page=start_page)
        chunks = text_to_chunks(texts, start_page=start_page)
    else: 
        raise FileNotFoundError('Neither .yml nor .pdf file found:',file_name_without_suffix)
    recommender.fit(chunks)
    return 'Corpus Loaded.'
# pdf_path = 'references\\学校老师小程序使用指南230323.pdf'
# assert pdf_path is not None,'pdf_path is None'
# load_recommender(recommender, pdf_path)
if __name__ == '__main__':
    s = SemanticSearch()
    load_recommender(s,os.path.join(os.path.dirname(__file__),'references','offseason_problems'))
    topn_chunks = s('如何参与CPHOS')
    for result_str in topn_chunks:
        print(result_str)
        print("\n===\n")
    s = SemanticSearch()
    load_recommender(s,os.path.join(os.path.dirname(__file__),'references','marking'))
    topn_chunks = s('修改学生信息')
    for result_str in topn_chunks:
        print(result_str)
        print("\n===\n")