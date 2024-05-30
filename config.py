from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    text_complexity_index: int = 30
    word_complexity_index: int = 4


settings = Settings()
