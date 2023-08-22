# bert_utils.py

from sentence_transformers import SentenceTransformer
import nltk
import numpy as np

# Load the pre-trained model
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_mean_embedding(row):
    review = row
    review_sentances = nltk.sent_tokenize(review)

    embeddings = bert_model.encode(review_sentances)

    mean_embeddings =  np.mean(embeddings, axis=0)
    return mean_embeddings

def generate_bert_embeddings(review_text):
    mean_embeddings = generate_mean_embedding(review_text)
    return mean_embeddings
