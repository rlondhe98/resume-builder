"""
ATS-Friendly Resume Builder
Interactively collects resume data, saves to JSON, and generates LaTeX/PDF output.
Run: python resume_builder.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "resume_data.json"
TEMPLATE_FILE = Path(__file__).parent / "template.tex"
OUTPUT_DIR = Path(__file__).parent / "output"


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
    print(f"\n[Saved] Data written to {DATA_FILE}")


def prompt(msg, default=""):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {msg}{suffix}: ").strip()
    return val if val else default


def prompt_multiline(msg):
    print(f"  {msg} (enter a blank line to finish):")
    lines = []
    while True:
        line = input("    > ").strip()
        if not line:
            break
        lines.append(line)
    return lines


# ─── Section editors ─────────────────────────────────────────────

def edit_personal(data):
    print("\n── Personal Information ──")
    data["name"] = prompt("Full Name", data.get("name", ""))
    data["email"] = prompt("Email", data.get("email", ""))
    data["phone"] = prompt("Phone", data.get("phone", ""))
    data["location"] = prompt("Location (City, State)", data.get("location", ""))
    data["linkedin"] = prompt("LinkedIn URL", data.get("linkedin", ""))
    data["github"] = prompt("GitHub URL", data.get("github", ""))
    data["website"] = prompt("Website/Portfolio URL", data.get("website", ""))


def edit_summary(data):
    print("\n── Professional Summary ──")
    print("  (2-3 sentences highlighting your value proposition)")
    if data.get("summary"):
        print(f"  Current: {data['summary'][:80]}...")
    new_summary = prompt("Summary (leave blank to keep current)", "")
    if new_summary:
        data["summary"] = new_summary


def edit_skills(data):
    print("\n── Skills ──")
    if data.get("skills"):
        print("  Current skills:")
        for i, skill in enumerate(data["skills"], 1):
            print(f"    {i}. {skill}")
    print("\n  Options: [a]dd skills, [r]eplace all, [d]elete one, [k]eep current")
    choice = prompt("Choice", "k").lower()
    if choice == "a":
        new_skills = prompt_multiline("Enter skills (one per line)")
        data["skills"].extend(new_skills)
    elif choice == "r":
        data["skills"] = prompt_multiline("Enter all skills (one per line)")
    elif choice == "d":
        idx = int(prompt("Skill number to delete")) - 1
        if 0 <= idx < len(data["skills"]):
            removed = data["skills"].pop(idx)
            print(f"  Removed: {removed}")


def edit_experience(data):
    print("\n── Professional Experience ──")
    if data.get("experience"):
        for i, exp in enumerate(data["experience"], 1):
            print(f"  {i}. {exp['title']} at {exp['company']} ({exp['dates']})")
    print("\n  Options: [a]dd entry, [e]dit entry, [d]elete entry, [k]eep current")
    choice = prompt("Choice", "k").lower()
    if choice == "a":
        entry = {}
        entry["title"] = prompt("Job Title")
        entry["company"] = prompt("Company")
        entry["location"] = prompt("Location")
        entry["dates"] = prompt("Dates (e.g., Jan 2022 - Present)")
        print("  Enter bullet points (achievements/responsibilities):")
        entry["bullets"] = prompt_multiline("Bullets")
        data["experience"].append(entry)
    elif choice == "e" and data.get("experience"):
        idx = int(prompt("Entry number to edit")) - 1
        if 0 <= idx < len(data["experience"]):
            exp = data["experience"][idx]
            exp["title"] = prompt("Job Title", exp["title"])
            exp["company"] = prompt("Company", exp["company"])
            exp["location"] = prompt("Location", exp["location"])
            exp["dates"] = prompt("Dates", exp["dates"])
            print("  Current bullets:")
            for b in exp.get("bullets", []):
                print(f"    - {b}")
            if prompt("Replace bullets? (y/n)", "n").lower() == "y":
                exp["bullets"] = prompt_multiline("New bullets")
    elif choice == "d" and data.get("experience"):
        idx = int(prompt("Entry number to delete")) - 1
        if 0 <= idx < len(data["experience"]):
            removed = data["experience"].pop(idx)
            print(f"  Removed: {removed['title']} at {removed['company']}")


def edit_education(data):
    print("\n── Education ──")
    if data.get("education"):
        for i, edu in enumerate(data["education"], 1):
            print(f"  {i}. {edu['degree']} - {edu['school']}")
    print("\n  Options: [a]dd entry, [d]elete entry, [k]eep current")
    choice = prompt("Choice", "k").lower()
    if choice == "a":
        entry = {}
        entry["degree"] = prompt("Degree (e.g., B.S. Computer Science)")
        entry["school"] = prompt("School/University")
        entry["location"] = prompt("Location")
        entry["dates"] = prompt("Dates (e.g., 2018 - 2022)")
        entry["gpa"] = prompt("GPA (optional, leave blank to skip)")
        entry["highlights"] = prompt_multiline("Relevant coursework/honors (optional)")
        data["education"].append(entry)
    elif choice == "d" and data.get("education"):
        idx = int(prompt("Entry number to delete")) - 1
        if 0 <= idx < len(data["education"]):
            removed = data["education"].pop(idx)
            print(f"  Removed: {removed['degree']} - {removed['school']}")


def edit_certifications(data):
    print("\n── Certifications ──")
    if data.get("certifications"):
        for i, cert in enumerate(data["certifications"], 1):
            print(f"  {i}. {cert}")
    print("\n  Options: [a]dd, [d]elete, [k]eep current")
    choice = prompt("Choice", "k").lower()
    if choice == "a":
        certs = prompt_multiline("Enter certifications (one per line)")
        data["certifications"].extend(certs)
    elif choice == "d" and data.get("certifications"):
        idx = int(prompt("Entry number to delete")) - 1
        if 0 <= idx < len(data["certifications"]):
            removed = data["certifications"].pop(idx)
            print(f"  Removed: {removed}")


def edit_projects(data):
    print("\n── Projects ──")
    if data.get("projects"):
        for i, proj in enumerate(data["projects"], 1):
            print(f"  {i}. {proj['name']}")
    print("\n  Options: [a]dd entry, [d]elete entry, [k]eep current")
    choice = prompt("Choice", "k").lower()
    if choice == "a":
        entry = {}
        entry["name"] = prompt("Project Name")
        entry["tech"] = prompt("Technologies Used")
        entry["link"] = prompt("Link (optional)")
        entry["bullets"] = prompt_multiline("Description/highlights")
        data["projects"].append(entry)
    elif choice == "d" and data.get("projects"):
        idx = int(prompt("Entry number to delete")) - 1
        if 0 <= idx < len(data["projects"]):
            removed = data["projects"].pop(idx)
            print(f"  Removed: {removed['name']}")


# ─── LaTeX generation ────────────────────────────────────────────

def escape_latex(text):
    """Escape special LaTeX characters."""
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
    """Generate a complete LaTeX document from resume data."""
    lines = []
    lines.append(r"\documentclass[11pt,a4paper]{article}")
    lines.append("")
    lines.append(r"\usepackage[utf8]{inputenc}")
    lines.append(r"\usepackage[T1]{fontenc}")
    lines.append(r"\usepackage{lmodern}")
    lines.append(r"\usepackage[margin=0.75in]{geometry}")
    lines.append(r"\usepackage{enumitem}")
    lines.append(r"\usepackage{hyperref}")
    lines.append(r"\usepackage{titlesec}")
    lines.append("")
    lines.append(r"\pagestyle{empty}")
    lines.append(r"\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]")
    lines.append(r"\titlespacing*{\section}{0pt}{12pt}{6pt}")
    lines.append(r"\setlength{\parindent}{0pt}")
    lines.append(r"\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=18pt}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")

    # Header
    name = escape_latex(data.get("name", "Your Name"))
    lines.append(r"\begin{center}")
    lines.append(rf"{{\LARGE\bfseries {name}}}\\[4pt]")

    contact_parts = []
    if data.get("email"):
        contact_parts.append(escape_latex(data["email"]))
    if data.get("phone"):
        contact_parts.append(escape_latex(data["phone"]))
    if data.get("location"):
        contact_parts.append(escape_latex(data["location"]))
    if data.get("linkedin"):
        contact_parts.append(r"\href{" + data["linkedin"] + "}{LinkedIn}")
    if data.get("github"):
        contact_parts.append(r"\href{" + data["github"] + "}{GitHub}")
    if data.get("website"):
        contact_parts.append(r"\href{" + data["website"] + "}{Portfolio}")

    lines.append(" | ".join(contact_parts))
    lines.append(r"\end{center}")
    lines.append(r"\vspace{4pt}")
    lines.append("")

    # Summary
    if data.get("summary"):
        lines.append(r"\section{Professional Summary}")
        lines.append(escape_latex(data["summary"]))
        lines.append("")

    # Skills
    if data.get("skills"):
        lines.append(r"\section{Skills}")
        lines.append(escape_latex(", ".join(data["skills"])))
        lines.append("")

    # Experience
    if data.get("experience"):
        lines.append(r"\section{Professional Experience}")
        for exp in data["experience"]:
            title = escape_latex(exp.get("title", ""))
            company = escape_latex(exp.get("company", ""))
            location = escape_latex(exp.get("location", ""))
            dates = escape_latex(exp.get("dates", ""))
            lines.append(rf"\textbf{{{title}}} \hfill {dates}\\")
            lines.append(rf"\textit{{{company}}} -- {location}")
            if exp.get("bullets"):
                lines.append(r"\begin{itemize}")
                for bullet in exp["bullets"]:
                    lines.append(rf"  \item {escape_latex(bullet)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    # Education
    if data.get("education"):
        lines.append(r"\section{Education}")
        for edu in data["education"]:
            degree = escape_latex(edu.get("degree", ""))
            school = escape_latex(edu.get("school", ""))
            location = escape_latex(edu.get("location", ""))
            dates = escape_latex(edu.get("dates", ""))
            lines.append(rf"\textbf{{{degree}}} \hfill {dates}\\")
            lines.append(rf"\textit{{{school}}} -- {location}")
            if edu.get("gpa"):
                lines.append(rf"\\ GPA: {escape_latex(edu['gpa'])}")
            if edu.get("highlights"):
                lines.append(r"\begin{itemize}")
                for h in edu["highlights"]:
                    lines.append(rf"  \item {escape_latex(h)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    # Certifications
    if data.get("certifications"):
        lines.append(r"\section{Certifications}")
        lines.append(r"\begin{itemize}")
        for cert in data["certifications"]:
            lines.append(rf"  \item {escape_latex(cert)}")
        lines.append(r"\end{itemize}")
        lines.append("")

    # Projects
    if data.get("projects"):
        lines.append(r"\section{Projects}")
        for proj in data["projects"]:
            name_p = escape_latex(proj.get("name", ""))
            tech = escape_latex(proj.get("tech", ""))
            link = proj.get("link", "")
            header = rf"\textbf{{{name_p}}}"
            if tech:
                header += rf" | \textit{{{tech}}}"
            if link:
                header += rf" | \href{{{link}}}{{Link}}"
            lines.append(header)
            if proj.get("bullets"):
                lines.append(r"\begin{itemize}")
                for b in proj["bullets"]:
                    lines.append(rf"  \item {escape_latex(b)}")
                lines.append(r"\end{itemize}")
            lines.append("")

    lines.append(r"\end{document}")
    return "\n".join(lines)


def build_pdf(tex_path):
    """Compile LaTeX to PDF using pdflatex."""
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(OUTPUT_DIR), str(tex_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            pdf_path = OUTPUT_DIR / "resume.pdf"
            print(f"\n[Success] PDF generated: {pdf_path}")
            return True
        else:
            print(f"\n[Error] LaTeX compilation failed. Check output/resume.log for details.")
            print(f"  Hint: Make sure pdflatex is installed (e.g., MiKTeX or TeX Live)")
            return False
    except FileNotFoundError:
        print("\n[Error] pdflatex not found. Install a LaTeX distribution:")
        print("  - Windows: https://miktex.org/download")
        print("  - Or install TeX Live: https://tug.org/texlive/")
        print(f"\n  The .tex file was still generated at: {OUTPUT_DIR / 'resume.tex'}")
        return False
    except subprocess.TimeoutExpired:
        print("\n[Error] LaTeX compilation timed out.")
        return False


def generate_output(data):
    """Generate LaTeX file and attempt PDF compilation."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    tex_content = generate_latex(data)
    tex_path = OUTPUT_DIR / "resume.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"\n[Generated] LaTeX file: {tex_path}")
    build_pdf(tex_path)


