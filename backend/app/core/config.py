from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Qualipharma"
    debug: bool = False

    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_db_url: str = Field(..., alias="SUPABASE_DB_URL")
    supabase_service_role_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-70b-8192", alias="GROQ_MODEL")

    embedding_dim: int = Field(default=384, alias="EMBEDDING_DIM")
    request_timeout_seconds: int = Field(default=120, alias="REQUEST_TIMEOUT_SECONDS")

    admin_key: str | None = Field(default=None, alias="ADMIN_KEY")


settings = Settings()
