"""
Update Table of Content, List of Figures, and List of Tables with the exact page numbers.
"""
from pathlib import Path
import re
import subprocess

code = Path("build_report.py").read_text(encoding="utf-8")

# Updated TOC block
new_toc = """  <div style="margin-top: 15pt;">
    <div class="toc-row" style="font-weight: bold;">
      <span>Title</span>
      <span class="toc-dots"></span>
      <span>Page No.</span>
    </div>
    <div class="toc-row"><span>Certificate</span><span class="toc-dots"></span><span>ii</span></div>
    <div class="toc-row"><span>Declaration</span><span class="toc-dots"></span><span>iii</span></div>
    <div class="toc-row"><span>Acknowledgement</span><span class="toc-dots"></span><span>iv</span></div>
    <div class="toc-row"><span>Area of Work</span><span class="toc-dots"></span><span>v</span></div>
    <div class="toc-row"><span>List of Figures</span><span class="toc-dots"></span><span>vii</span></div>
    <div class="toc-row"><span>List of Tables</span><span class="toc-dots"></span><span>viii</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 5pt;"><span>1. Abstract</span><span class="toc-dots"></span><span>1</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>2. Introduction</span><span class="toc-dots"></span><span>2</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.1 Background and Clinical Context</span><span class="toc-dots"></span><span>2</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.2 Motivation: Pitfalls of Generative AI in Radiology</span><span class="toc-dots"></span><span>2</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.3 The RP5 Paradigm and Proposed Contributions</span><span class="toc-dots"></span><span>3</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.4 Scope and Report Organization</span><span class="toc-dots"></span><span>3</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>3. Literature Review</span><span class="toc-dots"></span><span>4</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.1 Evolution of ACR BI-RADS Standards</span><span class="toc-dots"></span><span>4</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.2 Retrieval-Augmented Generation in Healthcare</span><span class="toc-dots"></span><span>5</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.3 Hallucination Detection and Verification Metrics</span><span class="toc-dots"></span><span>5</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.4 Patient Communication and Health Literacy</span><span class="toc-dots"></span><span>6</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.5 Comparative Analysis of Existing Approaches</span><span class="toc-dots"></span><span>6</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>4. Problem Definition and Objectives</span><span class="toc-dots"></span><span>7</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>4.1 Formal Problem Statement</span><span class="toc-dots"></span><span>7</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>4.2 Research and Engineering Objectives</span><span class="toc-dots"></span><span>8</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>5. Proposed Methodology and Work Description</span><span class="toc-dots"></span><span>9</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.1 End-to-End System Pipeline</span><span class="toc-dots"></span><span>9</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.2 Four-Stratum Knowledge Architecture</span><span class="toc-dots"></span><span>10</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.3 Section-Aware Chunking and Dense Vector Indexing</span><span class="toc-dots"></span><span>11</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.4 Dual Generation Heads (Clinician &amp; Patient)</span><span class="toc-dots"></span><span>11</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.5 Attribution Engine &amp; Clinical Conflict Policy</span><span class="toc-dots"></span><span>12</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.6 Guard Agent &amp; Safe Abstention Mechanism</span><span class="toc-dots"></span><span>13</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>6. Proposed Algorithms</span><span class="toc-dots"></span><span>14</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>6.1 End-to-End Generation &amp; Guard Algorithm</span><span class="toc-dots"></span><span>14</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>6.2 Multi-Factor Claim Attribution Algorithm</span><span class="toc-dots"></span><span>15</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>7. Proposed Flowchart / Block Diagram / DFD</span><span class="toc-dots"></span><span>16</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>7.1 System Flowcharts and Decision Logic</span><span class="toc-dots"></span><span>16</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>7.2 Data Flow Diagrams (Level 0 and Level 1)</span><span class="toc-dots"></span><span>17</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>8. Implementation (Tools and Technology Used)</span><span class="toc-dots"></span><span>18</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>8.1 Development Stack and Libraries</span><span class="toc-dots"></span><span>18</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>8.2 Core Module Implementations</span><span class="toc-dots"></span><span>19</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>8.3 RESTful API &amp; Interactive Web UI</span><span class="toc-dots"></span><span>20</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>9. Result Discussion and Analysis</span><span class="toc-dots"></span><span>21</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>9.1 Primary Evaluation &amp; BI-RADS Agreement</span><span class="toc-dots"></span><span>21</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>9.2 Multi-Run Consistency &amp; Temperature Sensitivity</span><span class="toc-dots"></span><span>22</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>9.3 Adversarial Hallucination Audit Findings</span><span class="toc-dots"></span><span>23</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>9.4 Stage-by-Stage Latency Analysis</span><span class="toc-dots"></span><span>24</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>10. Conclusion and Future Scope</span><span class="toc-dots"></span><span>25</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>11. References (IEEE Format)</span><span class="toc-dots"></span><span>26</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>12. List of Publications</span><span class="toc-dots"></span><span>28</span></div>
    <div class="toc-row" style="font-weight: bold; margin-top: 4pt;"><span>13. Plagiarism Compliance Report</span><span class="toc-dots"></span><span>29</span></div>
  </div>"""

