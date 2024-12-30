import streamlit as st
import sqlite3
import random
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search
from transformers import T5ForConditionalGeneration, T5Tokenizer

conn = sqlite3.connect("api/news_database.db")
cursor = conn.cursor()

def save_user_preferences(user_id, category, sentiment):
    cursor.execute("""
        INSERT OR REPLACE INTO user_preferences (user_id, preferred_category, preferred_sentiment)
        VALUES (?, ?, ?)
    """, (user_id, category, sentiment))
    conn.commit()

def get_user_preferences(user_id):
    cursor.execute("SELECT preferred_category, preferred_sentiment FROM user_preferences WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return {"preferred_category": result[0], "preferred_sentiment": result[1]}
    else:
        return None

cursor.execute("SELECT title, link, description, pubDate, category, sentiment FROM news")
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

t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=False)

st.title("Chatbot: Haber Öneri Sistemi")

user_id = st.text_input("Kullanıcı ID'nizi girin:", "user123")
user_category = st.text_input("Ne tür haberler ilgini çeker? (Örneğin: Spor, Teknoloji)")
user_sentiment = st.radio("Hangi tür haberleri görmek istersiniz?", ("Olumlu", "Olumsuz"))

if st.button("Kaydet ve Haber Önerisi Al"):
    save_user_preferences(user_id, user_category, user_sentiment)

    user_preferences = get_user_preferences(user_id)
    
    if user_preferences:
        st.success(f"Kullanıcı tercihleriniz kaydedildi: {user_preferences}")
        
        query = user_category if user_category else "top"
        query_embedding = retriever.encode(query, convert_to_tensor=True)
        hits = semantic_search(query_embedding, corpus_embeddings, top_k=1)
        best_match_idx = hits[0][0]["corpus_id"]
        best_match = data[best_match_idx]
        
        input_text = f"Özetle: {best_match['text']}"
        input_ids = t5_tokenizer.encode(input_text, return_tensors="pt")
        output_ids = t5_model.generate(input_ids, max_length=50, num_beams=4, early_stopping=True)
        summary = t5_tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        st.write(f"**Başlık:** {best_match['text']}")
        st.write(f"**Özet:** {summary}")
        st.write(f"[İlgili haber linki]({best_match['link']})")
    else:
        st.warning("Kullanıcı tercihleriniz bulunamadı.")