# ─── Main menu ───────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("       ATS-FRIENDLY RESUME BUILDER (LaTeX/PDF)")
    print("=" * 60)
    print("  Your data is saved automatically to resume_data.json")
    print("  Re-run anytime to update sections.\n")

    data = load_data()

    while True:
        print("\n┌─────────────────────────────────┐")
        print("│  Resume Sections                │")
        print("├─────────────────────────────────┤")
        print("│  1. Personal Information        │")
        print("│  2. Professional Summary        │")
        print("│  3. Skills                      │")
        print("│  4. Professional Experience     │")
        print("│  5. Education                   │")
        print("│  6. Certifications              │")
        print("│  7. Projects                    │")
        print("│  8. Generate Resume (PDF)       │")
        print("│  9. View Current Data           │")
        print("│  0. Save & Exit                 │")
        print("└─────────────────────────────────┘")

        choice = prompt("Select option", "")

        if choice == "1":
            edit_personal(data)
            save_data(data)
        elif choice == "2":
            edit_summary(data)
            save_data(data)
        elif choice == "3":
            edit_skills(data)
            save_data(data)
        elif choice == "4":
            edit_experience(data)
            save_data(data)
        elif choice == "5":
            edit_education(data)
            save_data(data)
        elif choice == "6":
            edit_certifications(data)
            save_data(data)
        elif choice == "7":
            edit_projects(data)
            save_data(data)
        elif choice == "8":
            generate_output(data)
        elif choice == "9":
            print("\n── Current Resume Data ──")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        elif choice == "0":
            save_data(data)
            print("\nGoodbye! Run again anytime to update your resume.")
            break
        else:
            print("  Invalid option. Try again.")


if __name__ == "__main__":
    main()
