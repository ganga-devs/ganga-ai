from typing import List
import configparser
import os

"""
2048 is the default context size that used by ollama. So the vram mentioned on the website is for this value. If you use higher values like 4096 simply proportionately scale it.
"""

class Config:
    config_file_path = ".gangaairc"
    default_llm_model = "qwen3:8b"
    default_embedding_model = "BAAI/bge-small-en-v1.5"
    default_transformer_dimension = "384"
    default_context_window = "2048"
    default_data_url = "https://github.com/ganga-devs/ganga"
    default_cache_dir = "cache"
    default_dbname = "rag"
    default_db_username = "cern"
    default_db_password = "root"
    default_host = "localhost"
    default_port = "5432"

    def __init__(self):
        config = self.build_config_parser_object()
        self.llm_model: str = config["DEFAULT"].get("MODEL", self.default_llm_model)
        self.context_window: str = config["DEFAULT"].get("CONTEXT_WINDOW", self.default_context_window)
        self.embedding_model: str = config["DEFAULT"].get(
            "EMBEDDING_MODEL", self.default_embedding_model
        )
        self.data_urls: List[str] = (
            config["DEFAULT"].get("DATA_URLS", self.default_data_url).split(",")
        )
        self.cache_dir: str = config["DEFAULT"].get("CACHE_DIR", self.default_cache_dir)
        self.dbname: str = config["DEFAULT"].get("DBNAME", self.default_dbname)
        self.db_username: str = config["DEFAULT"].get(
            "USERNAME", self.default_db_username
        )
        self.db_password: str = config["DEFAULT"].get(
            "PASSWORD", self.default_db_password
        )
        self.host: str = config["DEFAULT"].get("HOST", self.default_host)
        self.port: str = config["DEFAULT"].get("PORT", self.default_port)
        self.transformer_dimension: int = int(
            config["DEFAULT"].get(
                "TRANSFORMER_DIMENSION", self.default_transformer_dimension
            )
        )

    def build_config_parser_object(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config_prefix = "[DEFAULT]\n"
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, "r") as file:
                default_config_values = config_prefix + file.read()
            config.read_string(default_config_values)
        else:
            config.read_string(config_prefix)
        return config


config = Config()
