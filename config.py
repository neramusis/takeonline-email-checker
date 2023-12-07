from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tenant_id: str
    client_id: str
    client_secret: str
    refresh_token: str
    openai_api_key: str
    mysql_username: str
    mysql_password: str
    mysql_database: str
    takeonline_auth_key: str

    class Config:
        env_file = ".env"
