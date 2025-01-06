import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv


class WebsocketConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6969 


class GeneralConfig(BaseSettings):

    found_env_file: bool = load_dotenv(find_dotenv())
    
    if found_env_file:
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
        email: str = os.environ["EMAIL"]


def use_proper_city_name(city_name: str) -> str:

    if "_" in city_name:
        return city_name.replace("_", "").title()
    else: 
        return city_name.title()


websocket_config = WebsocketConfig()
general_config = GeneralConfig()

