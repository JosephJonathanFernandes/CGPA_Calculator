# src/config.py
"""
Configuration and theming for CGPA Calculator.
Design system: Inter (display/body) + JetBrains Mono (data values).
Palette: Indigo primary · Amber accent · Saffron backlog-warning · Emerald success.
"""
from dataclasses import dataclass
import os
import secrets
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

@dataclass(frozen=True)
class Theme:
    primary: str           # Indigo 600 / Sky 400 dark
    primary_dark: str      # Indigo 700 / Sky 600 dark
    accent: str            # Amber 500
    surface: str           # Page background
    card: str              # Card / sidebar background
    glass_bg: str          # Semi-transparent card
    border: str            # Subtle border
    text: str              # Body text
    muted: str             # Secondary / label text
    success: str = "#10B981"
    danger: str = "#EF4444"
    warning: str = "#F97316"   # Saffron — backlog-withheld state
    btn_text: str = "#FFFFFF"  # High contrast text for primary buttons


def get_theme(dark_mode: bool = False) -> Theme:
    if dark_mode:
        return Theme(
            primary="#818CF8",       # Indigo 400 — readable on dark
            primary_dark="#6366F1",
            accent="#FCD34D",        # Amber 300 — warm on dark
            surface="#08080D",       # Near-black, purple-tinted (darkened)
            card="#101017",          # Darkened proportionally
            glass_bg="rgba(16, 16, 23, 0.80)", # Darkened proportionally
            border="#2D2D3D",
            text="#F0F0FF",
            muted="#8B8BA8",
            success="#34D399",
            danger="#F87171",
            warning="#FB923C",
            btn_text="#FFFFFF",      # White text for primary buttons in dark mode
        )
    return Theme(
        primary="#4F46E5",       # Indigo 600
        primary_dark="#4338CA",  # Indigo 700
        accent="#8A5805",        # Amber 500 (darkened for AA contrast)
        surface="#F5F5FA",       # Very faint indigo-tinted white
        card="#FFFFFF",
        glass_bg="rgba(255, 255, 255, 0.82)",
        border="#E2E1F0",        # Faint indigo border
        text="#111128",          # Near-black, slightly purple
        muted="#6B6B8A",         # Muted indigo-grey
        success="#047D57",       # Emerald (darkened)
        danger="#DC2626",
        warning="#C3490A",       # Saffron (darkened)
        btn_text="#FFFFFF",      # White text for dark primary button in light mode
    )


def global_css(theme: Theme) -> str:
    """Return global CSS: fonts, CSS variables, base element styling."""
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {{
        color-scheme: {"dark" if theme.surface == "#08080D" else "light"};
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
        --warning: {theme.warning};
        --btn-text: {theme.btn_text};

        /* Semantic role aliases */
        --backlog-color: {theme.warning};
        --backlog-bg: {"rgba(234,88,12,0.07)" if theme.surface != "#0D0D14" else "rgba(251,146,60,0.09)"};
        --cleared-color: {theme.success};
        --pride-color: {theme.accent};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Inter', system-ui, sans-serif !important;
    }}

    html {{
        font-size: 1.0625rem !important;
    }}

    .stApp {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: var(--card) !important;
        border-right: 1px solid var(--border) !important;
    }}

    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: var(--text) !important;
    }}

    #MainMenu {{ visibility: hidden; }}
    [data-testid="stMainMenu"] {{ display: none !important; }}
    [data-testid="stHeader"] {{
        background: var(--surface) !important;
        border-bottom: 1px solid var(--border) !important;
    }}

    input, textarea, select, div[data-baseweb="select"], div[role="listbox"] {{
        border-radius: 10px !important;
        color: var(--text) !important;
        background-color: var(--card) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}

    /* Focus ring — accessibility floor */
    input:focus, textarea:focus, select:focus,
    button:focus-visible,
    div[data-testid="stPageLink"] a:focus-visible {{
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--muted); }}
    
    /* File Uploader Fix */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: var(--surface) !important;
        border: 1px dashed var(--border) !important;
    }}
    [data-testid="stFileUploaderDropzone"] * {{
        color: var(--text) !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background-color: var(--primary) !important;
        color: var(--btn-text) !important;
    }}
    [data-testid="stFileUploaderDropzone"] button * {{
        background-color: transparent !important;
    }}
    [data-testid="stFileUploaderDropzone"] small {{
        color: var(--muted) !important;
    }}

    /* Expander Fixes */
    [data-testid="stExpander"] details summary {{
        background-color: transparent !important;
        color: var(--text) !important;
    }}
    [data-testid="stExpander"] details summary:hover {{
        background-color: var(--surface) !important;
    }}
    [data-testid="stExpander"] details[open] summary {{
        background-color: var(--surface) !important;
    }}

    /* Link Styling */
    a:not(.feat-btn), .stMarkdown a:not(.feat-btn) {{
        color: var(--primary) !important;
        text-decoration: none;
    }}
    a:not(.feat-btn):hover, .stMarkdown a:not(.feat-btn):hover {{
        color: var(--accent) !important;
        text-decoration: underline;
    }}

    /* Tooltips */
    [data-testid="stTooltipContent"] {{
        background-color: var(--card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }}
    [data-testid="stTooltipHoverTarget"] svg {{
        fill: var(--muted) !important;
        color: var(--muted) !important;
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
            Config.SECRET_KEY = secrets.token_urlsafe(32)
