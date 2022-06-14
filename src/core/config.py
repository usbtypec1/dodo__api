from dotenv import load_dotenv
from pydantic import BaseSettings, Field

__all__ = (
    'app_settings',
)

load_dotenv()

APP_USER_AGENT = 'Goretsky-Band'


class AppSettings(BaseSettings):
    port: int = Field(..., env='APP_PORT')
    host: str = Field(..., env='APP_HOST')
    is_debug: bool = Field(..., env='IS_DEBUG')


app_settings = AppSettings()
