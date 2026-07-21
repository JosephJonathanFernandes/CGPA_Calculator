# 🎓 CGPA Calculator

A **professional, stateful academic performance tracker** built with Python and Streamlit. Designed specifically for engineering students (defaulted to Goa University curriculum, but customizable), this tool provides accurate CGPA/SGPA calculations, intelligent backlog handling, and a premium glassmorphism UI.

## ✨ Features

- **Accurate CGPA & SGPA Computation:** Credit-weighted calculations supporting up to 12 semesters.
- **Intelligent Backlog Handling:** Automatically detects failed subjects (0.0 points) or withheld results, putting calculations "on hold" rather than hiding them behind a misleading `0.00` average.
- **Premium UI/UX:** A bespoke design system utilizing DM Sans and JetBrains Mono fonts, Indigo/Amber/Saffron accents, and responsive layout scaling across all devices.
- **Goal-Based Planner:** "What-if" simulation engine to predict what grades are needed to reach a target CGPA.
- **Sharable Result Cards:** Generates a downloadable, beautifully styled PNG result card summarizing your standing and percentage.
- **PDF Reports:** Export a full, printable breakdown of your semester performance (requires `fpdf2`).
- **Profile Persistence:** Save your academic profile as a `.json` file and load it seamlessly.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- `pip` (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/cgpa-calculator.git
   cd cgpa-calculator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```
   *The application will open automatically in your default browser at `http://localhost:8501`.*

## 🛠️ Architecture

- **`main.py`**: The entry point, handling routing via `st.navigation`.
- **`src/logic.py`**: Pure, stateless calculations. Returns results and statuses (`"cleared"`, `"blocked"`).
- **`src/layout.py`**: The core UI component and CSS store, defining the custom design system and layout components (glassmorphism cards, responsive metrics).
- **`src/config.py`**: Color palette and semantic design tokens.
- **`src/export.py`**: PDF and PNG generation logic (gracefully degrades if `fpdf2` isn't installed).
- **`data/curriculum.json`**: Branch/semester curriculum database mappings.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
