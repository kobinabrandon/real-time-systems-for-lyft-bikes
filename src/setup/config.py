from pydantic_settings import BaseSettings, SettingsConfigDict


class WebsocketConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    host: str = "localhost"
    port: int = 6963 


def use_proper_city_name(city_name: str) -> str:

    if "_" in city_name:
        return city_name.replace("_", "").title()
    else: 
        return city_name.title()


websocket_config = WebsocketConfig()

