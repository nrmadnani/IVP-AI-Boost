from openai.resources.chat.completions import Completions
from pathlib import Path
original_create = Completions.create

def patched_create(self, *args, **kwargs):
    kwargs.pop("store", None)  # 🔴 REMOVE unsupported param
    return original_create(self, *args, **kwargs)

Completions.create = patched_create

from mem0 import Memory
import pandas as pd
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0 import Memory
import os
from dotenv import load_dotenv

load_dotenv()

memory = Memory.from_config({
    "llm": {
        "provider": "openai",
        "config": {
            "model": "finathon-gpt-5.1-chat",
            "temperature": 0.1,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "openai_base_url": os.getenv("OPENAI_ENDPOINT")   # 👈 IMPORTANT
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "finathon-text-embedding-3-large",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "openai_base_url": os.getenv("OPENAI_ENDPOINT")   # 👈 IMPORTANT
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "kmr_memory",
            "path": "./vectorstore/chromadb"
        }
    }
})

import pandas as pd
import math


def clean_record(record: dict) -> dict:
    cleaned = {}
    for k, v in record.items():
        if isinstance(v, float) and math.isnan(v):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def build_text_from_dynamic_columns(record: dict) -> str:
    """
    Dynamically builds structured text using ALL columns
    """
    lines = []

    for col, val in record.items():
        if val is None or val == "":
            continue

        col_clean = str(col).strip()
        val_clean = str(val).strip()

        lines.append(f"{col_clean}: {val_clean}")

    return "\n".join(lines)


def build_metadata(record: dict, file_path: str, idx: int, namespace: str) -> dict:
    """
    Flexible metadata extraction without assuming fixed schema
    """

    def safe_get(keys):
        for k in keys:
            if k in record and record[k]:
                return str(record[k])
        return ""

    return {
        "source": file_path,
        "row_id": int(idx),
        "namespace": namespace,

        # 🔥 intelligent fallback mapping
        "client": safe_get(["Client Name", "Client", "Customer"]),
        "status": safe_get(["Project Status", "Status"]),
        "owner": safe_get(["KM SPOC", "Owner", "Manager"]),
    }


def ingest_xlsx_to_memory(memory, file_path: str, namespace: str):
    df = pd.read_excel(file_path, header=0)  # ✅ first row = headers

    for idx, row in df.iterrows():
        record = clean_record(row.to_dict())

        # ✅ ONE ROW → ONE MEMORY ENTRY
        text = build_text_from_dynamic_columns(record)

        metadata = build_metadata(record, file_path, idx, namespace)
        print(text)
        print(metadata)
        print('***************************')
        memory.add(
        agent_id="123",
        messages=[
            {
                "role": "system",
                "content": ("This is structured database ingestion.\n",
                "Do NOT extract multiple memories.\n",
                "Store as ONE single memory entry.\n\n",
                f"{text}")
            }
        ],
        metadata=metadata
        )

def test_memory(memory):
    print("\n🔍 Running test queries...\n")

    queries = [
        "Apollo",
        "completed projects",
        "who is the owner",
        "projects using C#",
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        results = memory.search(q, limit=3, agent_id="123")

        if not results:
            print("No results found")
            continue
        print(results)
import chromadb
if __name__ == "__main__":
    EXCEL_FILE = r"C:\Users\nrmadnani\Downloads\Consulting - KM Repository.xlsx"
    ingest_xlsx_to_memory(memory=memory,file_path=EXCEL_FILE, namespace=Path(EXCEL_FILE).stem)
    # test_memory(memory=memory)

    # client = chromadb.PersistentClient(path="./vectorstore/chroma_db")

    vectorstore = memory.vector_store
    collection = vectorstore.collection
    print(collection)
    
    data = collection.get(limit=5)
    print(data)
    # def inspect_one_record(collection):
    #     data = collection.get(limit=1)

    #     print("\n🧠 ID:", data["ids"][0])
    #     print("\n📄 TEXT:\n", data["documents"][0])
    #     print("\n🏷️ METADATA:\n", data["metadatas"][0])

    # inspect_one_record(collection)
