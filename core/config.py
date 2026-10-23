import os

class Settings:
    PORT: int = int(os.getenv("PORT", 8002))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", 
        "https://metainspector.lcastro.com.ar,https://lcastro.com.ar"
    ).split(",")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 20))

settings = Settings()
