"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the Loan Eligibility Assessment System."""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "loan_eligibility_db"

    jwt_secret: str = "change-this-to-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    frontend_url: str = "http://localhost:5173"
    app_name: str = "AI-Based Loan Eligibility Assessment System"
    debug: bool = True

    # Demo EMI interest defaults by loan type (sample rates, not real bank rates)
    default_interest_rates: dict = {
        "Personal Loan": 12.0,
        "Education Loan": 9.5,
        "Home Loan": 8.5,
        "Vehicle Loan": 10.5,
        "Business Loan": 14.0,
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
