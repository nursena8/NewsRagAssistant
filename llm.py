import sqlite3
from sentence_transformers import SentenceTransformer # text to vector
import numpy as np
from sentence_transformers.util import semantic_search #matching user query text
from transformers import T5ForConditionalGeneration, T5Tokenizer #text summary

conn = sqlite3.connect("news_database.db")
cursor = conn.cursor()

query = "SELECT title, link, description, pubDate,category,sentiment  FROM news"
cursor.execute(query)
rows = cursor.fetchall()

conn.close()

data = [
    {
        "text": f"{row[0]} - {row[2]} (Kategori: {row[4]}, Tarih: {row[3]}, Duygu: {row[5]})",
        "link": row[1]
    }
    for row in rows
]


retriever = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

corpus = [entry["text"] for entry in data]
corpus_embeddings = retriever.encode(corpus, convert_to_tensor=True)

print(corpus_embeddings.shape)  # (n_samples, embedding_dim)
query = "spor haberlerinde ne var ? "
query_embedding = retriever.encode(query, convert_to_tensor=True)  

hits = semantic_search(query_embedding, corpus_embeddings, top_k=1)
best_match_idx = hits[0][0]["corpus_id"]


retrieved_data = data[best_match_idx]
print(f"En iyi eşleşme: {retrieved_data}")


t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small",legacy=False)
input_text = f"Özetle: {retrieved_data['text']}"
input_ids = t5_tokenizer.encode(input_text, return_tensors="pt")
output_ids = t5_model.generate(input_ids, max_length=50, num_beams=4, early_stopping=True)

response = t5_tokenizer.decode(output_ids[0], skip_special_tokens=True)

print(f"Yanıt: {response}")

print(f"İlgili haber: {retrieved_data['link']}")

