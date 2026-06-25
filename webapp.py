"""
ATS-Friendly Resume Builder - Web Application
Run: python webapp.py
Then open http://localhost:5000 in your browser.
"""

import json
import os
import subprocess
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "resume_data.json"
OUTPUT_DIR = BASE_DIR / "output"


def find_pdflatex():
    """Locate pdflatex executable, checking common MiKTeX paths if not on PATH."""
    import shutil
    path = shutil.which("pdflatex")
    if path:
        return path
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64" / "pdflatex.exe",
        Path("C:/Program Files/MiKTeX/miktex/bin/x64/pdflatex.exe"),
        Path(os.environ.get("APPDATA", "")) / "MiKTeX" / "miktex" / "bin" / "x64" / "pdflatex.exe",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "website": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def escape_latex(text):
    if not text:
        return ""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def generate_latex(data):
    lines = []
    lines.append(r"\documentclass[11pt,a4paper]{article}")
    lines.append(r"\usepackage[utf8]{inputenc}")
    lines.append(r"\usepackage[T1]{fontenc}")
    lines.append(r"\usepackage{lmodern}")
    lines.append(r"\usepackage[margin=0.7in]{geometry}")
    lines.append(r"\usepackage{enumitem}")
    lines.append(r"\usepackage[hidelinks]{hyperref}")
    lines.append(r"\usepackage{titlesec}")
    lines.append(r"\usepackage{xcolor}")
    lines.append("")
    lines.append(r"\pagestyle{empty}")
    lines.append("")
    lines.append(r"% ATS-friendly link color -- visible but not distracting")
    lines.append(r"\definecolor{linkblue}{HTML}{0645AD}")
    lines.append(r"\hypersetup{colorlinks=true, urlcolor=linkblue, linkcolor=linkblue}")
    lines.append("")
    lines.append(r"% Section headings")
    lines.append(r"\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]")
    lines.append(r"\titlespacing*{\section}{0pt}{14pt}{6pt}")
    lines.append("")
    lines.append(r"\setlength{\parindent}{0pt}")
    lines.append(r"\setlist[itemize]{nosep, topsep=3pt, leftmargin=18pt}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")

    # Header
    name = escape_latex(data.get("name", "Your Name"))
    lines.append(r"\begin{center}")
    lines.append(rf"{{\LARGE\bfseries {name}}}\\[6pt]")

    contact_parts = []
    if data.get("email"):
        email = data["email"]
        contact_parts.append(r"\href{mailto:" + email + "}{" + escape_latex(email) + "}")
    if data.get("phone"):
        contact_parts.append(escape_latex(data["phone"]))
    if data.get("location"):
        contact_parts.append(escape_latex(data["location"]))
    if data.get("linkedin"):
        url = data["linkedin"]
        # Show readable label e.g. linkedin.com/in/johndoe
        display = url.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + url + "}{" + escape_latex(display) + "}")
    if data.get("github"):
        url = data["github"]
        display = url.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + url + "}{" + escape_latex(display) + "}")
    if data.get("website"):
        url = data["website"]
        display = url.replace("https://", "").replace("http://", "").rstrip("/")
        contact_parts.append(r"\href{" + url + "}{" + escape_latex(display) + "}")

    lines.append(r"{\small " + " $\\mid$ ".join(contact_parts) + "}")
    lines.append(r"\end{center}")
    lines.append(r"\vspace{2pt}")
    lines.append("")

    # Summary
    if data.get("summary"):
        lines.append(r"\section{Professional Summary}")
        lines.append(escape_latex(data["summary"]))
        lines.append("")

    # Skills
    if data.get("skills"):
        lines.append(r"\section{Skills}")
        lines.append(r"\textbf{Technical Skills:} " + escape_latex(", ".join(data["skills"])))
        lines.append("")

    # Experience
    if data.get("experience"):
        lines.append(r"\section{Professional Experience}")
        for idx, exp in enumerate(data["experience"]):
            title = escape_latex(exp.get("title", ""))
            company = escape_latex(exp.get("company", ""))
            location = escape_latex(exp.get("location", ""))
            dates = escape_latex(exp.get("dates", ""))
            if idx > 0:
                lines.append(r"\vspace{6pt}")
            lines.append(rf"\textbf{{{title}}} \hfill \textbf{{{dates}}}\\")
            lines.append(rf"\textit{{{company}}} \hfill {location}")
            bullets = [b for b in exp.get("bullets", []) if b]
            if bullets:
                lines.append(r"\begin{itemize}")
                for bullet in bullets:
                    lines.append(rf"  \item {escape_latex(bullet)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    # Education
    if data.get("education"):
        lines.append(r"\section{Education}")
        for idx, edu in enumerate(data["education"]):
            degree = escape_latex(edu.get("degree", ""))
            school = escape_latex(edu.get("school", ""))
            location = escape_latex(edu.get("location", ""))
            dates = escape_latex(edu.get("dates", ""))
            if idx > 0:
                lines.append(r"\vspace{6pt}")
            lines.append(rf"\textbf{{{degree}}} \hfill \textbf{{{dates}}}\\")
            lines.append(rf"\textit{{{school}}} \hfill {location}")
            if edu.get("gpa"):
                lines.append(rf" \\\\ \textbf{{GPA:}} {escape_latex(edu['gpa'])}")
            highlights = [h for h in edu.get("highlights", []) if h]
            if highlights:
                lines.append(r"\begin{itemize}")
                for h in highlights:
                    lines.append(rf"  \item {escape_latex(h)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    # Certifications
    if data.get("certifications"):
        certs = [c for c in data["certifications"] if c]
        if certs:
            lines.append(r"\section{Certifications}")
            lines.append(r"\begin{itemize}")
            for cert in certs:
                lines.append(rf"  \item {escape_latex(cert)}")
            lines.append(r"\end{itemize}")
            lines.append("")

    # Projects
    if data.get("projects"):
        lines.append(r"\section{Projects}")
        for idx, proj in enumerate(data["projects"]):
            name_p = escape_latex(proj.get("name", ""))
            tech = escape_latex(proj.get("tech", ""))
            link = proj.get("link", "")
            if idx > 0:
                lines.append(r"\vspace{6pt}")
            header = rf"\textbf{{{name_p}}}"
            if tech:
                header += rf" | \textit{{{tech}}}"
            if link:
                display = link.replace("https://", "").replace("http://", "").rstrip("/")
                header += rf" | \href{{{link}}}{{{escape_latex(display)}}}"
            lines.append(header)
            bullets = [b for b in proj.get("bullets", []) if b]
            if bullets:
                lines.append(r"\begin{itemize}")
                for b in bullets:
                    lines.append(rf"  \item {escape_latex(b)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    lines.append(r"\end{document}")
    return "\n".join(lines)


# ─── Routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())


@app.route("/api/data", methods=["POST"])
def post_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    save_data(data)
    return jsonify({"status": "saved"})


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        data = load_data()
    save_data(data)

    OUTPUT_DIR.mkdir(exist_ok=True)
    tex_content = generate_latex(data)
    tex_path = OUTPUT_DIR / "resume.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    # Try to compile PDF
    pdf_generated = False
    pdflatex_path = find_pdflatex()
    if pdflatex_path:
        try:
            result = subprocess.run(
                [pdflatex_path, "-interaction=nonstopmode", "-output-directory", str(OUTPUT_DIR), str(tex_path)],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                pdf_generated = True
            else:
                print("pdflatex stderr:", result.stderr[-500:] if result.stderr else "")
        except subprocess.TimeoutExpired:
            pass
    else:
        print("pdflatex not found on PATH or in common MiKTeX locations")

    return jsonify({
        "status": "ok",
        "tex_generated": True,
        "pdf_generated": pdf_generated,
        "tex_path": str(tex_path),
        "pdf_path": str(OUTPUT_DIR / "resume.pdf") if pdf_generated else None,
    })


@app.route("/api/download/tex")
def download_tex():
    tex_path = OUTPUT_DIR / "resume.tex"
    if tex_path.exists():
        return send_file(tex_path, as_attachment=True, download_name="resume.tex")
    return jsonify({"error": "Generate resume first"}), 404


@app.route("/api/download/pdf")
def download_pdf():
    pdf_path = OUTPUT_DIR / "resume.pdf"
    if pdf_path.exists():
        return send_file(pdf_path, as_attachment=True, download_name="resume.pdf")
    return jsonify({"error": "PDF not available. Make sure pdflatex is installed."}), 404


@app.route("/api/save-to", methods=["POST"])
def save_to_location():
    """Copy generated files to a user-specified directory."""
    import shutil
    payload = request.get_json()
    dest = payload.get("path", "").strip() if payload else ""
    if not dest:
        return jsonify({"error": "No path provided"}), 400

    dest_dir = Path(dest)
    # Security: resolve to absolute and ensure it's under a real user directory
    try:
        dest_dir = dest_dir.resolve()
    except Exception:
        return jsonify({"error": "Invalid path"}), 400

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return jsonify({"error": f"Cannot create directory: {e}"}), 400

    copied = []
    for fname in ["resume.tex", "resume.pdf"]:
        src = OUTPUT_DIR / fname
        if src.exists():
            shutil.copy2(src, dest_dir / fname)
            copied.append(fname)

    if not copied:
        return jsonify({"error": "No files to copy. Generate resume first."}), 404

    return jsonify({"status": "ok", "copied": copied, "destination": str(dest_dir)})


if __name__ == "__main__":
    print("=" * 50)
    print("  ATS Resume Builder - Web Interface")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
