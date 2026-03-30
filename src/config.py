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
    primary: str = "#2563EB"
    primary_dark: str = "#1D4ED8"
    accent: str = "#F97316"
    surface: str = "#F1F5F9"
    card: str = "#FFFFFF"
    border: str = "#CBD5E1"
    text: str = "#0F172A"
    muted: str = "#475569"


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
    body {{
        color: var(--text);
        background: radial-gradient(circle at 10% 10%, #ffffff 0%, #f8fafc 35%, #eef2ff 100%);
    }}
    .stApp, [data-testid="stAppViewContainer"] {{
        color: var(--text);
        background: radial-gradient(circle at 10% 10%, #ffffff 0%, #f8fafc 35%, #eef2ff 100%) !important;
    }}
    [data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.92) !important;
    }}
    [data-testid="stSidebar"] {{
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }}
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        background: transparent !important;
        color: #0f172a !important;
    }}
    #MainMenu {{
        visibility: hidden;
    }}
    [data-testid="stMainMenu"] {{
        display: none !important;
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {{
        color: #0f172a !important;
    }}
    .light-card {{
        background: #f8fafc;
        color: #0b1221;
        border: 1px solid #e5e7eb;
    }}
    input, textarea, select {{
        background: #ffffff;
        color: #0b1221;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
    }}
    label, .stTextInput label, .stNumberInput label {{
        color: #0b1221;
        font-weight: 700;
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
