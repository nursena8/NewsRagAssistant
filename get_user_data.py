import sqlite3
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
        "preferred_categories": ["sports", "technology"], 
        "preferred_sentiment": "positive"  
    }

def suggest_news(user_profile):
    news_data = get_news_data()
    suggested_news = []

    for news in news_data:
        title, description, category = news
        if category in user_profile["preferred_categories"]:
            suggested_news.append(f"Kategori: {category}, Başlık: {title}")
    
    return random.choice(suggested_news) if suggested_news else "Uygun haber bulunamadı."