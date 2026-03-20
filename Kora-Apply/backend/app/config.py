import os

class Config:
    """Base configuration with default settings."""

    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # CORS: Origins
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
    if ALLOWED_ORIGINS:
        ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]

    print("Configured CORS origins:", ALLOWED_ORIGINS)


# Automatically select config based on ENVIRONMENT variable
def get_config():
    return Config()


config = get_config()