# Find old TOC and replace
old_toc_pattern = re.compile(r'  <div style="margin-top: 15pt;">\s*<div class="toc-row" style="font-weight: bold;">.*?<span>13\. Plagiarism Compliance Report</span><span class="toc-dots"></span><span>\d+</span>\s*</div>\s*</div>', re.DOTALL)
code = old_toc_pattern.sub(new_toc, code)

# Updated List of Figures block
new_lof = """  <div style="margin-top: 20pt;">
    <div class="toc-row" style="font-weight: bold;">
      <span>Fig. No.</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Description</span>
      <span class="toc-dots"></span>
      <span>Page No.</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 1</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">End-to-End RP5 System Architecture</span>
      <span class="toc-dots"></span>
      <span>9</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 2</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Four-Stratum Knowledge Ingestion and Chunking Framework</span>
      <span class="toc-dots"></span>
      <span>10</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 3</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Multi-Tier Attribution Alignment and Contradiction Resolution Logic</span>
      <span class="toc-dots"></span>
      <span>12</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 4</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Guard Agent Multi-Gate Decision Tree and Abstention Policy</span>
      <span class="toc-dots"></span>
      <span>16</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 5</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Data Flow Diagrams: Level 0 (Context) and Level 1 (Decomposition)</span>
      <span class="toc-dots"></span>
      <span>17</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 6</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Primary Evaluation Benchmarks on Non-Abstained Test Vignettes</span>
      <span class="toc-dots"></span>
      <span>21</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 7</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Component Latency Breakdown: Cold-Start vs Steady-State Execution</span>
      <span class="toc-dots"></span>
      <span>24</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 8</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Adversarial Hallucination Audit Results across 9 Clinical Probes</span>
      <span class="toc-dots"></span>
      <span>23</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Figure 9</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">RP5 Interactive Web Application UI and Clinical Workflow Wireframe</span>
      <span class="toc-dots"></span>
      <span>20</span>
    </div>
  </div>"""

old_lof_pattern = re.compile(r'  <div style="margin-top: 20pt;">\s*<div class="toc-row" style="font-weight: bold;">\s*<span>Fig\. No\.</span>.*?Figure 9</span>.*?<span>\d+</span>\s*</div>\s*</div>', re.DOTALL)
code = old_lof_pattern.sub(new_lof, code)

# Updated List of Tables block
new_lot = """  <div style="margin-top: 20pt;">
    <div class="toc-row" style="font-weight: bold;">
      <span>Table No.</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Description</span>
      <span class="toc-dots"></span>
      <span>Page No.</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 1</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">ACR BI-RADS Assessment Categories and Clinical Action Protocols</span>
      <span class="toc-dots"></span>
      <span>4</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 2</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Comparative Analysis of Existing Clinical NLP/RAG Systems vs RP5</span>
      <span class="toc-dots"></span>
      <span>6</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 3</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Four-Stratum Knowledge Ingestion Specifications &amp; Chunk Counts</span>
      <span class="toc-dots"></span>
      <span>10</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 4</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">BI-RADS Category to Clinical Recommendation Harmony Matrix</span>
      <span class="toc-dots"></span>
      <span>13</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 5</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Core Software Tools, Libraries, and Execution Environment Specifications</span>
      <span class="toc-dots"></span>
      <span>18</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 6</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Case-by-Case Primary Evaluation Metrics (<tspan font-family="monospace">results/evaluation.json</tspan>)</span>
      <span class="toc-dots"></span>
      <span>21</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 7</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Multi-Run Consistency and Temperature Sensitivity Results (N=15 Runs)</span>
      <span class="toc-dots"></span>
      <span>22</span>
    </div>
    <div class="toc-row">
      <span style="font-weight: bold;">Table 8</span>
      <span style="width: 75%; text-align: left; margin-left: 15px;">Adversarial Probe Audit Family Analysis (<tspan font-family="monospace">results/audit.json</tspan>)</span>
      <span class="toc-dots"></span>
      <span>23</span>
    </div>
  </div>"""

old_lot_pattern = re.compile(r'  <div style="margin-top: 20pt;">\s*<div class="toc-row" style="font-weight: bold;">\s*<span>Table No\.</span>.*?Table 8</span>.*?<span>\d+</span>\s*</div>\s*</div>', re.DOTALL)
code = old_lot_pattern.sub(new_lot, code)

Path("build_report.py").write_text(code, encoding="utf-8")
print("Updated build_report.py with synchronized page numbers.")

subprocess.run(["python", "build_report.py"], check=True)
print("Recompiled synchronized PDF.")
