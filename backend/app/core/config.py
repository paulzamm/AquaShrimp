from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str 
    DB_PORT: int 
    DB_USER: str 
    DB_PASSWORD: str
    DB_NAME: str 

    APP_ENV: str 
    SECRET_KEY: str 

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
