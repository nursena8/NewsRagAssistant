import sqlite3
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever
from langchain.schema.retriever import BaseRetriever
from pydantic import BaseModel, Field
from langchain.schema import Document
import os

def read_data_from_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, pubDate FROM news")
    rows = cursor.fetchall()
    conn.close()
    documents = [f"Başlık: {row[0]}, İçerik: {row[1]}, Tarih: {row[2]}" for row in rows]
    return documents

documents = read_data_from_sqlite("news_database.db")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts(documents, embedding_model)

bm25_retriever = BM25Retriever.from_texts(documents)
bm25_retriever.k= 2

ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, vectorstore.as_retriever(search_kwargs={"k": 2})], weights=[0.3, 0.7])

search = DuckDuckGoSearchAPIWrapper()
ddg_search_tool = DuckDuckGoSearchRun(api_wrapper=search)
ddg_search_results_tool = DuckDuckGoSearchResults(api_wrapper=search)

llm = GoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-1219", temperature=0)

template = """Aşağıdaki bağlamı kullanarak kullanıcı sorusunu cevapla.
Hem veritabanından hem de internetten getirilen en alakalı bilgileri birleştirerek cevap ver.
Cevabı 3-4 cümle içinde özetle.

Bağlam:
{context}

Soru: {question}
Cevap:
"""
prompt = PromptTemplate(template=template, input_variables=["context", "question"])

class HybridRetrieverWithInternet(BaseRetriever, BaseModel):
    ensemble_retriever: EnsembleRetriever = Field(...)
    search_tool: DuckDuckGoSearchRun = Field(...)
    search_results_tool: DuckDuckGoSearchResults = Field(...)
    
    def _search_internet(self, query):
        search_results = self.search_results_tool.run(query)
        print(f"İnternet Arama Sonuçları: {search_results}")
        return search_results

    def _get_relevant_documents(self, query):
        relevant_docs = self.ensemble_retriever.get_relevant_documents(query)
        print(f"Veritabanı Sonuçları: {relevant_docs}")

        search_results = self._search_internet(query)

        all_docs = relevant_docs
        if search_results:
            all_docs.append(Document(page_content=search_results))

        return all_docs

hybrid_retriever = HybridRetrieverWithInternet(ensemble_retriever=ensemble_retriever, search_tool=ddg_search_tool, search_results_tool=ddg_search_results_tool)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=hybrid_retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

def answer_question(question):
    result = qa_chain({"query": question})
    print("Cevap:", result["result"])
    print("Kaynak Dokümanlar:")
    if isinstance(result["source_documents"], str):
       print("İnternet Kaynakları:\n",result["source_documents"])
    else:
        for doc in result["source_documents"]:
            print(doc.page_content)


question = "son haberlerde ne var"
answer_question(question)
