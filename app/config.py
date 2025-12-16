from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    primary: str = "#2563EB"  # blue-600
    primary_dark: str = "#1D4ED8"
    accent: str = "#F97316"  # orange-500
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

    .main {{
        background: transparent;
        padding-top: 1rem;
    }}

    .stApp {{
        background: transparent;
    }}

    header, .css-18e3th9, .css-1d391kg {{
        background: transparent;
    }}

    .glass-card {{
        border: 1px solid var(--border);
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.92), rgba(15, 23, 42, 0.9));
        border-radius: 16px;
        padding: 1.25rem 1rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
    }}

    .headline {{
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }}

    .pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.14);
        color: #0b1221;
        border: 1px solid rgba(255, 255, 255, 0.35);
        font-size: 0.85rem;
    }}

    .metric-label {{
        color: var(--muted);
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }}

    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
    }}

    .footnote {{
        color: var(--muted);
        font-size: 0.9rem;
    }}
    """
