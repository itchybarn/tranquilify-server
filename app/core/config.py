from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings reads env at instantiation and assigns to variables
class Settings(BaseSettings):
    # Docker already passes in an env, but this line would still be useful if we ever ran outside of docker
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGO: str

    TWILIO_SID: str
    TWILIO_CLIENT_SECRET: str
    TRANQUILIFY_SERVICE_SID: str

settings = Settings()