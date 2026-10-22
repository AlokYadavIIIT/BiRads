"""
Script to apply fine-grained layout polish to build_report.py:
- TOC fits completely on Page 6 (no orphan lines on Page 7)
- Problem definition objectives fit cleanly across two balanced pages
- Implementation sections 8.2 and 8.3 balanced
- References evenly split across two balanced pages
"""
from pathlib import Path
import re
import subprocess

code = Path("build_report.py").read_text(encoding="utf-8")

# 1. Polish TOC style
code = code.replace(
    """.toc-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2pt;
    font-size: 10.5pt;
  }""",
    """.toc-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1pt;
    font-size: 10pt;
    line-height: 1.12;
  }"""
)

# 2. Adjust Chapter 4 margins so the objectives layout is balanced
code = code.replace(
    """  <h2>4.2 Research and Engineering Objectives</h2>
  <p>
    To resolve this problem, the primary objectives of the RP5 system are established as follows:
  </p>""",
    """  <h2>4.2 Research and Engineering Objectives</h2>
  <p style="margin-bottom: 4pt;">
    To resolve this problem, the primary objectives of the RP5 system are established as follows:
  </p>"""
)

# 3. Reference item polish: 2 evenly balanced pages
code = code.replace(
    """.reference-item {
    font-size: 10pt;
    line-height: 1.15;
    margin-bottom: 6pt;
    padding-left: 2em;
    text-indent: -2em;
    text-align: justify;
  }""",
    """.reference-item {
    font-size: 9.5pt;
    line-height: 1.15;
    margin-bottom: 4.5pt;
    padding-left: 2em;
    text-indent: -2em;
    text-align: justify;
  }"""
)

# 4. In Section 8.2: Adjust padding and image in 8.3 to avoid orphan bullets
code = code.replace(
    """<div class="page">
  <h2>8.3 RESTful API & Interactive Web UI</h2>""",
    """<div class="page" style="margin-top: 5pt;">
  <h2>8.3 RESTful API & Interactive Web UI</h2>"""
)

Path("build_report.py").write_text(code, encoding="utf-8")
print("Updated build_report.py with layout polish.")

# Run build_report.py
subprocess.run(["python", "build_report.py"], check=True)
print("Recompiled polished PDF.")
