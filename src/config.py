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
    primary: str
    primary_dark: str
    accent: str
    surface: str
    card: str
    glass_bg: str
    border: str
    text: str
    muted: str
    success: str = "#10B981"
    danger: str = "#EF4444"

def get_theme(dark_mode: bool = False) -> Theme:
    """Return Theme configuration based on manual toggle."""
    if dark_mode:
        return Theme(
            primary="#38BDF8",       # Vibrant Sky
            primary_dark="#0284C7",
            accent="#818CF8",
            surface="#09090B",       # Zinc 950
            card="#18181B",          # Zinc 900
            glass_bg="rgba(24, 24, 27, 0.75)", # Zinc 900 with opacity
            border="#27272A",        # Zinc 800
            text="#FAFAFA",          # Zinc 50
            muted="#A1A1AA"          # Zinc 400
        )
    return Theme(
        primary="#0284C7",       # Sky 600
        primary_dark="#0369A1",
        accent="#6366F1",
        surface="#F8FAFC",       # Slate 50
        card="#FFFFFF",          # White
        glass_bg="rgba(255, 255, 255, 0.8)", # White with opacity
        border="#E2E8F0",        # Slate 200
        text="#0F172A",          # Slate 900
        muted="#64748B"          # Slate 500
    )

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
        --glass-bg: {theme.glass_bg};
        --border: {theme.border};
        --text: {theme.text};
        --muted: {theme.muted};
        --success: {theme.success};
        --danger: {theme.danger};
    }}
    
    /* Ensure Streamlit containers use the Inter font, respect manual theme, and scale up font size */
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    html {{
        font-size: 18px !important;
    }}
    
    .stApp {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: var(--card) !important;
    }}
    
    /* Force common text elements to respect our text color */
    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: var(--text) !important;
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
