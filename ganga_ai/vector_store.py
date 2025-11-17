import os
import re
import shutil
import subprocess
import psycopg2
from typing import Literal, List
from ganga_ai.config import config
from ganga_ai.github import download_github_repo
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.postgres import PGVectorStore
from ganga_ai.ipython_history import ipython_history


def type_of_url(url: str) -> Literal["GITHUB", "UNKNOWN"]:
    """
    Determines the type of a given data url
    """
    match url:
        case url if re.match(r"^https?://(www\.)?github\.com(/|$)", url):
            url_type = "GITHUB"
        case _:
            url_type = "UNKNOWN"
    return url_type


def create_directory(directory_path: str) -> None:
    """
    Creates the given directory
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(
            f"file vector_store function create_directory created new directory at {directory_path}"
        )
    except Exception as err:
        print(f"file vector_store function create_directory error encountered: {err}")


def remove_directory(directory_path: str) -> None:
    """
    Removes a certain directory
    """
    try:
        shutil.rmtree(directory_path)
        print(
            f"file vector_store function remove_directory removed directory {directory_path}"
        )
    except Exception as err:
        print(f"file vector_store function create_directory error encountered: {err}")


class Vector_Store:
    """
    Main class for the vector store
    """

    cache_path = config.cache_dir
    embedding_model = config.embedding_model
    llm_model = config.llm_model
    context_window = config.context_window
    data_urls = config.data_urls
    dbname = config.dbname
    username = config.db_username
    password = config.db_password
    host = config.host
    port = config.port
    transformer_dimension = config.transformer_dimension
    rag_table_name = "ganga_rag"
    request_timeout = 300
    raw_data_path = os.path.join(cache_path, "raw")
    processed_data_path = os.path.join(cache_path, "processed")
    Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model)
    Settings.llm = Ollama(model=llm_model, request_timeout=request_timeout, context_window=context_window)
    vector_store = None
    storage_context = None
    query_engine = None
    connection = psycopg2.connect(
        dbname=dbname, user=username, password=password, host=host
    )
    connection.autocommit = True

    def __init__(self):
        self.download_llm_model()
        if self.does_vector_store_exist():
            self.load_vector_store()
        else:
            self.create_and_load_vector_store()

    def download_llm_model(self):
        """
        Ensures the Ollama model is available locally by checking the modelfiles directory.
        Pulls it using `ollama pull` if missing.
        """
        model_path = os.path.join("modelfiles", self.llm_model)
        if not os.path.exists(model_path):
            print(
                f"file: vector_store method: ensure_ollama_model_exists model not found at {model_path}, pulling model"
            )
            try:
                subprocess.run(
                    ["ollama", "pull", self.llm_model],
                    check=True,
                    timeout=1000,
                )
                print(
                    f"file: vector_store method: ensure_ollama_model_exists successfully pulled {self.llm_model}"
                )
            except Exception as e:
                print(
                    f"file: vector_store method: ensure_ollama_model_exists failed to pull {self.llm_model}: {e}"
                )

    def does_vector_store_exist(self) -> bool:
        """
        This function checks whether the rag table exists or not by searching the information_schema
        provided by postgres.
        This is needed as the load methods creates an empty table in case it does not find one.
        Llama index also prefixes "data" to the name of the table provided by it.
        So in information_schema the rag table will show up as data_table_name in the public section.
        """
        try:
            with self.connection.cursor() as cursor:
                ps_sql_query = """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = %s
                    );
                """
                prefixed_table_name = f"data_{self.rag_table_name}"
                cursor.execute(ps_sql_query, (prefixed_table_name,))
                result = cursor.fetchone()
                if result is None:
                    return False
                return result[0]
        except Exception as e:
            print(f"file: vector_store method: does_vector_store_exist error: {e}")
            return False

    def generate_text_files_from_sphinx_files(
        self, input_sphinx_dir: str, output_txt_dir: str
    ):
        """
        Generates text files from sphinx files
        """

        build_command = ["sphinx-build", "-b", "text", input_sphinx_dir, output_txt_dir]
        subprocess.run(build_command, check=True)
        doctrees_path = os.path.join(output_txt_dir, ".doctrees")
        if os.path.exists(doctrees_path):
            shutil.rmtree(doctrees_path)

    def process_ganga_docs(self) -> None:
        ganga_sphinx_files_path = os.path.join(self.raw_data_path, "ganga/doc")
        ganga_txt_files_path = os.path.join(self.processed_data_path, "ganga/doc")
        create_directory(ganga_txt_files_path)
        self.generate_text_files_from_sphinx_files(
            input_sphinx_dir=ganga_sphinx_files_path,
            output_txt_dir=ganga_txt_files_path,
        )

    def process_data(self, dir_list: List[str]):
        for dir in dir_list:
            match dir:
                case "cache/raw/ganga/doc":
                    self.process_ganga_docs()
                case _:
                    print(
                        f"file: vector_store method: consume_data unhandled type of data: {dir}"
                    )

    def create_list_of_directories_to_process(self, raw_cache_path: str) -> List[str]:
        """
        Create a list of directories to consume data from which the rag will be built
        """

        dir_list = []
        try:
            for subdir in os.listdir(raw_cache_path):
                subdir_path = os.path.join(raw_cache_path, subdir)
                if subdir == "ganga":
                    dir_list.append(os.path.join(subdir_path, "doc"))
                else:
                    dir_list.append(subdir_path)
        except Exception as err:
            print(
                f"file: vector_store method: create_list_of_directories_to_consume error: {err}"
            )
        return dir_list

    def download_intial_data(self, url: str, download_path) -> None:
        url_type = type_of_url(url=url)
        match url_type:
            case "GITHUB":
                download_github_repo(github_url=url, download_path=download_path)
            case "UNKNOWN":
                print(
                    f"file: vector_store method: download_data the unknown type of url encountered: {url}"
                )

    def create_and_load_vector_store(self) -> None:
        print(f"file: vector_store method: create_vector_store downloading data")
        for directory_path in (self.raw_data_path, self.processed_data_path):
            create_directory(directory_path)

        for url in self.data_urls:
            self.download_intial_data(url=url, download_path=self.raw_data_path)

        print(
            f"file: vector_store method: create_vector_store processing downloaded data"
        )
        dir_list = self.create_list_of_directories_to_process(self.raw_data_path)
        self.process_data(dir_list=dir_list)

        print(
            f"file: vector_store method: create_vector_store preparing vector database"
        )
        self.vector_store = PGVectorStore.from_params(
            database=self.dbname,
            host=self.host,
            password=self.password,
            port=self.port,
            user=self.username,
            table_name=self.rag_table_name,
            embed_dim=self.transformer_dimension,
            hnsw_kwargs={
                "hnsw_m": 16,
                "hnsw_ef_construction": 64,
                "hnsw_ef_search": 40,
                "hnsw_dist_method": "vector_cosine_ops",
            },
        )

        print(
            f"file: vector_store method: create_vector_store loading processed documents"
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        documents = SimpleDirectoryReader(
            input_dir=self.processed_data_path, recursive=True
        ).load_data()

        print(f"file: vector_store method: create_vector_store creating query_engine")
        index = VectorStoreIndex.from_documents(
            documents, storage_context=self.storage_context
        )
        self.query_engine = index.as_query_engine()

        print(
            f"file: vector_store method: create_vector_store clearing intermediary files"
        )
        for directory_path in (self.raw_data_path, self.processed_data_path):
            remove_directory(directory_path=directory_path)

    def load_vector_store(self) -> bool:
        """
        Load the vector store if it exists
        """
        try:
            self.vector_store = PGVectorStore.from_params(
                database=self.dbname,
                host=self.host,
                password=self.password,
                port=self.port,
                user=self.username,
                table_name=self.rag_table_name,
                embed_dim=self.transformer_dimension,
                hnsw_kwargs={
                    "hnsw_m": 16,
                    "hnsw_ef_construction": 64,
                    "hnsw_ef_search": 40,
                    "hnsw_dist_method": "vector_cosine_ops",
                },
            )
            index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
            self.query_engine = index.as_query_engine()
            return True
        except Exception as e:
            print(f"file: vector_store method: load_vector_store error: {e}")
            return False

    def query_vector_store(self, query: str):
        history = ipython_history.get_history()
        formatted_history = "\n".join([f"{role}: {msg}" for role, msg in history])
        final_prompt = f"{formatted_history}\nuser: {query}"
        if self.query_engine:
            llm_response = self.query_engine.query(final_prompt)
            ipython_history.add_user_input_to_history(query)
            ipython_history.add_llm_response_to_history(str(llm_response))
            return llm_response
        else:
            return ""


vector_store = Vector_Store()
