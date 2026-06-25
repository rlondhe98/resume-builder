# ATS-Friendly Resume Builder

A web-based interactive resume builder that generates clean, ATS-parseable resumes in LaTeX/PDF format. Fill in your details through a browser UI with live preview, and export a professional PDF.

## Features

- **Web Interface**: Tabbed form with real-time resume preview in the browser
- **ATS-Optimized Output**: Single-column layout, standard fonts, proper section headers, no tables/graphics — designed to pass ATS parsers
- **Live Preview**: See your resume update as you type
- **Clickable Hyperlinks**: Email, LinkedIn, GitHub, and project links are rendered as proper hyperlinks in both preview and PDF
- **Sort by Date**: One-click sorting of experience entries (latest first)
- **Persistent Data**: All inputs are saved to `resume_data.json` — close and come back anytime
- **Save Anywhere**: Save generated PDF/TeX to any folder on your machine
- **PDF Export**: Generates a LaTeX file and compiles to PDF via pdflatex
- **CLI Mode**: Also includes a standalone terminal-based builder (`resume_builder.py`)

## Prerequisites

1. **Python 3.7+**  
   Download: https://www.python.org/downloads/

2. **Flask** (Python package)  
   ```bash
   pip install flask
   ```

3. **MiKTeX** (LaTeX distribution, for PDF generation)  
   Download: https://miktex.org/download  
   - During installation, check **"Install missing packages on the fly"**
   - The app auto-detects MiKTeX in its default install location — no need to add to PATH manually
   - *Alternative*: If you don't want to install MiKTeX, you can download the `.tex` file and compile it on [Overleaf](https://www.overleaf.com) (free)

## Quick Start

```bash
# 1. Navigate to the project folder
cd C:\Users\qlg9915\Documents\resume-builder

# 2. Install dependencies
pip install flask

# 3. Start the web app
python webapp.py

# 4. Open in your browser
#    http://localhost:5000
```

## How to Use

1. **Open** http://localhost:5000 in your browser after starting the server
2. **Fill in sections** using the tabs on the left: Personal, Summary, Skills, Experience, Education, Certifications, Projects
3. **Watch the live preview** update on the right as you type
4. **Add entries** dynamically — click "+ Add Experience", "+ Add Education", etc.
5. **Sort experience** by date using the "Sort by Date" button (latest first)
6. **Save your data** — click "Save" to persist to `resume_data.json` (also auto-saves when generating)
7. **Generate PDF** — click "Generate PDF" to compile and download the PDF
8. **Download .tex** — click "Download .tex" to get the LaTeX source file
9. **Save To...** — click "Save To..." to save PDF and TeX files to a specific folder

### CLI Mode (Alternative)

```bash
python resume_builder.py
```
Follow the interactive terminal menu to fill in sections and generate the resume.

## File Structure

```
resume-builder/
├── webapp.py            # Flask web server (main entry point)
├── resume_builder.py    # CLI-based builder (alternative)
├── templates/
│   └── index.html       # Web UI (form + live preview)
├── template.tex         # Reference LaTeX template
├── requirements.txt     # Python dependencies
├── resume_data.json     # Your saved resume data (auto-generated)
├── output/
│   ├── resume.tex       # Generated LaTeX source
│   └── resume.pdf       # Final PDF output
└── README.md
```

## ATS Tips

- Use standard section headers (Professional Experience, Education, Skills)
- Quantify achievements with numbers (e.g., "Increased revenue by 25%")
- Include keywords from the job description
- Avoid acronyms without spelling them out at least once
- Keep to 1-2 pages maximum
- Use action verbs to start bullet points (Led, Built, Improved, Reduced)
- Don't use headers/footers for critical info — some ATS parsers skip them
