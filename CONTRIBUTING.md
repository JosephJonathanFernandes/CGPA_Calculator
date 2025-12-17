# Contributing

Thanks for your interest in improving the CGPA Calculator! To keep changes smooth and reviewable, please follow these guidelines.

## Getting started
- Create a virtual environment and install deps: `pip install streamlit pandas`.
- Run locally: `python -m streamlit run main.py`.
- Keep UI text concise and accessible; preserve contrast and keyboard navigation.

## Pull requests
- Use feature branches and clear PR titles.
- Describe the change, why it’s needed, and how you tested it.
- Prefer small, focused PRs (UI copy, layout tweaks, logic fix, etc.).

## Code style
- Python 3.10+ type hints.
- Keep logic in `app/logic.py` and UI composition in `app/layout.py`.
- Avoid inline CSS in components; add shared styles to `app/config.py` when possible.

## Testing
- Manually verify the form flow (semesters, trailing blanks, custom credits).
- Check that charts and tables render without warnings.

## Reporting issues
- Include steps to reproduce, expected vs. actual behavior, and screenshots for UI issues.
