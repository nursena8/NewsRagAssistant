import sqlite3
from sentence_transformers import SentenceTransformer
from transformers import T5ForConditionalGeneration, T5Tokenizer
import random

def get_news_data():
    conn = sqlite3.connect("news_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, category FROM news")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_profile(user_id):
    return {
        "preferred_categories": ["sports", "tech"],  # Kullanıcının tercih ettiği kategoriler
        "preferred_sentiment": "positive"  # Kullanıcının tercih ettiği duygu
    }

# Haber önerisi yapma
def suggest_news(user_profile):
    news_data = get_news_data()
    suggested_news = []

    # Kullanıcının tercih ettiği kategorilere göre haber önerisi yap
    for news in news_data:
        title, description, category = news
        if category in user_profile["preferred_categories"]:
            suggested_news.append(f"Kategori: {category}, Başlık: {title}")
    
    return random.choice(suggested_news)

def chatbot(user_id):
    user_profile = get_user_profile(user_id)
    
    user_input = input("Ne tür haberler ilgini çeker? (Örneğin: Spor, Teknoloji): ")
    if user_input.lower() in ["spor", "teknoloji"]:
        print(f"İlginizi çekecek bir haber önerisi: {suggest_news(user_profile)}")
    else:
        print("Başka bir kategori seçmek ister misiniz?")

user_id = "user123"  
chatbot(user_id)