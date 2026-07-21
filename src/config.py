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
    primary: str = "var(--primary-color, #3B82F6)"
    primary_dark: str = "var(--primary-color, #2563EB)"
    accent: str = "#8B5CF6"
    surface: str = "var(--secondary-background-color, #F8FAFC)"
    card: str = "var(--background-color, #FFFFFF)"
    border: str = "var(--secondary-background-color, #E2E8F0)"
    text: str = "var(--text-color, #0F172A)"
    muted: str = "var(--text-color, #64748B)"
    success: str = "#10B981"
    danger: str = "#EF4444"

def global_css(theme: Theme) -> str:
    """Return global CSS styling for Streamlit components."""
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --primary: {theme.primary};
        --primary-dark: {theme.primary_dark};
        --accent: {theme.accent};
        --surface: {theme.surface};
        --card: {theme.card};
        --border: {theme.border};
        --text: {theme.text};
        --muted: {theme.muted};
        --success: {theme.success};
        --danger: {theme.danger};
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Ensure Streamlit containers use the Inter font */
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif !important;
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
        border-radius: 10px !important;
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
