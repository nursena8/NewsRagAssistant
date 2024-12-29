import bbc
import sqlite3

news_api = bbc.news.get_news(bbc.Languages.Turkish)

conn = sqlite3.connect("news.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    summary TEXT,
    image_link TEXT,
    news_link TEXT UNIQUE
)
""")
conn.commit()

news_data = bbc.news.get_latest_news(bbc.Languages.Turkish)  
for item in news_data:
    cursor.execute("""
    INSERT OR IGNORE INTO news (category, title, summary, image_link, news_link)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "Son Haberler", 
        item.get("title"),
        item.get("summary"),
        item.get("image_link"),
        item.get("news_link"),
    ))
print("Son haberler veritabanına kaydedildi.")

categories = news_api.news_categories()
for category in categories:
    print(f"Kategori işleniyor: {category}")
    section_news = news_api.news_category(category)
    for news_dict in section_news:
        cursor.execute("""
        INSERT OR IGNORE INTO news (category, title, summary, image_link, news_link)
        VALUES (?, ?, ?, ?, ?)
        """, (
            category, 
            news_dict.get("title"),
            news_dict.get("summary"),
            news_dict.get("image_link"),
            news_dict.get("news_link"),
        ))


conn.commit()
conn.close()
