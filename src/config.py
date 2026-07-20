# src/config.py
"""
Configuration and theming for CGPA Calculator (modular, secure).
"""
from dataclasses import dataclass
import os
import secrets
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

@dataclass(frozen=True)
class Theme:
    primary: str = "var(--primary-color, #2563EB)"
    primary_dark: str = "var(--primary-color, #1D4ED8)"
    accent: str = "#F97316"
    surface: str = "var(--secondary-background-color, #F1F5F9)"
    card: str = "var(--background-color, #FFFFFF)"
    border: str = "var(--secondary-background-color, #CBD5E1)"
    text: str = "var(--text-color, #0F172A)"
    muted: str = "gray"

def global_css(theme: Theme) -> str:
    """Return global CSS styling for Streamlit components."""
    return f"""
    :root {{
        --primary: {theme.primary};
        --primary-dark: {theme.primary_dark};
        --accent: {theme.accent};
        --surface: {theme.surface};
        --card: {theme.card};
        --border: {theme.border};
        --text: {theme.text};
        --muted: {theme.muted};
    }}
    #MainMenu {{
        visibility: hidden;
    }}
    [data-testid="stMainMenu"] {{
        display: none !important;
    }}
    .light-card {{
        background: var(--card);
        color: var(--text);
        border: 1px solid var(--border);
    }}
    input, textarea, select {{
        border-radius: 10px;
    }}
    """

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    SECRET_KEY = os.getenv('SECRET_KEY', '')

    @staticmethod
    def validate():
        if not Config.SECRET_KEY:
            if Config.ENVIRONMENT in {'production', 'prod'}:
                raise ValueError('SECRET_KEY is not set in environment variables.')

            # Use an ephemeral key in local/dev to keep initialization smooth.
            Config.SECRET_KEY = secrets.token_urlsafe(32)
