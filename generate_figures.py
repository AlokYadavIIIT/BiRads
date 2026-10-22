"""
Script to generate publication-grade SVG figures for the RP5 project report.
Generates genuine diagrams based on system architecture, workflows, and empirical results.
"""
from pathlib import Path

OUT_DIR = Path("output/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_svg(name: str, content: str):
    (OUT_DIR / name).write_text(content.strip(), encoding="utf-8")
    print(f"Generated {name}")

# 1. IIIT Bhopal Logo SVG
save_svg("iiit_bhopal_logo.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="160" height="160">
  <defs>
    <radialGradient id="goldGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fdfbf7"/>
      <stop offset="100%" stop-color="#f5efe6"/>
    </radialGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.2"/>
    </filter>
  </defs>
  <!-- Outer circle border -->
  <circle cx="150" cy="150" r="140" fill="#ffffff" stroke="#1a2b49" stroke-width="6"/>
  <circle cx="150" cy="150" r="132" fill="none" stroke="#d4af37" stroke-width="3"/>
  <circle cx="150" cy="150" r="102" fill="none" stroke="#1a2b49" stroke-width="2.5"/>
  
  <!-- Outer circular text path -->
  <path id="textCircleTop" d="M 40,150 A 110,110 0 0,1 260,150" fill="none"/>
  <path id="textCircleBottom" d="M 260,150 A 110,110 0 0,1 40,150" fill="none"/>
  
  <text font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1a2b49" text-anchor="middle">
    <textPath href="#textCircleTop" startOffset="50%">भारतीय सूचना प्रौद्योगिकी संस्थान भोपाल</textPath>
  </text>
  <text font-family="'Times New Roman', serif" font-size="9.5" font-weight="bold" fill="#1a2b49" text-anchor="middle">
    <textPath href="#textCircleBottom" startOffset="50%">INDIAN INSTITUTE OF INFORMATION TECHNOLOGY BHOPAL</textPath>
  </text>
  
  <!-- Central Emblem Elements -->
  <!-- Central background shield/circle -->
  <circle cx="150" cy="150" r="96" fill="#fdfdfd"/>
  
  <!-- Tower / Pi structure representing IT & Pillar -->
  <g id="emblemCore" transform="translate(150, 142)">
    <!-- Book / Base -->
    <path d="M -45,45 Q 0,38 45,45 L 42,50 Q 0,43 -42,50 Z" fill="#d4af37"/>
    <path d="M -45,43 Q 0,34 0,34 Q 0,34 45,43 L 42,47 Q 0,38 -42,47 Z" fill="#1a2b49"/>
    
    <!-- Motto ribbon below book -->
    <rect x="-42" y="52" width="84" height="15" rx="3" fill="#d4af37" opacity="0.9"/>
    <text x="0" y="63" font-family="'Times New Roman', serif" font-size="7.5" font-weight="bold" fill="#1a2b49" text-anchor="middle">विद्याऽमृतमश्नुते</text>
    
    <!-- Central Pillar / Pi Legs -->
    <!-- Left column -->
    <rect x="-24" y="-28" width="10" height="64" fill="#1a2b49" rx="1"/>
    <!-- Right column -->
    <rect x="14" y="-28" width="10" height="64" fill="#1a2b49" rx="1"/>
    <!-- Center antenna pole -->
    <rect x="-3" y="-36" width="6" height="72" fill="#1a2b49" rx="1"/>
    
    <!-- Cross lintel (Pi beam) -->
    <rect x="-36" y="-30" width="72" height="10" fill="#1a2b49" rx="2"/>
    
    <!-- Radio / Wifi waves radiating from antenna -->
    <path d="M -16,-44 A 20,20 0 0,1 16,-44" fill="none" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
    <path d="M -26,-52 A 32,32 0 0,1 26,-52" fill="none" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
    <path d="M -36,-60 A 44,44 0 0,1 36,-60" fill="none" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
    
    <!-- Central beacon dot -->
    <circle cx="0" cy="-38" r="4" fill="#d4af37"/>
  </g>
  <!-- Decorative stars -->
  <polygon points="35,150 37,153 41,153 38,155 39,159 35,156 31,159 32,155 29,153 33,153" fill="#d4af37"/>
  <polygon points="265,150 267,153 271,153 268,155 269,159 265,156 261,159 262,155 259,153 263,153" fill="#d4af37"/>
</svg>
''')

# 2. Figure 1: End-to-End RP5 System Architecture
save_svg("fig1_architecture.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 480" width="850" height="480">
  <defs>
    <linearGradient id="blueBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="tealBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f766e"/>
      <stop offset="100%" stop-color="#14b8a6"/>
    </linearGradient>
    <linearGradient id="purpleBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#581c87"/>
      <stop offset="100%" stop-color="#7e22ce"/>
    </linearGradient>
    <linearGradient id="amberBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
    <linearGradient id="greenBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#15803d"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </linearGradient>
    <linearGradient id="redBox" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#991b1b"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#334155"/>
    </marker>
  </defs>

  <rect width="850" height="480" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>

  <!-- Title banner -->
  <text x="425" y="30" font-family="'Times New Roman', serif" font-size="17" font-weight="bold" fill="#0f172a" text-anchor="middle">
    RP5: BI-RADS-Grounded Retrieval-Augmented Generation Architecture
  </text>

  <!-- Stage 0: Finding Card -->
  <g transform="translate(40, 60)" filter="url(#cardShadow)">
    <rect width="210" height="90" rx="8" fill="url(#blueBox)"/>
    <text x="105" y="28" font-family="'Times New Roman', serif" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Finding Card Input (JSON)</text>
    <text x="105" y="50" font-family="'Times New Roman', serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Modality / Laterality / Density</text>
    <text x="105" y="66" font-family="'Times New Roman', serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Lesion morphology &amp; descriptors</text>
    <text x="105" y="80" font-family="'Times New Roman', serif" font-size="10.5" fill="#fef08a" text-anchor="middle">[Label Isolation Enforced]</text>
  </g>

  <!-- Arrow to Retrieval -->
  <line x1="250" y1="105" x2="310" y2="105" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="280" y="95" font-family="'Times New Roman', serif" font-size="10" fill="#475569" text-anchor="middle">q serialization</text>

  <!-- Stage 1: Retrieval -->
  <g transform="translate(315, 55)" filter="url(#cardShadow)">
    <rect width="230" height="100" rx="8" fill="url(#tealBox)"/>
    <text x="115" y="26" font-family="'Times New Roman', serif" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Retrieval Engine</text>
    <text x="115" y="46" font-family="'Times New Roman', serif" font-size="11" fill="#ccfbf1" text-anchor="middle">• all-MiniLM-L6-v2 (384-dim)</text>
    <text x="115" y="62" font-family="'Times New Roman', serif" font-size="11" fill="#ccfbf1" text-anchor="middle">• FAISS L2 / Inner Product (top-k=8)</text>
    <text x="115" y="78" font-family="'Times New Roman', serif" font-size="11" fill="#ccfbf1" text-anchor="middle">• Four-Stratum Ingestion (S1–S4)</text>
    <text x="115" y="92" font-family="'Times New Roman', serif" font-size="10" fill="#fef08a" text-anchor="middle">• S4 Few-Shot Exemplar Selection</text>
  </g>

  <!-- Arrow to Generation -->
  <line x1="545" y1="105" x2="605" y2="105" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="575" y="95" font-family="'Times New Roman', serif" font-size="10" fill="#475569" text-anchor="middle">Passages + Prompts</text>

  <!-- Stage 2: Dual Generation Heads -->
  <g transform="translate(610, 50)" filter="url(#cardShadow)">
    <rect width="200" height="110" rx="8" fill="url(#purpleBox)"/>
    <text x="100" y="24" font-family="'Times New Roman', serif" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Dual Generation Heads</text>
    <rect x="12" y="34" width="176" height="32" rx="4" fill="#ffffff" fill-opacity="0.15"/>
    <text x="100" y="48" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Clinician Head</text>
    <text x="100" y="61" font-family="'Times New Roman', serif" font-size="10" fill="#f3e8ff" text-anchor="middle">Strict JSON Structured Report</text>
    <rect x="12" y="70" width="176" height="32" rx="4" fill="#ffffff" fill-opacity="0.15"/>
    <text x="100" y="84" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Patient Head</text>
    <text x="100" y="96" font-family="'Times New Roman', serif" font-size="10" fill="#fef08a" text-anchor="middle">FK Readability Target &lt; 8.0</text>
  </g>

  <!-- Arrow down to Attribution -->
  <path d="M 710,160 L 710,210 L 460,210" fill="none" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="600" y="202" font-family="'Times New Roman', serif" font-size="10.5" fill="#475569" text-anchor="middle">Drafts + Retrieved Chunks</text>

  <!-- Stage 3: Attribution Engine -->
  <g transform="translate(180, 225)" filter="url(#cardShadow)">
    <rect width="270" height="110" rx="8" fill="url(#amberBox)"/>
    <text x="135" y="26" font-family="'Times New Roman', serif" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Multi-Tier Attribution Engine</text>
    <text x="135" y="48" font-family="'Times New Roman', serif" font-size="11" fill="#fffbeb" text-anchor="middle">• Claim Decomposition &amp; Normalization</text>
    <text x="135" y="64" font-family="'Times New Roman', serif" font-size="11" fill="#fffbeb" text-anchor="middle">• Lexical Overlap + MiniLM Cosine (&#8805; 0.45)</text>
    <text x="135" y="80" font-family="'Times New Roman', serif" font-size="11" fill="#fffbeb" text-anchor="middle">• Negation Conflict Verification</text>
    <text x="135" y="96" font-family="'Times New Roman', serif" font-size="10.5" fill="#fef08a" text-anchor="middle">• Laterality &amp; Size Mismatch Rejection</text>
  </g>

  <!-- Arrow to Guard Agent -->
  <line x1="450" y1="280" x2="520" y2="280" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="485" y="272" font-family="'Times New Roman', serif" font-size="10" fill="#475569" text-anchor="middle">Aligned Claims</text>

  <!-- Stage 4: Guard Agent -->
  <g transform="translate(525, 225)" filter="url(#cardShadow)">
    <rect width="260" height="110" rx="8" fill="#1e293b"/>
    <text x="130" y="26" font-family="'Times New Roman', serif" font-size="14" font-weight="bold" fill="#38bdf8" text-anchor="middle">Clinical Guard Agent</text>
    <text x="130" y="48" font-family="'Times New Roman', serif" font-size="11" fill="#e2e8f0" text-anchor="middle">• BI-RADS Category &#8660; Recommendation</text>
    <text x="130" y="64" font-family="'Times New Roman', serif" font-size="11" fill="#e2e8f0" text-anchor="middle">• Descriptor Allowlisting (Strata 1 &amp; 2)</text>
    <text x="130" y="80" font-family="'Times New Roman', serif" font-size="11" fill="#e2e8f0" text-anchor="middle">• Citation Coverage Check (&#8805; 70%)</text>
    <text x="130" y="96" font-family="'Times New Roman', serif" font-size="10.5" fill="#facc15" text-anchor="middle">• Confidence Threshold Filter (&#964; &#8805; 0.50)</text>
  </g>

  <!-- Fork: Pass vs Abstain -->
  <path d="M 655,335 L 655,375 L 530,375 L 530,405" fill="none" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="580" y="368" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#16a34a" text-anchor="middle">ALL CHECKS PASS</text>

  <path d="M 655,335 L 655,375 L 750,375 L 750,405" fill="none" stroke="#dc2626" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="715" y="368" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#dc2626" text-anchor="middle">VIOLATION DETECTED</text>

  <!-- Output 1: Valid Report -->
  <g transform="translate(430, 410)" filter="url(#cardShadow)">
    <rect width="200" height="55" rx="6" fill="url(#greenBox)"/>
    <text x="100" y="24" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">VALID CLINICAL REPORT</text>
    <text x="100" y="42" font-family="'Times New Roman', serif" font-size="10.5" fill="#f0fdf4" text-anchor="middle">Clinician JSON + Patient Summary</text>
  </g>

  <!-- Output 2: Safe Abstention -->
  <g transform="translate(650, 410)" filter="url(#cardShadow)">
    <rect width="180" height="55" rx="6" fill="url(#redBox)"/>
    <text x="90" y="24" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">SAFE ABSTENTION</text>
    <text x="90" y="42" font-family="'Times New Roman', serif" font-size="10.5" fill="#fef2f2" text-anchor="middle">Logged with Missing Reason</text>
  </g>
</svg>
''')

# 3. Figure 2: Four-Stratum Knowledge Architecture
save_svg("fig2_four_stratum.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="800" height="360">
  <defs>
    <filter id="boxShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="2" dy="2" stdDeviation="2.5" flood-opacity="0.12"/>
    </filter>
  </defs>
  <rect width="800" height="360" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  
  <text x="400" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Four-Stratum Knowledge Ingestion &amp; Chunking Model
  </text>
  
  <!-- Stratum 1 -->
  <g transform="translate(30, 50)" filter="url(#boxShadow)">
    <rect width="165" height="230" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <rect width="165" height="42" rx="8" fill="#3b82f6"/>
    <text x="82" y="26" font-family="'Times New Roman', serif" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Stratum 1: Lexicon</text>
    <text x="15" y="65" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1e3a8a">• Source:</text>
    <text x="15" y="80" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155">ACR BI-RADS Atlas</text>
    <text x="15" y="105" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1e3a8a">• Contents:</text>
    <text x="15" y="120" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Morphology, margins,</text>
    <text x="15" y="134" font-family="'Times New Roman', serif" font-size="10" fill="#334155">calcification descriptors,</text>
    <text x="15" y="148" font-family="'Times New Roman', serif" font-size="10" fill="#334155">mass descriptors.</text>
    <text x="15" y="175" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1e3a8a">• Chunking Rule:</text>
    <text x="15" y="190" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Section-bound per lesion</text>
    <text x="15" y="204" font-family="'Times New Roman', serif" font-size="10" fill="#334155">type (18–49 tokens).</text>
  </g>

  <!-- Stratum 2 -->
  <g transform="translate(220, 50)" filter="url(#boxShadow)">
    <rect width="165" height="230" rx="8" fill="#f0fdfa" stroke="#0d9488" stroke-width="2"/>
    <rect width="165" height="42" rx="8" fill="#0d9488"/>
    <text x="82" y="26" font-family="'Times New Roman', serif" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Stratum 2: Guidance</text>
    <text x="15" y="65" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f766e">• Source:</text>
    <text x="15" y="80" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155">ACR Practice Parameters</text>
    <text x="15" y="105" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f766e">• Contents:</text>
    <text x="15" y="120" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Follow-up protocols,</text>
    <text x="15" y="134" font-family="'Times New Roman', serif" font-size="10" fill="#334155">biopsy indications,</text>
    <text x="15" y="148" font-family="'Times New Roman', serif" font-size="10" fill="#334155">screening intervals.</text>
    <text x="15" y="175" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f766e">• Chunking Rule:</text>
    <text x="15" y="190" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Category-mapped</text>
    <text x="15" y="204" font-family="'Times New Roman', serif" font-size="10" fill="#334155">rules (~108 tokens).</text>
  </g>

  <!-- Stratum 3 -->
  <g transform="translate(410, 50)" filter="url(#boxShadow)">
    <rect width="165" height="230" rx="8" fill="#fdf4ff" stroke="#a855f7" stroke-width="2"/>
    <rect width="165" height="42" rx="8" fill="#a855f7"/>
    <text x="82" y="26" font-family="'Times New Roman', serif" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Stratum 3: Templates</text>
    <text x="15" y="65" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#7e22ce">• Source:</text>
    <text x="15" y="80" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155">Institutional Norms</text>
    <text x="15" y="105" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#7e22ce">• Contents:</text>
    <text x="15" y="120" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Structured report shells:</text>
    <text x="15" y="134" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Clinical History, Findings,</text>
    <text x="15" y="148" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Assessment, Recs.</text>
    <text x="15" y="175" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#7e22ce">• Chunking Rule:</text>
    <text x="15" y="190" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Section slots</text>
    <text x="15" y="204" font-family="'Times New Roman', serif" font-size="10" fill="#334155">(4–17 tokens).</text>
  </g>

  <!-- Stratum 4 -->
  <g transform="translate(600, 50)" filter="url(#boxShadow)">
    <rect width="165" height="230" rx="8" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
    <rect width="165" height="42" rx="8" fill="#f59e0b"/>
    <text x="82" y="26" font-family="'Times New Roman', serif" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Stratum 4: Examples</text>
    <text x="15" y="65" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#b45309">• Source:</text>
    <text x="15" y="80" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155">Expert Cases (Disclosed)</text>
    <text x="15" y="105" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#b45309">• Contents:</text>
    <text x="15" y="120" font-family="'Times New Roman', serif" font-size="10" fill="#334155">De-identified mammogram</text>
    <text x="15" y="134" font-family="'Times New Roman', serif" font-size="10" fill="#334155">vignettes with few-shot</text>
    <text x="15" y="148" font-family="'Times New Roman', serif" font-size="10" fill="#334155">prompt demonstrations.</text>
    <text x="15" y="175" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#b45309">• Chunking Rule:</text>
    <text x="15" y="190" font-family="'Times New Roman', serif" font-size="10" fill="#334155">Exemplar case units</text>
    <text x="15" y="204" font-family="'Times New Roman', serif" font-size="10" fill="#334155">(11–12 tokens).</text>
  </g>

  <!-- Provenance Footer -->
  <rect x="30" y="295" width="735" height="45" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1"/>
  <text x="400" y="315" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1e293b" text-anchor="middle">
    Immutable Provenance Ledger (<tspan font-family="monospace">provenance.jsonl</tspan>):
  </text>
  <text x="400" y="330" font-family="'Times New Roman', serif" font-size="10.5" fill="#475569" text-anchor="middle">
    Tracks Document ID, Stratum Assignment, Source Path, Preprocessing Transformations, and UTC Timestamp per Chunk.
  </text>
</svg>
''')

# 4. Figure 3: Attribution Alignment & Conflict Engine
save_svg("fig3_attribution_logic.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 380" width="820" height="380">
  <defs>
    <marker id="attrArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#334155"/>
    </marker>
  </defs>
  <rect width="820" height="380" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="410" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Multi-Tier Attribution Alignment &amp; Contradiction Resolution Flow
  </text>

  <!-- Input Draft Sentence -->
  <g transform="translate(30, 60)">
    <rect width="180" height="70" rx="6" fill="#e0e7ff" stroke="#4f46e5" stroke-width="1.5"/>
    <text x="90" y="25" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#312e81" text-anchor="middle">Draft Claim Sentence</text>
    <text x="90" y="45" font-family="'Times New Roman', serif" font-size="10" fill="#3730a3" text-anchor="middle">Decomposed into atomic</text>
    <text x="90" y="58" font-family="'Times New Roman', serif" font-size="10" fill="#3730a3" text-anchor="middle">clinical proposition (c_i)</text>
  </g>

  <line x1="210" y1="95" x2="260" y2="95" stroke="#334155" stroke-width="2" marker-end="url(#attrArrow)"/>

  <!-- Step 1: Lexical + Semantic Overlap -->
  <g transform="translate(265, 50)">
    <rect width="260" height="90" rx="6" fill="#f8fafc" stroke="#0284c7" stroke-width="2"/>
    <text x="130" y="24" font-family="'Times New Roman', serif" font-size="12.5" font-weight="bold" fill="#0369a1" text-anchor="middle">1. Dual-Evidence Scorer</text>
    <text x="130" y="44" font-family="'Times New Roman', serif" font-size="10.5" fill="#0f172a" text-anchor="middle">• Jaccard Lexical Overlap &#8805; 0.35</text>
    <text x="130" y="60" font-family="'Times New Roman', serif" font-size="10.5" fill="#0f172a" text-anchor="middle">• MiniLM-L6 Embedding Cosine &#8805; 0.45</text>
    <text x="130" y="76" font-family="'Times New Roman', serif" font-size="9.5" fill="#64748b" text-anchor="middle">Ranked against top-k retrieved chunks</text>
  </g>

  <!-- Decision diamond: Above Threshold? -->
  <line x1="525" y1="95" x2="575" y2="95" stroke="#334155" stroke-width="2" marker-end="url(#attrArrow)"/>

  <g transform="translate(580, 55)">
    <polygon points="50,0 100,40 50,80 0,40" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="50" y="38" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#92400e" text-anchor="middle">Sim &#8805; 0.45</text>
    <text x="50" y="50" font-family="'Times New Roman', serif" font-size="9.5" fill="#92400e" text-anchor="middle">&amp; Lex &#8805; 0.35?</text>
  </g>

  <!-- Branch NO -->
  <line x1="680" y1="95" x2="720" y2="95" stroke="#dc2626" stroke-width="2" marker-end="url(#attrArrow)"/>
  <text x="698" y="88" font-family="'Times New Roman', serif" font-size="9.5" font-weight="bold" fill="#dc2626">NO</text>
  <g transform="translate(725, 70)">
    <rect width="80" height="50" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="40" y="24" font-family="'Times New Roman', serif" font-size="10.5" font-weight="bold" fill="#991b1b" text-anchor="middle">FLAG</text>
    <text x="40" y="38" font-family="'Times New Roman', serif" font-size="9" fill="#991b1b" text-anchor="middle">Unsupported</text>
  </g>

  <!-- Branch YES down to Clinical Contradiction Policy -->
  <line x1="630" y1="135" x2="630" y2="185" stroke="#16a34a" stroke-width="2" marker-end="url(#attrArrow)"/>
  <text x="642" y="160" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#16a34a">YES</text>

  <!-- Step 2: Clinical Domain Contradiction Guard -->
  <g transform="translate(180, 190)">
    <rect width="470" height="115" rx="8" fill="#fdf4ff" stroke="#9333ea" stroke-width="2"/>
    <text x="235" y="25" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#6b21a8" text-anchor="middle">2. Explicit Clinical Conflict &amp; Assertion Filters</text>
    
    <g transform="translate(15, 38)">
      <rect width="135" height="65" rx="4" fill="#ffffff" stroke="#c084fc"/>
      <text x="67" y="18" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#7e22ce" text-anchor="middle">Negation Check</text>
      <text x="67" y="34" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">"No mass" vs</text>
      <text x="67" y="46" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">"mass present"</text>
      <text x="67" y="58" font-family="'Times New Roman', serif" font-size="8.5" fill="#dc2626" text-anchor="middle">&#8680; Contradiction</text>
    </g>

    <g transform="translate(165, 38)">
      <rect width="135" height="65" rx="4" fill="#ffffff" stroke="#c084fc"/>
      <text x="67" y="18" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#7e22ce" text-anchor="middle">Laterality Check</text>
      <text x="67" y="34" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">"left breast" vs</text>
      <text x="67" y="46" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">"right breast"</text>
      <text x="67" y="58" font-family="'Times New Roman', serif" font-size="8.5" fill="#dc2626" text-anchor="middle">&#8680; Mismatch</text>
    </g>

    <g transform="translate(315, 38)">
      <rect width="140" height="65" rx="4" fill="#ffffff" stroke="#c084fc"/>
      <text x="70" y="18" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#7e22ce" text-anchor="middle">Measurement Check</text>
      <text x="70" y="34" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">"12.0 mm" vs "25 mm"</text>
      <text x="70" y="46" font-family="'Times New Roman', serif" font-size="9" fill="#475569" text-anchor="middle">Unit norm &amp; range test</text>
      <text x="70" y="58" font-family="'Times New Roman', serif" font-size="8.5" fill="#dc2626" text-anchor="middle">&#8680; Size Mismatch</text>
    </g>
  </g>

  <!-- Output outcomes -->
  <line x1="415" y1="305" x2="415" y2="335" stroke="#16a34a" stroke-width="2" marker-end="url(#attrArrow)"/>
  <rect x="250" y="338" width="330" height="30" rx="4" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="415" y="357" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#14532d" text-anchor="middle">
    Verified Citation Support Attached (Coverage Metric: 100%)
  </text>
</svg>
''')

# 5. Figure 4: Guard Agent Decision Tree
save_svg("fig4_guard_decision_tree.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 440" width="850" height="440">
  <defs>
    <marker id="treeArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#334155"/>
    </marker>
  </defs>
  <rect width="850" height="440" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="425" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Guard Agent Multi-Gate Decision Tree &amp; Abstention Policy
  </text>

  <!-- Input Draft -->
  <g transform="translate(40, 50)">
    <rect width="140" height="50" rx="6" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>
    <text x="70" y="25" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#1e293b" text-anchor="middle">Input Draft</text>
    <text x="70" y="40" font-family="'Times New Roman', serif" font-size="10" fill="#475569" text-anchor="middle">(Clinician + Patient)</text>
  </g>

  <line x1="180" y1="75" x2="225" y2="75" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 1: Strict JSON Schema -->
  <g transform="translate(230, 45)">
    <rect width="160" height="60" rx="6" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.5"/>
    <text x="80" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0369a1" text-anchor="middle">Gate 1: Schema</text>
    <text x="80" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#0c4a6e" text-anchor="middle">Valid JSON, keys present,</text>
    <text x="80" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#0c4a6e" text-anchor="middle">category in [0..6]?</text>
  </g>

  <line x1="390" y1="75" x2="435" y2="75" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 2: Lexicon Allowlisting -->
  <g transform="translate(440, 45)">
    <rect width="170" height="60" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
    <text x="85" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">Gate 2: Descriptors</text>
    <text x="85" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#14532d" text-anchor="middle">All terms in finding card</text>
    <text x="85" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#14532d" text-anchor="middle">grounded in Strata S1/S2?</text>
  </g>

  <line x1="610" y1="75" x2="655" y2="75" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 3: Category Harmony -->
  <g transform="translate(660, 45)">
    <rect width="165" height="60" rx="6" fill="#fefce8" stroke="#ca8a04" stroke-width="1.5"/>
    <text x="82" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#a16207" text-anchor="middle">Gate 3: Harmony</text>
    <text x="82" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#713f12" text-anchor="middle">Recommendation consistent</text>
    <text x="82" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#713f12" text-anchor="middle">with BI-RADS assessment?</text>
  </g>

  <!-- Row 2 Gates -->
  <path d="M 742,105 L 742,150 L 742,175" fill="none" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 4: Citation Coverage -->
  <g transform="translate(660, 180)">
    <rect width="165" height="60" rx="6" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5"/>
    <text x="82" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#7e22ce" text-anchor="middle">Gate 4: Citations</text>
    <text x="82" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#581c87" text-anchor="middle">Citation coverage &#8805; 70%</text>
    <text x="82" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#581c87" text-anchor="middle">supported by evidence?</text>
  </g>

  <line x1="660" y1="210" x2="615" y2="210" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 5: Readability -->
  <g transform="translate(440, 180)">
    <rect width="170" height="60" rx="6" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5"/>
    <text x="85" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#c2410c" text-anchor="middle">Gate 5: Readability</text>
    <text x="85" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#7c2d12" text-anchor="middle">Patient Flesch-Kincaid &#8804; 8.0</text>
    <text x="85" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#7c2d12" text-anchor="middle">(1 regen attempted if &gt; 8)?</text>
  </g>

  <line x1="440" y1="210" x2="395" y2="210" stroke="#334155" stroke-width="2" marker-end="url(#treeArrow)"/>

  <!-- Gate 6: Composite Confidence -->
  <g transform="translate(230, 180)">
    <rect width="160" height="60" rx="6" fill="#fdf2f8" stroke="#db2777" stroke-width="1.5"/>
    <text x="80" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#be185d" text-anchor="middle">Gate 6: Confidence &#964;</text>
    <text x="80" y="40" font-family="'Times New Roman', serif" font-size="9.5" fill="#831843" text-anchor="middle">Composite score &#964; &#8805; 0.50</text>
    <text x="80" y="52" font-family="'Times New Roman', serif" font-size="9.5" fill="#831843" text-anchor="middle">(0.6 logprob + 0.4 ret)?</text>
  </g>

  <!-- Final Pass Arrow -->
  <line x1="230" y1="210" x2="150" y2="210" stroke="#16a34a" stroke-width="2.5" marker-end="url(#treeArrow)"/>
  
  <!-- Final Green Success Box -->
  <g transform="translate(30, 180)">
    <rect width="115" height="60" rx="6" fill="#15803d" stroke="#14532d" stroke-width="2"/>
    <text x="57" y="26" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">APPROVAL</text>
    <text x="57" y="44" font-family="'Times New Roman', serif" font-size="10" fill="#f0fdf4" text-anchor="middle">Emit Clinician &amp;</text>
    <text x="57" y="55" font-family="'Times New Roman', serif" font-size="10" fill="#f0fdf4" text-anchor="middle">Patient Output</text>
  </g>

  <!-- Red Abstain Box at Bottom -->
  <g transform="translate(220, 310)">
    <rect width="400" height="105" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
    <text x="200" y="26" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#991b1b" text-anchor="middle">SAFE ABSTENTION GATEWAY (ABSTAIN)</text>
    <text x="200" y="46" font-family="'Times New Roman', serif" font-size="10.5" fill="#7f1d1d" text-anchor="middle">Triggered if ANY of the 6 validation gates fail.</text>
    <text x="200" y="64" font-family="'Times New Roman', serif" font-size="10" fill="#7f1d1d" text-anchor="middle">• Emits explicit failure reason (e.g., <tspan font-family="monospace">unsupported_descriptor</tspan>)</text>
    <text x="200" y="80" font-family="'Times New Roman', serif" font-size="10" fill="#7f1d1d" text-anchor="middle">• Flags clinical review requirement &amp; preserves patient safety</text>
    <text x="200" y="96" font-family="'Times New Roman', serif" font-size="10" fill="#7f1d1d" text-anchor="middle">• Prevents unsafe automation bias and hallucinated radiology claims</text>
  </g>

  <!-- Connect failure lines from each gate to Abstention -->
  <path d="M 310,105 L 310,310" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#treeArrow)"/>
  <path d="M 525,105 L 525,310" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#treeArrow)"/>
  <path d="M 742,240 L 742,280 L 580,280 L 580,310" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#treeArrow)"/>
  <path d="M 310,240 L 310,310" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#treeArrow)"/>
</svg>
''')

# 6. Figure 5: Level 0 and Level 1 Data Flow Diagrams (DFD)
save_svg("fig5_dfd_level0_1.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 460" width="840" height="460">
  <defs>
    <marker id="dfdArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#1e293b"/>
    </marker>
  </defs>
  <rect width="840" height="460" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  
  <!-- DFD Level 0 (Context) -->
  <text x="420" y="24" font-family="'Times New Roman', serif" font-size="15" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Data Flow Diagram — Level 0 (Context Level Diagram)
  </text>

  <!-- Entity: Radiologist -->
  <g transform="translate(40, 45)">
    <rect width="130" height="60" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>
    <text x="65" y="28" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Radiologist /</text>
    <text x="65" y="44" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">PACS Source</text>
  </g>

  <!-- Process 0.0: RP5 System -->
  <g transform="translate(330, 40)">
    <circle cx="90" cy="35" r="42" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
    <text x="90" y="32" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#1e40af" text-anchor="middle">0.0 RP5</text>
    <text x="90" y="46" font-family="'Times New Roman', serif" font-size="10.5" fill="#1e40af" text-anchor="middle">RAG System</text>
  </g>

  <!-- Entity: Patient Portal -->
  <g transform="translate(670, 45)">
    <rect width="130" height="60" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>
    <text x="65" y="28" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Patient /</text>
    <text x="65" y="44" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">EMR Portal</text>
  </g>

  <!-- Data flows Level 0 -->
  <line x1="170" y1="65" x2="330" y2="65" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <text x="250" y="58" font-family="'Times New Roman', serif" font-size="9.5" fill="#334155" text-anchor="middle">Finding Card Data</text>

  <line x1="330" y1="85" x2="170" y2="85" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <text x="250" y="99" font-family="'Times New Roman', serif" font-size="9.5" fill="#334155" text-anchor="middle">Clinician JSON Report / Abstain</text>

  <line x1="510" y1="75" x2="670" y2="75" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <text x="590" y="67" font-family="'Times New Roman', serif" font-size="9.5" fill="#334155" text-anchor="middle">Plain Patient Summary (FK &#8804; 8)</text>

  <!-- Divider -->
  <line x1="40" y1="125" x2="800" y2="125" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="6"/>

  <!-- DFD Level 1 -->
  <text x="420" y="150" font-family="'Times New Roman', serif" font-size="15" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Data Flow Diagram — Level 1 (Subsystem Decomposed Diagram)
  </text>

  <!-- Process 1.0: Normalization -->
  <g transform="translate(40, 180)">
    <rect width="130" height="50" rx="20" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>
    <text x="65" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">1.0 Ingestion &amp;</text>
    <text x="65" y="38" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155" text-anchor="middle">Normalization</text>
  </g>

  <!-- Data Store D1: Corpus -->
  <g transform="translate(230, 175)">
    <line x1="0" y1="0" x2="130" y2="0" stroke="#0284c7" stroke-width="2"/>
    <line x1="0" y1="60" x2="130" y2="60" stroke="#0284c7" stroke-width="2"/>
    <text x="65" y="26" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0369a1" text-anchor="middle">D1 Four-Stratum</text>
    <text x="65" y="44" font-family="'Times New Roman', serif" font-size="10" fill="#0369a1" text-anchor="middle">Corpus (S1-S4)</text>
  </g>

  <!-- Process 2.0: Retrieval -->
  <g transform="translate(420, 180)">
    <rect width="130" height="50" rx="20" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>
    <text x="65" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">2.0 Dense MiniLM</text>
    <text x="65" y="38" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155" text-anchor="middle">FAISS Retrieval</text>
  </g>

  <!-- Process 3.0: Dual Generation -->
  <g transform="translate(650, 180)">
    <rect width="140" height="50" rx="20" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>
    <text x="70" y="24" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">3.0 Dual Head</text>
    <text x="70" y="38" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155" text-anchor="middle">LLM Generation</text>
  </g>

  <!-- Process 4.0: Attribution -->
  <g transform="translate(260, 310)">
    <rect width="150" height="55" rx="20" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>
    <text x="75" y="26" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">4.0 Attribution &amp;</text>
    <text x="75" y="42" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155" text-anchor="middle">Contradiction Align</text>
  </g>

  <!-- Process 5.0: Guard -->
  <g transform="translate(530, 310)">
    <rect width="150" height="55" rx="20" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>
    <text x="75" y="26" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">5.0 Clinical Guard</text>
    <text x="75" y="42" font-family="'Times New Roman', serif" font-size="10.5" fill="#334155" text-anchor="middle">&amp; Abstention Gate</text>
  </g>

  <!-- Connections Level 1 -->
  <line x1="170" y1="205" x2="230" y2="205" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <line x1="360" y1="205" x2="420" y2="205" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <line x1="550" y1="205" x2="650" y2="205" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  
  <path d="M 720,230 L 720,270 L 335,270 L 335,310" fill="none" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <text x="530" y="265" font-family="'Times New Roman', serif" font-size="9.5" fill="#475569" text-anchor="middle">Unverified Drafts</text>

  <line x1="410" y1="337" x2="530" y2="337" stroke="#1e293b" stroke-width="1.8" marker-end="url(#dfdArrow)"/>
  <text x="470" y="330" font-family="'Times New Roman', serif" font-size="9.5" fill="#475569" text-anchor="middle">Claim Map</text>

  <!-- Output endpoints -->
  <line x1="680" y1="337" x2="760" y2="337" stroke="#16a34a" stroke-width="2" marker-end="url(#dfdArrow)"/>
  <text x="720" y="330" font-family="'Times New Roman', serif" font-size="9" font-weight="bold" fill="#16a34a" text-anchor="middle">Report Pass</text>

  <path d="M 605,365 L 605,410 L 450,410" fill="none" stroke="#dc2626" stroke-width="2" marker-end="url(#dfdArrow)"/>
  <text x="560" y="402" font-family="'Times New Roman', serif" font-size="9" font-weight="bold" fill="#dc2626" text-anchor="middle">Safe Abstain</text>
  
  <rect x="330" y="395" width="120" height="30" rx="4" fill="#fee2e2" stroke="#dc2626"/>
  <text x="390" y="415" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#991b1b" text-anchor="middle">Abstention Log</text>
</svg>
''')

# 7. Figure 6: Evaluation Metrics Chart
save_svg("fig6_evaluation_metrics.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 360" width="760" height="360">
  <rect width="760" height="360" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="380" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Primary Evaluation Benchmarks on Non-Abstained Cases (N=3 Vignettes)
  </text>

  <!-- Graph grid -->
  <g transform="translate(80, 50)">
    <!-- Y-axis line -->
    <line x1="0" y1="0" x2="0" y2="240" stroke="#64748b" stroke-width="1.5"/>
    <!-- X-axis line -->
    <line x1="0" y1="240" x2="620" y2="240" stroke="#64748b" stroke-width="1.5"/>

    <!-- Grid lines & ticks -->
    <line x1="0" y1="180" x2="620" y2="180" stroke="#e2e8f0" stroke-width="1"/>
    <text x="-15" y="185" font-family="'Times New Roman', serif" font-size="10" fill="#64748b" text-anchor="end">0.25</text>

    <line x1="0" y1="120" x2="620" y2="120" stroke="#e2e8f0" stroke-width="1"/>
    <text x="-15" y="125" font-family="'Times New Roman', serif" font-size="10" fill="#64748b" text-anchor="end">0.50</text>

    <line x1="0" y1="60" x2="620" y2="60" stroke="#e2e8f0" stroke-width="1"/>
    <text x="-15" y="65" font-family="'Times New Roman', serif" font-size="10" fill="#64748b" text-anchor="end">0.75</text>

    <line x1="0" y1="0" x2="620" y2="0" stroke="#e2e8f0" stroke-width="1"/>
    <text x="-15" y="5" font-family="'Times New Roman', serif" font-size="10" fill="#64748b" text-anchor="end">1.00</text>

    <!-- Bars -->
    <!-- Bar 1: Gwet's AC1 -->
    <rect x="50" y="0" width="80" height="240" fill="#2563eb" rx="3"/>
    <text x="90" y="-10" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#1e3a8a" text-anchor="middle">1.00</text>
    <text x="90" y="260" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">Gwet AC1</text>
    <text x="90" y="275" font-family="'Times New Roman', serif" font-size="9.5" fill="#64748b" text-anchor="middle">(Agreement)</text>

    <!-- Bar 2: Citation Coverage -->
    <rect x="190" y="0" width="80" height="240" fill="#0d9488" rx="3"/>
    <text x="230" y="-10" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f766e" text-anchor="middle">1.00 (100%)</text>
    <text x="230" y="260" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">Citation Cov.</text>
    <text x="230" y="275" font-family="'Times New Roman', serif" font-size="9.5" fill="#64748b" text-anchor="middle">(&#8805; 0.70 Target)</text>

    <!-- Bar 3: Abstention Rate -->
    <rect x="330" y="160" width="80" height="80" fill="#f59e0b" rx="3"/>
    <text x="370" y="150" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#b45309" text-anchor="middle">0.333 (33%)</text>
    <text x="370" y="260" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">Abstention</text>
    <text x="370" y="275" font-family="'Times New Roman', serif" font-size="9.5" fill="#64748b" text-anchor="middle">(Safe Refusal)</text>

    <!-- Bar 4: Readability Normalized (6.65 / 12 scale = 0.554) -->
    <rect x="470" y="107" width="80" height="133" fill="#8b5cf6" rx="3"/>
    <text x="510" y="97" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#6d28d9" text-anchor="middle">6.65 Grade</text>
    <text x="510" y="260" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">Flesch-Kincaid</text>
    <text x="510" y="275" font-family="'Times New Roman', serif" font-size="9.5" fill="#64748b" text-anchor="middle">(Target &#8804; 8.0)</text>
  </g>
</svg>
''')

# 8. Figure 7: Latency Breakdown Chart
save_svg("fig7_latency_breakdown.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 340" width="780" height="340">
  <rect width="780" height="340" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="390" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Component Latency Profiles: Cold-Start vs Warm Execution
  </text>

  <!-- Horizontal bar chart -->
  <g transform="translate(180, 50)">
    <!-- Stage 1: Retrieval -->
    <text x="-15" y="32" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="end">Retrieval (FAISS)</text>
    <rect x="0" y="15" width="24" height="24" fill="#0284c7" rx="3"/>
    <text x="35" y="32" font-family="'Times New Roman', serif" font-size="10.5" fill="#0369a1">24.5 ms (0.3%)</text>

    <!-- Stage 2: Clinician Head -->
    <text x="-15" y="82" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="end">Clinician Head</text>
    <rect x="0" y="65" width="6" height="24" fill="#6366f1" rx="3"/>
    <text x="15" y="82" font-family="'Times New Roman', serif" font-size="10.5" fill="#4338ca">0.26 ms (&lt;0.01%)</text>

    <!-- Stage 3: Patient Head -->
    <text x="-15" y="132" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="end">Patient Head (Model)</text>
    <rect x="0" y="115" width="120" height="24" fill="#a855f7" rx="3"/>
    <text x="130" y="132" font-family="'Times New Roman', serif" font-size="10.5" fill="#7e22ce">1634.1 ms (21.8%)</text>

    <!-- Stage 4: Attribution -->
    <text x="-15" y="182" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="end">Attribution &amp; MiniLM</text>
    <rect x="0" y="165" width="420" height="24" fill="#f59e0b" rx="3"/>
    <text x="430" y="182" font-family="'Times New Roman', serif" font-size="10.5" fill="#b45309">5823.6 ms (77.8% cold-start)</text>

    <!-- Stage 5: Guard Agent -->
    <text x="-15" y="232" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="end">Guard Validation Gate</text>
    <rect x="0" y="215" width="5" height="24" fill="#10b981" rx="3"/>
    <text x="15" y="232" font-family="'Times New Roman', serif" font-size="10.5" fill="#047857">0.12 ms (&lt;0.01%)</text>
  </g>

  <!-- Note on warm vs cold latency -->
  <rect x="60" y="290" width="660" height="35" rx="5" fill="#eff6ff" stroke="#bfdbfe"/>
  <text x="390" y="312" font-family="'Times New Roman', serif" font-size="11" fill="#1e40af" text-anchor="middle">
    Cold-Start Total: <tspan font-weight="bold">7,482 ms</tspan> | Warm Steady-State Inference Amortized Mean: <tspan font-weight="bold">310.2 ms</tspan> (min: 3.7 ms)
  </text>
</svg>
''')

# 9. Figure 8: Adversarial Audit Performance
save_svg("fig8_adversarial_audit.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="800" height="360">
  <rect width="800" height="360" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="400" y="28" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Adversarial Hallucination Audit Results across 9 Probes
  </text>

  <!-- 3 Family Cards -->
  <g transform="translate(40, 55)">
    <!-- Family 1: Out-of-Corpus -->
    <rect width="220" height="220" rx="8" fill="#ffffff" stroke="#ef4444" stroke-width="2"/>
    <rect width="220" height="38" rx="8" fill="#ef4444"/>
    <text x="110" y="24" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Family 1: Out-of-Corpus (N=3)</text>
    
    <text x="20" y="65" font-family="'Times New Roman', serif" font-size="11" fill="#334155">• Probes: OOC-0, 1, 2</text>
    <text x="20" y="85" font-family="'Times New Roman', serif" font-size="10.5" fill="#475569">Injected ungrounded entity:</text>
    <text x="20" y="100" font-family="'Times New Roman', serif" font-size="10" fill="#dc2626">"hyperlucent galactocele"</text>
    
    <rect x="20" y="125" width="180" height="50" rx="6" fill="#fee2e2"/>
    <text x="110" y="148" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#991b1b" text-anchor="middle">100% Abstention</text>
    <text x="110" y="165" font-family="'Times New Roman', serif" font-size="10" fill="#7f1d1d" text-anchor="middle">Reason: unsupported_descriptor</text>

    <text x="110" y="200" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">&#10004; 0 Hallucinations Emitted</text>
  </g>

  <g transform="translate(290, 55)">
    <!-- Family 2: Conflicting Categories -->
    <rect width="220" height="220" rx="8" fill="#ffffff" stroke="#f59e0b" stroke-width="2"/>
    <rect width="220" height="38" rx="8" fill="#f59e0b"/>
    <text x="110" y="24" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Family 2: Conflicting (N=3)</text>
    
    <text x="20" y="65" font-family="'Times New Roman', serif" font-size="11" fill="#334155">• Probes: CONF-0, 1, 2</text>
    <text x="20" y="85" font-family="'Times New Roman', serif" font-size="10.5" fill="#475569">Injected contradiction:</text>
    <text x="20" y="100" font-family="'Times New Roman', serif" font-size="10" fill="#d97706">BI-RADS 1 with Biopsy</text>
    
    <rect x="20" y="125" width="180" height="50" rx="6" fill="#fef3c7"/>
    <text x="110" y="148" font-family="'Times New Roman', serif" font-size="13" font-weight="bold" fill="#92400e" text-anchor="middle">100% Abstention</text>
    <text x="110" y="165" font-family="'Times New Roman', serif" font-size="10" fill="#78350f" text-anchor="middle">Reason: category_conflict</text>

    <text x="110" y="200" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">&#10004; 0 Hallucinations Emitted</text>
  </g>

  <g transform="translate(540, 55)">
    <!-- Family 3: Distractors -->
    <rect width="220" height="220" rx="8" fill="#ffffff" stroke="#3b82f6" stroke-width="2"/>
    <rect width="220" height="38" rx="8" fill="#3b82f6"/>
    <text x="110" y="24" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Family 3: Distractors (N=3)</text>
    
    <text x="20" y="65" font-family="'Times New Roman', serif" font-size="11" fill="#334155">• Probes: DIST-0, 1, 2</text>
    <text x="20" y="85" font-family="'Times New Roman', serif" font-size="10.5" fill="#475569">Irrelevant evidence chunks</text>
    <text x="20" y="100" font-family="'Times New Roman', serif" font-size="10" fill="#2563eb">injected ahead of target</text>
    
    <rect x="20" y="125" width="180" height="50" rx="6" fill="#eff6ff"/>
    <text x="110" y="145" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">DIST-0: 100% Support</text>
    <text x="110" y="160" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#b45309" text-anchor="middle">DIST-1: 1 Flagged Claim</text>
    <text x="110" y="174" font-family="'Times New Roman', serif" font-size="10" fill="#dc2626" text-anchor="middle">DIST-2: Abstain (low_conf)</text>

    <text x="110" y="200" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">&#10004; Automatic Attribution Catch</text>
  </g>

  <!-- Summary banner -->
  <rect x="40" y="295" width="720" height="42" rx="6" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="400" y="321" font-family="'Times New Roman', serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">
    Overall Adversarial Abstention Rate: <tspan fill="#b45309">77.78% (7/9 cases)</tspan> | Residual Hallucination Rate: <tspan fill="#059669">16.67% (1 claim in 6)</tspan>
  </text>
</svg>
''')

# 10. Figure 9: Web UI Wireframe & Architecture
save_svg("fig9_ui_wireframe.svg", '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 400" width="820" height="400">
  <defs>
    <filter id="winShadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-opacity="0.15"/>
    </filter>
  </defs>
  <rect width="820" height="400" fill="#f8fafc" rx="8" stroke="#cbd5e1" stroke-width="1"/>
  <text x="410" y="26" font-family="'Times New Roman', serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">
    RP5 Web Clinical Interface Architecture (FastAPI + Asynchronous Frontend)
  </text>

  <!-- Window Frame -->
  <g transform="translate(30, 42)" filter="url(#winShadow)">
    <rect width="760" height="330" rx="8" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
    <!-- Window title bar -->
    <rect width="760" height="30" rx="8" fill="#1e293b"/>
    <circle cx="16" cy="15" r="5" fill="#ef4444"/>
    <circle cx="32" cy="15" r="5" fill="#f59e0b"/>
    <circle cx="48" cy="15" r="5" fill="#10b981"/>
    <text x="400" y="20" font-family="'Times New Roman', serif" font-size="11" fill="#cbd5e1" text-anchor="middle">RP5 Breast Imaging Reporting Decision-Support Portal — http://127.0.0.1:8000</text>

    <!-- Left Column: Input Card Panel -->
    <g transform="translate(15, 42)">
      <rect width="270" height="270" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
      <rect width="270" height="28" rx="6" fill="#3b82f6"/>
      <text x="135" y="19" font-family="'Times New Roman', serif" font-size="11.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Finding Card Input (PACS Feed)</text>

      <text x="12" y="48" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#334155">Case ID: DEMO-001 | Modality: MG</text>
      <text x="12" y="66" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#334155">Laterality: Left | Breast Density: B</text>
      
      <rect x="10" y="80" width="250" height="75" rx="4" fill="#ffffff" stroke="#e2e8f0"/>
      <text x="18" y="98" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#1e293b">Lesion 1:</text>
      <text x="18" y="114" font-family="'Times New Roman', serif" font-size="9.5" fill="#475569">• Kind: Mass | Location: Upper outer quadrant</text>
      <text x="18" y="128" font-family="'Times New Roman', serif" font-size="9.5" fill="#475569">• Size: 12.0 mm | Descriptors: circumscribed</text>
      <text x="18" y="142" font-family="'Times New Roman', serif" font-size="9.5" fill="#047857">• Pathology: benign</text>

      <rect x="10" y="165" width="250" height="32" rx="4" fill="#2563eb"/>
      <text x="135" y="185" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">Execute RAG Pipeline</text>

      <!-- Safety Badge -->
      <rect x="10" y="210" width="250" height="45" rx="4" fill="#f0fdf4" stroke="#86efac"/>
      <text x="135" y="228" font-family="'Times New Roman', serif" font-size="10" font-weight="bold" fill="#166534" text-anchor="middle">Safety Guard: ACTIVE</text>
      <text x="135" y="244" font-family="'Times New Roman', serif" font-size="9" fill="#15803d" text-anchor="middle">Reference labels isolated from prompt</text>
    </g>

    <!-- Right Top: Clinician Draft JSON -->
    <g transform="translate(300, 42)">
      <rect width="445" height="135" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
      <rect width="445" height="26" rx="6" fill="#1e293b"/>
      <text x="222" y="18" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">Clinician Structured Output (JSON)</text>
      
      <rect x="10" y="34" width="425" height="92" rx="4" fill="#1e1e1e"/>
      <text x="20" y="52" font-family="monospace" font-size="9.5" fill="#4ec9b0">"view"<tspan fill="#d4d4d4">: </tspan><tspan fill="#ce9178">"MG"</tspan><tspan fill="#d4d4d4">,</tspan></text>
      <text x="20" y="68" font-family="monospace" font-size="9.5" fill="#4ec9b0">"findings"<tspan fill="#d4d4d4">: </tspan><tspan fill="#ce9178">"mass at upper outer quadrant, 12.0 mm."</tspan><tspan fill="#d4d4d4">,</tspan></text>
      <text x="20" y="84" font-family="monospace" font-size="9.5" fill="#4ec9b0">"final_assessment"<tspan fill="#d4d4d4">: </tspan><tspan fill="#b5cea8">2</tspan><tspan fill="#d4d4d4">, </tspan><tspan fill="#6a9955">// BI-RADS 2 (Benign)</tspan></text>
      <text x="20" y="100" font-family="monospace" font-size="9.5" fill="#4ec9b0">"recommendation"<tspan fill="#d4d4d4">: </tspan><tspan fill="#ce9178">"Routine screening."</tspan></text>
      <text x="20" y="116" font-family="monospace" font-size="9" fill="#569cd6">Status: VALIDATED | Citation Coverage: 100% | Support: 1.00</text>
    </g>

    <!-- Right Bottom: Patient Plain Language -->
    <g transform="translate(300, 185)">
      <rect width="445" height="127" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>
      <rect width="445" height="26" rx="6" fill="#0d9488"/>
      <text x="222" y="18" font-family="'Times New Roman', serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">Patient Layperson Summary (FK Readability: Grade 6.89)</text>

      <rect x="10" y="34" width="425" height="84" rx="4" fill="#ffffff" stroke="#e2e8f0"/>
      <text x="20" y="52" font-family="'Times New Roman', serif" font-size="10.5" fill="#0f172a">"Your mammogram showed a round, well-defined spot (circumscribed mass) in your left breast,</text>
      <text x="20" y="68" font-family="'Times New Roman', serif" font-size="10.5" fill="#0f172a">measuring about 12 millimeters. The findings look completely normal and benign (BI-RADS 2).</text>
      <text x="20" y="84" font-family="'Times New Roman', serif" font-size="10.5" fill="#0f172a">No further special testing or biopsy is needed at this time. Please continue your routine screening."</text>
      
      <rect x="15" y="94" width="415" height="20" rx="3" fill="#f0fdf4"/>
      <text x="222" y="108" font-family="'Times New Roman', serif" font-size="9.5" font-weight="bold" fill="#166534" text-anchor="middle">Verified Readability: 6.89 &#8804; Grade 8.0 Target Ceiling | Citations Verified: 2/2 chunks</text>
    </g>
  </g>
</svg>
''')

print("All publication-grade SVG figures generated successfully in output/figures/.")
