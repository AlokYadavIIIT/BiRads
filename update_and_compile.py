"""
Refined PDF and HTML builder for RP5 project report.
Removes min-height: 100vh to eliminate accidental blank pages.
Tightens TOC spacing and image heights for perfect page fits.
"""
from pathlib import Path
import subprocess

OUT_DIR = Path("output")
OUT_DIR.mkdir(parents=True, exist_ok=True)
HTML_PATH = OUT_DIR / "RP5_Project_Report.html"
PDF_PATH = OUT_DIR / "RP5_Project_Report.pdf"

# Read existing build_report.py content
old_code = Path("build_report.py").read_text(encoding="utf-8")

# Replace the style block with perfected print CSS
old_style_target = """  .page {
    page-break-after: always;
    break-after: page;
    position: relative;
    box-sizing: border-box;
    padding: 0;
    min-height: 100vh;
  }"""

new_style_replacement = """  @page {
    size: A4;
    margin: 20mm 20mm 20mm 20mm;
    @bottom-center {
      content: counter(page);
      font-family: 'Times New Roman', Times, serif;
      font-size: 11pt;
    }
  }

  @page:first {
    @bottom-center { content: ""; }
  }

  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.15;
    color: #000000;
    margin: 0;
    padding: 0;
    text-align: justify;
    text-justify: inter-word;
  }

  .page {
    page-break-before: always;
    break-before: page;
    position: relative;
    box-sizing: border-box;
    padding: 0;
    margin: 0;
  }

  .page:first-of-type {
    page-break-before: avoid;
    break-before: avoid;
  }"""

# Update style
new_code = old_code.replace(old_style_target, new_style_replacement)

# Update figure container max-height
new_code = new_code.replace(
    ".figure-container img, .figure-container svg {\n    max-width: 95%;\n    height: auto;\n    display: inline-block;\n  }",
    ".figure-container img, .figure-container svg {\n    max-width: 92%;\n    max-height: 220px;\n    height: auto;\n    display: inline-block;\n  }"
)

# Update TOC row margin
new_code = new_code.replace(
    ".toc-row {\n    display: flex;\n    justify-content: space-between;\n    margin-bottom: 4pt;\n    font-size: 11.5pt;\n  }",
    ".toc-row {\n    display: flex;\n    justify-content: space-between;\n    margin-bottom: 2pt;\n    font-size: 10.5pt;\n  }"
)

Path("build_report.py").write_text(new_code, encoding="utf-8")
print("Updated build_report.py with refined print CSS.")

# Re-run build_report.py
subprocess.run(["python", "build_report.py"], check=True)
print("Recompiled PDF successfully.")
