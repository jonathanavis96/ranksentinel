from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    # Core
    RANKSENTINEL_DB_PATH: str = "./ranksentinel.sqlite3"
    RANKSENTINEL_BASE_URL: str = ""
    RANKSENTINEL_OPERATOR_EMAIL: str = ""

    # Mailgun
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""
    MAILGUN_FROM: str = ""
    MAILGUN_TO: str = ""

    # PSI
    PSI_API_KEY: str = ""

    # Stripe (scaffold only)
    STRIPE_WEBHOOK_SECRET: str = ""


def get_settings() -> Settings:
    return Settings()
