import os

class Settings:
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    REPO_NAME: str = "Validation2026/Enflasyon"
    BRANCH: str = "main"
    EXCEL_FILE: str = "TUFE_Konfigurasyon.xlsx"
    PRICE_FILE: str = "Fiyat_Veritabani.xlsx"
    SHEET_NAME: str = "Madde_Sepeti"
    EVDS_API_KEY: str = os.getenv("EVDS_API_KEY")

settings = Settings()