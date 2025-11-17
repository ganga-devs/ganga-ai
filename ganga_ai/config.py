import configparser
import os

class Config:
    config_file_path = ".gangaairc"
    default_backend_url = "http://localhost:8000"
    default_user_id = "12345"

    def __init__(self):
        config = self.build_config_parser_object()
        self.backend_url: str = config["DEFAULT"].get("BACKEND_URL", self.default_backend_url)
        self.user_id: str = config["DEFAULT"].get("USER_UUID", self.default_user_id)

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
