"""
Perfect page boundary balance:
- Add page break before 4.2 so 4.1 and 4.2 each have a dedicated, fully-utilized page
- Add page break before 8.2 so Table 5 is on its own page, and 8.2 + 8.3 are cleanly grouped
- Add page break before Reference [15] so References are split 14 + 14 evenly
"""
from pathlib import Path
import subprocess

code = Path("build_report.py").read_text(encoding="utf-8")

# 1. Page break before 4.2
target_42 = "  <h2>4.2 Research and Engineering Objectives</h2>"
replacement_42 = """</div>
<div class="page">
  <h2>4.2 Research and Engineering Objectives</h2>"""
code = code.replace(target_42, replacement_42)

# 2. Page break before 8.2
target_82 = "  <h2>8.2 Core Module Implementations</h2>"
replacement_82 = """</div>
<div class="page">
  <h2>8.2 Core Module Implementations</h2>"""
code = code.replace(target_82, replacement_82)

# Remove the artificial margin-top on 8.3 so 8.2 and 8.3 flow naturally
code = code.replace('<div class="page" style="margin-top: 5pt;">\n  <h2>8.3 RESTful API & Interactive Web UI</h2>', '  <h2>8.3 RESTful API & Interactive Web UI</h2>')

# 3. Page break before Reference [15]
target_ref15 = '    <div class="reference-item">[15] S. Min et al.,'
replacement_ref15 = """  </div>
</div>
<div class="page">
  <div style="margin-top: 10pt;">
    <div class="reference-item">[15] S. Min et al.,"""
code = code.replace(target_ref15, replacement_ref15)

Path("build_report.py").write_text(code, encoding="utf-8")
print("Updated build_report.py with balanced page breaks.")

subprocess.run(["python", "build_report.py"], check=True)
print("Recompiled perfectly balanced PDF.")
