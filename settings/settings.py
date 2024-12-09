from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class for application configuration.
    """
    postgres_user: str
    postgres_password: str
    postgres_url: str
    postgres_port: str
    postgres_db: str

    @property
    def database_url(self) -> str:
        return (f"postgresql://{self.postgres_user}:{self.postgres_password}@"
                f"{self.postgres_url}:{self.postgres_port}/{self.postgres_db}")