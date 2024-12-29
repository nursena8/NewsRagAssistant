'''
'''
import schedule
import time
import sqlite3
import requests
from textblob import TextBlob
import json
class NewsFetcherAgent:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url

    def fetch_news(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            news_data = response.json().get('results', [])
            print("Total news fetched:", len(news_data))   
            return news_data
        else:
            print("error fetching news.")

class NewsAnalysisAgent:
    def analyze_sentiment(self, news_list):
        for news in news_list:
            sentiment = TextBlob(news['title']).sentiment.polarity
            news['sentiment'] = 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'
        return news_list


class NewsDistributionAgent:
    def distribute(self, news_list):
        conn = sqlite3.connect('news_database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    article_id TEXT PRIMARY KEY,
                    title TEXT,
                    link TEXT,
                    description TEXT,
                    pubDate TEXT,
                    category TEXT,
                    sentiment TEXT
                    
                )
            ''')
        except Exception as e:
            print(f"Error creating table: {e}")
            return


        for news in news_list:
            cursor.execute("SELECT COUNT(*) FROM news WHERE article_id = ?", (news['article_id'],))
            count = cursor.fetchone()[0]

            if count == 0:
                category = ', '.join(news.get('category', ['N/A'])) if isinstance(news.get('category'), list) else news.get('category', 'N/A')
                cursor.execute('''
                INSERT INTO news (article_id, title, link, description, pubDate, category, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news['article_id'],
                    news['title'],
                    news['link'],
                    news['description'],
                    news['pubDate'],
                    category,
                    news.get('sentiment', 'N/A')
                    

                ))
                print(f"News with ID {news['article_id']} added to database.")
            else:
                print(f"News with ID {news['article_id']} already exists in the database.")

        conn.commit()
        conn.close()


api_key = 'pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751'
#url = f"https://newsdata.io/api/1/latest?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=en"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=tr"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=en&category=technology"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=en&category=education"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=tr&category=sports"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=en&category=business&country=us"
url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=tr&category=sports"
#url = f"https://newsdata.io/api/1/news?apikey=pub_62732dec8cc1ebecf8e4a6c66aee1b8f04751&language=en&category=education&country=us"


fetcher = NewsFetcherAgent(api_key, url)
analyzer = NewsAnalysisAgent()
distributor = NewsDistributionAgent()
news = fetcher.fetch_news()
analyzed_news = analyzer.analyze_sentiment(news)
distributor.distribute(analyzed_news)

fetcher = NewsFetcherAgent(api_key, url)
analyzer = NewsAnalysisAgent()
distributor = NewsDistributionAgent()

news = fetcher.fetch_news()


#schedule.every().day.at("00:00").do(job) #request every day
    
#while True:
#    schedule.run_pending()  
#   time.sleep(5)  #controlling in two minutes

