import configparser
import os
from ganga_ai.helpers.rag import load_rag_index, toggle_rag_state, does_rag_exist


class Config:
    _config_file_path = ".gangaairc"
    _default_system_prompt = "Your task is to help users write and diagonize the python code they write at a Ipython terminal. Use markdown to format the responses. If the user is interacting with you the message starts with %%assisst else the user is just running commands."
    _default_model = "mistral"
    _is_rag_enabled: bool = False
    _rag_index = None

    def __init__(self):
        config = self._build_config_parser_object()
        self._model = config["DEFAULT"].get("model", self._default_model)
        self._system_prompt = config["DEFAULT"].get(
            "system_prompt", self._default_system_prompt
        )
        self._load_rag_state()
        if self._is_rag_enabled:
            self._rag_index = load_rag_index()

    def _enable_rag_state(self):
        self._is_rag_enabled = True
        if self._is_rag_enabled:
            self._rag_index = load_rag_index()
        toggle_rag_state(True)

    def _load_rag_state(self):
        rag_state: bool = does_rag_exist()
        self._is_rag_enabled = rag_state

    def get_model(self) -> str:
        return self._model

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def get_rag_state(self) -> bool:
        return self._is_rag_enabled

    def _build_config_parser_object(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config_prefix = "[DEFAULT]\n"
        if os.path.exists(self._config_file_path):
            with open(self._config_file_path, "r") as file:
                default_config_values = config_prefix + file.read()
            config.read_string(default_config_values)
        else:
            config.read_string(config_prefix)
        return config
