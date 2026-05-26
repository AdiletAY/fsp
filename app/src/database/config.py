import os

from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    user: str | None = os.getenv("POSTGRES_USER")
    password: str | None = os.getenv("POSTGRES_PASSWORD")
    host: str | None = os.getenv("POSTGRES_HOST")
    port: str | None = os.getenv("POSTGRES_PORT")
    name: str | None = os.getenv("POSTGRES_DB")

    pool_min_size: int = int(os.getenv("DB_POOL_MIN_SIZE", 10))
    pool_max_size: int = int(os.getenv("DB_POOL_MAX_SIZE", 50))

    @property
    def dsn(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


db_config = DatabaseConfig()
