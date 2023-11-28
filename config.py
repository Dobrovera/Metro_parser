from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    BASE_DIR = Path(__file__).resolve().parent

    @property
    def DATABASE_URL(self):
        return f'sqlite+aiosqlite:///metro.db'


settings = Settings()
