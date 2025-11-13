import os
import json
from time import sleep
from dotenv import load_dotenv
import pandas as pd
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate

load_dotenv()
GROQ_API_KEY = os.environ['GROQ_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']


def get_summarizer_chain():
    # 1. define llm model
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=OPENAI_API_KEY
    )

    # 2. define summarization prompt
    prompt = PromptTemplate(
        input_variables=[
            "description", "identifier", "keywords", "price",
            "price_quantity", "sold_individually", "producttype",
            "height", "length", "operatingweight", "weight", "width"
        ],
        template="""
    You are a precise and factual product description generator for semantic embeddings.

    Your goal: generate a short, clean, factual paragraph describing the product using **only** the provided inputs.
    Preserve all meaningful details from `description`; never invent or exaggerate any information.

    ---

    ### Rules:
    - Clean the `identifier` before using it: remove special symbols like `*`, `;`, `/`, or extra spaces, but keep the text readable (e.g., "* ROLLER" → "ROLLER", "SEAL;RUBBER" → "SEAL RUBBER").
    - Begin the description with the cleaned identifier if available. If `description` exists, merge it naturally so that no details are lost.
    - Never add or assume any brand, feature, or claim not in the data.
    - If `producttype` exists, include it naturally (e.g., “spare part”, “component”).
    - If `sold_individually` is true or "True", include “sold individually”; otherwise omit.
    - If `price` exists, express it naturally (e.g., "priced at 0.0 INR per 1 EA (type N)").
    - Convert `price_quantity` into a natural phrase (“for 1 unit” or “for {price_quantity} units”).
    - Include height, length, weight, or operating weight only if available.
    - Use `keywords` only if they add clarity — never invent.
    - Do **not** show raw field names or placeholders.
    - Write 2–4 clear sentences suitable for product catalogs and semantic embeddings.

    ---

    ### Examples

    **Example 1:**
    identifier=COVER  
    price=0.0 INR:N::1 EA::  
    price_quantity=1.0  
    sold_individually=True  
    producttype=SpareParts  
    description=High-quality Tata Hitachi COVER spare part designed for durability and precise fit on compatible construction machinery models.

    Output:
    COVER is a Tata Hitachi spare part designed for durability and a precise fit on compatible construction machinery models. It belongs to the SpareParts category and is sold individually, priced at 0.0 INR per 1 EA (type N) for 1 unit.

    ---

    **Example 2:**
    identifier=SEAL;RUBBER  
    price=  
    price_quantity=1.0  
    sold_individually=True  
    producttype=SpareParts  
    description=High-quality rubber seal (P/N: SEAL;RUBBER) for Tata Hitachi construction machinery, providing superior sealing performance and reliability in various applications.

    Output:
    SEAL RUBBER is a high-quality rubber seal for Tata Hitachi construction machinery, providing reliable sealing performance. It is a SpareParts component sold individually for 1 unit.

    ---

    **Example 3:**
    identifier=* ROLLER  
    price=  
    price_quantity=1.0  
    sold_individually=True  
    producttype=SpareParts  
    description=High-quality Tata Hitachi spare part roller designed for durability and performance in construction machinery, compatible with various models.

    Output:
    ROLLER is a Tata Hitachi spare part designed for durability and strong performance in construction machinery. It belongs to the SpareParts category and is sold individually for 1 unit.

    ---

    **Example 4:**
    identifier=BUSHING;RUBBER  
    price=  
    price_quantity=1.0  
    sold_individually=True  
    producttype=SpareParts  
    description=High-quality Tata Hitachi rubber bushing (P/N: BUSHING;RUBBER) designed for durability and precision fit in compatible construction machinery models.

    Output:
    BUSHING RUBBER is a Tata Hitachi rubber bushing designed for durability and a precise fit in compatible construction machinery models. It is a SpareParts component sold individually for 1 unit.

    ---

    Now generate a factual, fluent, and semantically rich description using these inputs:

    Description: {description}  
    Identifier: {identifier}  
    Keywords: {keywords}  
    Price: {price}  
    Price quantity: {price_quantity}  
    Sold individually: {sold_individually}  
    Product type: {producttype}  
    Height: {height}  
    Length: {length}  
    Operating weight: {operatingweight}  
    Weight: {weight}  
    Width: {width}

    Output:
    Write one paragraph (2–4 sentences) that includes all relevant fields, removes unwanted symbols from identifiers, and never invents or omits factual data.
    """
    )

    # 3. contruct and return chain
    chain =  prompt | llm | StrOutputParser()
    return chain

def run_summarizer(df, chain, TEMP_FILE):
    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, "r") as f:
            summaries = json.load(f)
        start_index = len(summaries)
        print(f"Resuming from batch starting at index {start_index}")
    else:
        summaries = []
        start_index = 0
        print("Starting fresh")

    batch_size = 50  
    total_rows = len(df)
    for i in range(start_index, total_rows, batch_size):
        batch = []
        for _, row in df.iloc[i:i+batch_size].iterrows():
            inputs = {
                "description": row.get("description", ""),
                "identifier": row.get("Identifier", ""),
                "keywords": row.get("Keywords", ""),
                "price": row.get("Price", ""),
                "price_quantity": row.get("Price quantity", ""),
                "sold_individually": row.get("Sold individually", ""),
                "producttype": row.get("productType", ""),
                "height": row.get("height", ""),
                "length": row.get("length", ""),
                "operatingweight": row.get("operatingWeight", ""),
                "weight": row.get("weight", ""),
                "width": row.get("width", "")
            }
            batch.append(inputs)

        try:
            batch_summaries = chain.batch(batch)
            summaries.extend([s.strip() for s in batch_summaries])

            with open(TEMP_FILE, "w") as f:
                json.dump(summaries, f, indent=2)

            print(f"Processed {i + len(batch)} / {total_rows} rows — saved progress")

            sleep(2)

        except Exception as e:
            print(f"Error at batch starting {i}: {e}")
            print("Sleeping for 10s before retry...")
            sleep(10)
            continue

    print("\nAll summaries processed successfully!")

def save_summaries_with_article_number(temp_file, read_file_path, write_file_path):
    # 1. Load summaries from temp file
    with open(temp_file, "r") as f:
        summaries = json.load(f)

    # 2. Load original CSV to get article numbers
    df_original = pd.read_csv(read_file_path)

    # 3. Check for length mismatch
    if len(df_original) != len(summaries):
        print("Warning: Number of summaries does not match number of original rows.")

    # 4. Combine article_number and summaries
    df_output = pd.DataFrame({
        "Article Number": df_original.get("Article Number", ""),
        "Summary": summaries
    })

    # 5. Save to CSV
    df_output.to_csv(write_file_path, index=False)
    print(f"Summaries saved with article_number to {write_file_path}")

READ_FILE_PATH = '/Users/admin/Desktop/one_digitals/thcm/thcm_poc/thcm_agentic_poc/data/product_catalog_updated.csv'
WRITE_FILE_PATH = '/Users/admin/Desktop/one_digitals/thcm/thcm_poc/thcm_agentic_poc/data/product_summary.csv'
TEMP_FILE = '/Users/admin/Desktop/one_digitals/thcm/thcm_poc/thcm_agentic_poc/data/summary_progress.json'

df_original = pd.read_csv(READ_FILE_PATH)
# summarizer_chain = get_summarizer_chain()
# run_summarizer(df_original, summarizer_chain)
# save_summaries_with_article_number(TEMP_FILE, READ_FILE_PATH, WRITE_FILE_PATH)

