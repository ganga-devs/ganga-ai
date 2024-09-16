from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, load_index_from_storage, Settings
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
import shutil
import subprocess

def create_new_rag_store(rag_cache_path: str):
    if os.path.exists(rag_cache_path):
        shutil.rmtree(rag_cache_path)
    os.makedirs(rag_cache_path)

def generate_text_files(data_store: str, ganga_doc_path: str):
    command = [
        'sphinx-build',
        '-b', 'text',
        ganga_doc_path,
        data_store
    ]
    subprocess.run(command, check=True)
    doctrees_path = os.path.join(data_store, '.doctrees')
    if os.path.exists(doctrees_path):
        subprocess.run(['rm', '-rf', doctrees_path], check=True)
    return

# def consume_dir():
#     rag_store = "./cache/rag"
#     data_store = "./cache/data"
#     ganga_doc_path = "../ganga/doc"
#     create_new_rag_store(rag_store)
#     generate_text_files(data_store=data_store, ganga_doc_path=ganga_doc_path)
#     Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
#     Settings.llm = Ollama(model="mistral", request_timeout=300)
#     if not os.listdir(rag_store):
#         documents = SimpleDirectoryReader(input_dir=data_store, recursive=True).load_data()
#         index = VectorStoreIndex.from_documents(documents)
#         index.storage_context.persist(persist_dir=rag_store)
#     else:
#         storage_context = StorageContext.from_defaults(persist_dir=rag_store)
#         index = load_index_from_storage(storage_context)
#     query_engine = index.as_query_engine()
#     response = query_engine.query("What is claude?")
#     print(response)

# def consume_dir():
#     rag_store = "./cache/rag"
#     data_store = "./cache/data"
#     # ganga_doc_path = "../ganga/doc"
#     # create_new_rag_store(rag_store)
#     # generate_text_files(data_store=data_store, ganga_doc_path=ganga_doc_path)
#     Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
#     Settings.llm = Ollama(model="mistral", request_timeout=300)
#     if not os.listdir(rag_store):
#         documents = SimpleDirectoryReader(input_dir=data_store, recursive=True).load_data()
#         index = VectorStoreIndex.from_documents(documents)
#         index.storage_context.persist(persist_dir=rag_store)
#     else:
#         storage_context = StorageContext.from_defaults(persist_dir=rag_store)
#         index = load_index_from_storage(storage_context)
#     query_engine = index.as_query_engine()
#     response = query_engine.query("What is claude?")
#     print(response)

def build_rag():
    rag_store = "./cache/rag"
    data_store = "./cache/data"
    ganga_doc_path = "../ganga/doc"
    create_new_rag_store(rag_store)
    generate_text_files(data_store=data_store, ganga_doc_path=ganga_doc_path)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    documents = SimpleDirectoryReader(input_dir=data_store, recursive=True).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=rag_store)
    return index

def load_rag():
    rag_store = "./cache/rag"
    storage_context = StorageContext.from_defaults(persist_dir=rag_store)
    index = load_index_from_storage(storage_context)
    return index
