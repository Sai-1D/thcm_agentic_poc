# src/vector_store/prepare_vector_store.py
import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRODUCT_FILE = BASE_DIR / "data" / "product_summary.csv"
TEMP_EMBEDDINGS_FILE = BASE_DIR / "data" / "embeddings_progress.json"
VECTOR_STORE_DIR = BASE_DIR / "data" / "faiss_index"

def get_embedder():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )

def load_embeddings(temp_embeddings_file):
    with open(temp_embeddings_file, 'r') as f:
        embeddings = json.load(f)
    print(f"Loaded {len(embeddings)} embeddings, dimension: {len(embeddings[0])}")
    return embeddings

def build_vector_store(product_file, temp_embeddings_file, vector_store_dir):
    # 1. Load product summaries
    df = pd.read_csv(product_file)

    # 2. Load precomputed embeddings
    embeddings = load_embeddings(temp_embeddings_file)  # list of lists

    # 3. Initialize embedder (needed for queries)
    embedder = get_embedder()

    # 4. Prepare text_embedding pairs (text, embedding)
    texts = df["Summary"].tolist()
    text_embeddings = list(zip(texts, embeddings))  # [(text, embedding), ...]

    # 5. Prepare IDs (Article Number) and optional metadata
    ids = df["Article Number"].tolist()
    metadatas = [{"id": article_number} for article_number in ids]

    # 6. Build FAISS vector store using precomputed embeddings
    vector_store = FAISS.from_embeddings(
        text_embeddings=text_embeddings,
        embedding=embedder,
        ids=ids,
        metadatas=metadatas
    )

    # 7. Save the FAISS index locally
    vector_store.save_local(vector_store_dir)
    print(f"FAISS vector store saved at {vector_store_dir}")

    return vector_store


def get_vector_store_retriever(vector_store_dir, search_type, top_k):
    # 1. Initialize embedder (needed for queries)
    embedder = get_embedder()

    # 2. Load the vector store from the local
    vector_store = FAISS.load_local(
        folder_path = vector_store_dir,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )

    # 3. Return the retriever
    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": top_k}
    )
    return retriever

if __name__ == "__main__":
    # vector_store = build_vector_store(PRODUCT_FILE, TEMP_EMBEDDINGS_FILE, VECTOR_STORE_DIR)
    retriever = get_vector_store_retriever(VECTOR_STORE_DIR, "similarity", 5)

    query = "I need to buy cover for machine"
    docs = retriever.invoke(query)

    for doc in docs:
        print("Article Number:", doc.metadata.get("id"))  # metadata contains your Article Number
        print("Summary:", doc.page_content)               # the actual text of the summary
        print("-" * 50)
