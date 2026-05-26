from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings reads env at instantiation and assigns to variables
class Settings(BaseSettings):
    # Docker already passes in an env, but this line would still be useful if we ever ran outside of docker
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str

settings = Settings()