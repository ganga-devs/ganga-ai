from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    load_index_from_storage,
    Settings,
)
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
import shutil
import subprocess
import json

RAG_STATE_FILE: str = "./cache/rag_state.json"
RAG_STORE = "./cache/rag"
DATA_STORE = "./cache/data"

def create_new_rag_cache_path(rag_cache_path: str):
    if os.path.exists(rag_cache_path):
        shutil.rmtree(rag_cache_path)
    os.makedirs(rag_cache_path)


def generate_text_files(data_store: str, ganga_doc_path: str):
    command = ["sphinx-build", "-b", "text", ganga_doc_path, data_store]
    subprocess.run(command, check=True)
    doctrees_path = os.path.join(data_store, ".doctrees")
    if os.path.exists(doctrees_path):
        subprocess.run(["rm", "-rf", doctrees_path], check=True)
    return


def build_rag_index(ganga_path: str):
    GANGA_DOC_PATH = f"{ganga_path}/doc"
    create_new_rag_cache_path(RAG_STORE)
    generate_text_files(data_store=DATA_STORE, ganga_doc_path=GANGA_DOC_PATH)
    toggle_rag_state(True)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    documents = SimpleDirectoryReader(input_dir=DATA_STORE, recursive=True).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=RAG_STORE)
    return index


def load_rag_index():
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    storage_context = StorageContext.from_defaults(persist_dir=RAG_STORE)
    index = load_index_from_storage(storage_context)
    return index

def remove_rag_index():
    pass

def does_rag_exist():
    if not os.path.exists(RAG_STATE_FILE):
        return False
    with open(RAG_STATE_FILE) as rag_state_file:
        current_rag_state = json.load(rag_state_file)
        return current_rag_state.get("is_rag_enabled", False)

def toggle_rag_state(state: bool):
    new_rag_state = {"is_rag_enabled": state}
    with open(RAG_STATE_FILE, "w") as f:
        json.dump(new_rag_state, f)
