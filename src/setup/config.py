from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    host_name: str = "localhost"
    port: int = 6569


def use_proper_city_name(city_name: str) -> str:

    if "_" in city_name:
        return city_name.replace("_", "").title()
    else: 
        return city_name.title()


config = GeneralConfig()

