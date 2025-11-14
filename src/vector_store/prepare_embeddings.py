# src.vector_store.prepare_embeddings.py
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # go from src/vector_store → src → thcm_agentic_poc
PRODUCT_FILE = BASE_DIR / "data" / "product_summary.csv"
TEMP_EMBEDDINGS_FILE = BASE_DIR / "data" / "embeddings_progress.json"

def get_embedder():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
    )

def generate_embeddings(product_file, temp_embeddings_file):
    # 1. Read the file
    product_summary_df = pd.read_csv(product_file)
    
    # 2. initialize embedder
    embedder = get_embedder()

    # 3. Take out the summaries
    summaries = product_summary_df["Summary"].tolist()

    # 4. Create embeddings for the summary
    embeddings = embedder.embed_documents(summaries)

    # 5. Save it in a file
    with open(temp_embeddings_file, "w") as f:
        json.dump(embeddings, f)

    print(f"Saved {len(embeddings)} embeddings to {temp_embeddings_file}")

def get_temp_embeddings_file_info(temp_embeddings_file):
    with open(temp_embeddings_file, 'r') as f:
        emb = json.load(f)

    print(f"Total embeddings: {len(emb)}, Dimension of each embedding: {len(emb[0])}")

def save_embeddings(product_file, temp_embeddings_file, output_file=None):
    # 1. Read the summaries CSV
    product_summary_df = pd.read_csv(product_file)

    # 2. Load embeddings stored earlier
    with open(temp_embeddings_file, 'r') as f:
        emb_lst = json.load(f)

    # 3. Validate
    if len(emb_lst) != len(product_summary_df):
        raise ValueError(
            f"Embedding count ({len(emb_lst)}) does not match row count ({len(product_summary_df)})"
        )

    # 4. Add embeddings to dataframe
    product_summary_df["Embeddings"] = emb_lst
    print(product_summary_df.head(2))

    # 5. Decide output file
    if output_file is None:
        output_file = product_file  # overwrite original

    # 6. Save updated CSV
    product_summary_df.to_csv(output_file, index=False)

    print(f"Embeddings added and saved to: {output_file}")


# generate_embeddings(PRODUCT_FILE, TEMP_EMBEDDINGS_FILE)
# get_temp_embeddings_file_info(TEMP_EMBEDDINGS_FILE)
# save_embeddings(PRODUCT_FILE, TEMP_EMBEDDINGS_FILE)