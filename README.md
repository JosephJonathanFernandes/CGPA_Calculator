# CGPA Calculator

A human-centered Streamlit app for calculating CGPA with semester-level credit control, partial semester support, and quick insights.

[![Streamlit](https://img.shields.io/badge/Streamlit-deployed-blue)](https://streamlit.io/)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB)](https://www.python.org/)

## Features
- Custom or default credits per semester (GEC Computer defaults included).
- Handles trailing semesters without SGPA while keeping order intact.
- Metrics, breakdown table, and SGPA trend chart.
- Themed UI with accessible contrast and clear guidance.

## Project layout
- `main.py` — App entrypoint wiring theme, layout, and logic.
- `app/config.py` — Theme tokens and global styles.
- `app/logic.py` — CGPA math, defaults, and breakdown assembly.
- `app/layout.py` — Streamlit UI composition.
 - `.gitignore` — Housekeeping for venv and editor cruft.
 - `LICENSE` — MIT License.

## Setup
1. Create/activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install streamlit pandas
   ```
3. Run the app:
   ```bash
   python -m streamlit run main.py
   ```

## Contributing
- Fork, branch, and submit PRs with concise descriptions.
- Run `python -m streamlit run main.py` to verify UI locally.
- Keep UI copy concise and accessible; maintain contrast ratios.

## License
MIT. See [LICENSE](LICENSE).

## Usage
1. Set total semesters and how many have published SGPA.
2. Keep default credits or enter custom credits.
3. Enter SGPA for completed semesters.
4. Submit to see CGPA, totals, breakdown, and trend.

## Notes
- Missing SGPA is supported only for trailing semesters to keep ordering realistic.
- Update credits when electives or course loads change to maintain accuracy.
