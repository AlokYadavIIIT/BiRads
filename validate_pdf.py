"""
Updated PDF validator using pymupdf with UTF-8 safe output.
"""
import pymupdf
from pathlib import Path

PDF_PATH = Path("output/RP5_Project_Report.pdf")
PREVIEW_DIR = Path("output/page_previews")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

doc = pymupdf.open(PDF_PATH)
total_pages = len(doc)

print(f"Total pages in recompiled PDF: {total_pages}")

report_lines = []
blank_pages = []

for i in range(total_pages):
    page = doc[i]
    text = page.get_text().strip()
    images = page.get_images()
    
    char_count = len(text)
    word_count = len(text.split())
    
    # Save preview image
    pix = page.get_pixmap(dpi=150)
    img_path = PREVIEW_DIR / f"page_{i+1:02d}.png"
    pix.save(img_path)
    
    first_few = [l.strip() for l in text.split("\n") if l.strip()]
    first_line = " | ".join(first_few[:2]) if first_few else "EMPTY"
    
    # Filter safe ascii for printing
    safe_line = first_line.encode("ascii", errors="replace").decode("ascii")[:55]
    line_desc = f"Page {i+1:02d}: chars={char_count:4d}, words={word_count:3d}, images={len(images)}, preview: {safe_line}"
    print(line_desc)
    report_lines.append(line_desc)
    
    if char_count < 10 and len(images) == 0:
        blank_pages.append(i+1)

print("\n--- Validation Summary ---")
if blank_pages:
    print(f"ALERT: Detected blank pages: {blank_pages}")
else:
    print(f"SUCCESS: Zero blank pages detected! All {total_pages} pages contain valid text and graphic content.")

Path("output/validation_summary.txt").write_text("\n".join(report_lines), encoding="utf-8")
