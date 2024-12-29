import streamlit as st
from get_user_data import get_user_profile, suggest_news

categories = [
    "business", "crime", "domestic", "education", "entertainment", "environment",
    "food", "health", "lifestyle", "politics", "science", "sports", "technology",
    "top", "tourism", "world"
]

st.title("Chatbot: Haber Öneri Sistemi")

user_id = st.text_input("Kullanıcı ID'nizi girin:", "user123")

user_input = st.text_input("Ne tür haberler ilgini çeker? (Örneğin: Spor, Teknoloji)")

if st.button("Haber Önerisi Al"):

    user_profile = get_user_profile(user_id)
    if user_input.lower() in categories:
        suggestion = suggest_news(user_profile)
        st.success(f"İlginizi çekebilecek bir haber önerisi: {suggestion}")
    else:
        st.warning("Başka bir kategori seçmek ister misiniz?")

#if st.checkbox("Kullanıcı geçmişini göster")
