# 使用一个google训练的语言模型，在文档中搜索匹配相应的段落。
# 匹配时会使用语义信息，比较复杂。
import fitz
# import re
import numpy as np
import tensorflow_hub as hub
import tensorflow_text
import gradio as gr
import os
import regex as re
from sklearn.neighbors import NearestNeighbors
class SemanticSearch:
    def __init__(self):
        if os.path.exists('./universal-sentence-encoder-multilingual'):
            self.use = hub.load('./universal-sentence-encoder-multilingual')
        else:
            print('Directly download from web. If this is not your intention, please place the model at ./universal-sentence-encoder-multilingual')
            self.use = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
        self.fitted = False
    
    def fit(self, data, batch=600, n_neighbors=4):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True
    
    
    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]
        
        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors
    
    
    def get_text_embedding(self, texts, batch=600):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i:(i+batch)]
            emb_batch = self.use(text_batch)
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
def text_to_chunks(texts, word_length=40, start_page=1):
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
            chunk = f'[{idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks
def load_recommender(recommender, path, start_page=1):
    # global recommender
    texts = pdf_to_text(path, start_page=start_page)
    chunks = text_to_chunks(texts, start_page=start_page)
    recommender.fit(chunks)
    return 'Corpus Loaded.'
# pdf_path = 'references\\学校老师小程序使用指南230323.pdf'
# assert pdf_path is not None,'pdf_path is None'
# load_recommender(recommender, pdf_path)