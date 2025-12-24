# src/config.py
"""
Configuration and theming for CGPA Calculator (modular, secure).
"""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

@dataclass(frozen=True)
class Theme:
    primary: str = "#2563EB"
    primary_dark: str = "#1D4ED8"
    accent: str = "#F97316"
    surface: str = "#0B1221"
    card: str = "#111827"
    border: str = "#1F2937"
    text: str = "#F3F4F6"
    muted: str = "#9CA3AF"


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
        background: radial-gradient(circle at 20% 20%, #0f172a 0%, #0b1221 30%, #060913 70%);
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
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    SECRET_KEY = os.getenv('SECRET_KEY', '')

    @staticmethod
    def validate():
        if not Config.SECRET_KEY:
            raise ValueError('SECRET_KEY is not set in environment variables.')
