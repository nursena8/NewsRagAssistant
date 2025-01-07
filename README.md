# RAG Model for Question Answering System
![Zihin Haritası Beyin Fırtınası](https://github.com/user-attachments/assets/05094d46-4faf-4c71-8354-5c695a3565e0)

This project implements a **Retrieval-Augmented Generation (RAG)** model to provide answers to user queries by combining relevant data from both a local database (SQLite) and the internet. The model leverages various tools and technologies for document retrieval, embedding generation, and query answering.

## Technologies Used

- **SQLite**: Database for storing and retrieving news articles.
- **LangChain**: Framework for building the retrieval-augmented generation (RAG) pipeline.
  - **FAISS**: Used to perform efficient similarity search for embedding-based retrieval.
  - **BM25Retriever**: A classical IR technique used to retrieve relevant documents from a corpus.
  - **EnsembleRetriever**: Combines multiple retrievers to improve the quality of results.
  - **DuckDuckGoSearchAPIWrapper**: Performs internet searches to gather additional information when necessary.
- **HuggingFace Embeddings**: Used to generate dense vector embeddings for documents.
- **GoogleGenerativeAI**: A generative AI model that is used for answering queries based on the retrieved context.

## Model Workflow

1. **Document Retrieval**:
   - The system first retrieves relevant documents from a local SQLite database (`news_database.db`).
   - The documents are embedded using a pre-trained model (`sentence-transformers/all-MiniLM-L6-v2`), and stored in a FAISS index for efficient similarity search.
   - Additionally, BM25 retrieval is used as an alternative to retrieve documents based on classical keyword matching.
   
2. **Ensemble Retrieval**:
   - An `EnsembleRetriever` is used to combine the BM25 retriever and FAISS retriever, with the goal of improving retrieval quality. The ensemble uses a weight of 0.3 for BM25 and 0.7 for FAISS.
   
3. **Internet Search**:
   - If the local document retrieval does not provide sufficient information, the system uses the **DuckDuckGo** API to search the internet and fetch additional relevant content.
   
4. **Query Answering**:
   - The retrieved documents (from both the database and the internet) are fed into a language model (`GoogleGenerativeAI`), which generates a concise answer.
   - The answer is summarized in 3-4 sentences, drawing from both the local and internet context.
