from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    rabbitmq_url: str = "amqp://rrtm:rrtm@localhost:5672/"
    api_base_url: str = "http://localhost:8000"
    # Адрес Mini App. Telegram принимает только https, поэтому локально
    # оставляем пустым — тогда кнопка приложения просто не показывается.
    miniapp_url: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
