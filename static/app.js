async function health() {
  try {
    const r = await fetch('/api/health');
    const x = await r.json();
    document.getElementById('status').textContent = `Backend: ${x.backend} · corpus: ${x.corpus}`;
  } catch (e) {
    document.getElementById('status').textContent = 'Backend unavailable';
  }
}

function descriptors() {
  return [...document.querySelectorAll('.desc')].map(x => x.value.trim()).filter(Boolean);
}

document.getElementById('addDesc').onclick = () => {
  const x = document.createElement('input');
  x.className = 'desc';
  x.placeholder = 'descriptor';
  document.getElementById('descriptors').appendChild(x);
};

document.getElementById('run').onclick = async () => {
  const button = document.getElementById('run');
  button.disabled = true;
  button.textContent = 'Generating…';

  const payload = {
    case_id: document.getElementById('case_id').value,
    modality: document.getElementById('modality').value,
    laterality: document.getElementById('laterality').value,
    breast_density: document.getElementById('density').value || null,
    pathology: document.getElementById('pathology').value || null,
    reason_for_exam: document.getElementById('reason').value,
    lesions: [
      {
        kind: document.getElementById('kind').value,
        location: document.getElementById('location').value,
        size_mm: document.getElementById('size').value ? Number(document.getElementById('size').value) : null,
        descriptors: descriptors(),
      },
    ],
    reference_birads: null,
  };

  const box = document.getElementById('result');
  box.classList.remove('hidden');

  try {
    const r = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const x = await r.json();
    render(x);
  } catch (e) {
    box.innerHTML = `<div class="abstain"><h2>Request failed</h2><p>${escapeHtml(String(e))}</p></div>`;
  }

  button.disabled = false;
  button.textContent = 'Generate grounded draft';
};

function render(x) {
  const box = document.getElementById('result');

  if (x.abstained) {
    const warnHtml = (x.validation_warnings || []).length
      ? `<div class="warn-section"><b>Validation warnings:</b><ul>${x.validation_warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul></div>`
      : '';
    box.innerHTML = `
      <div class="abstain">
        <h2>ABSTAIN</h2>
        <p><b>Reason:</b> ${escapeHtml(x.reason || 'Safety criteria not met')}</p>
        <p><b>Missing / Discrepant information:</b> ${(x.missing_information || []).map(escapeHtml).join('; ')}</p>
        ${warnHtml}
      </div>`;
    return;
  }

  // Handle null / unavailable metrics safely
  const biradsVal = x.clinician_draft && x.clinician_draft.final_assessment != null
    ? x.clinician_draft.final_assessment
    : 'N/A';
  const provenanceLabel = x.assessment_provenance === 'source_explicit'
    ? 'Source Explicit'
    : 'Model Proposed';
  const covDisplay = x.coverage != null ? `${(x.coverage * 100).toFixed(1)}%` : 'N/A';
  const confDisplay = x.confidence != null ? Number(x.confidence).toFixed(3) : 'N/A';
  const fkDisplay = x.patient_fk_grade != null ? Number(x.patient_fk_grade).toFixed(2) : 'N/A';

  // Warnings banner
  const warningsList = x.validation_warnings || [];
  const warningsBanner = warningsList.length
    ? `<div class="warning-banner">
        <strong>Validation Warnings & Review Flags (${warningsList.length})</strong>
        <ul>${warningsList.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
       </div>`
    : '';

  // Clinician review badge
  const reviewBadge = x.requires_clinician_review
    ? `<span class="badge review-badge" title="Clinical decision-support only; requires clinician sign-off">Requires Clinician Review</span>`
    : `<span class="badge ok-badge">Verified</span>`;

  // Attribution entries
  const atts = x.attribution || {};
  const citations = Object.entries(atts).map(([claim, items]) => {
    const candidateRows = (items || []).slice(0, 3).map(z => {
      const statusClass = z.status === 'supported' ? 'badge-supported' : z.status === 'uncertain' ? 'badge-uncertain' : 'badge-unsupported';
      const statusLabel = z.status ? z.status.toUpperCase() : (z.supported ? 'SUPPORTED' : 'UNSUPPORTED');
      const lexStr = z.lexical_score != null ? Number(z.lexical_score).toFixed(3) : 'N/A';
      const semStr = z.semantic_score != null ? Number(z.semantic_score).toFixed(3) : 'N/A';
      const reasonStr = z.decision_reason ? ` · <span class="reason-tag">${escapeHtml(z.decision_reason)}</span>` : '';
      const snippet = z.passage_text ? `<div class="cite-snippet">"${escapeHtml(z.passage_text.slice(0, 140))}…"</div>` : '';

      return `
        <div class="cite-row">
          <div class="cite-meta">
            <b>${escapeHtml(z.passage_id)}</b> [${escapeHtml(z.stratum)}]
            <span class="badge ${statusClass}">${statusLabel}</span>
            <span>Lexical: ${lexStr}</span> · <span>Semantic: ${semStr}</span>
            ${reasonStr}
          </div>
          ${snippet}
        </div>`;
    }).join('');

    return `
      <div class="cite">
        <div class="claim-text"><b>Claim:</b> "${escapeHtml(claim)}"</div>
        <div class="cite-candidates">${candidateRows || '<em>No candidate evidence recorded.</em>'}</div>
      </div>`;
  }).join('');

  // Patient text block
  const patientFailed = x.patient_generation_status === 'failed' || x.patient_fk_grade == null;
  const patientBoxClass = patientFailed ? 'card patient-card patient-failed' : 'card patient-card';
  const patientHeader = patientFailed
    ? `<h3>Patient-facing explanation <span class="badge badge-unsupported">Generation Failed / Unverified</span></h3>`
    : `<h3>Patient-facing explanation <span class="badge badge-supported">Verified</span></h3>`;

  box.innerHTML = `
    ${warningsBanner}
    <div class="metric-row">
      <div class="metric">
        <span>BI-RADS Assessment</span>
        <b>BI-RADS ${escapeHtml(String(biradsVal))}</b>
        <div class="metric-sub">${escapeHtml(provenanceLabel)} · ${reviewBadge}</div>
      </div>
      <div class="metric">
        <span>Citation Coverage</span>
        <b>${covDisplay}</b>
        <div class="metric-sub" title="Fraction of claims grounded by evidence">Claim-support coverage</div>
      </div>
      <div class="metric">
        <span>Model Confidence</span>
        <b>${confDisplay}</b>
        <div class="metric-sub" title="Internal heuristic composite score (not cancer risk)">Internal score (not cancer risk)</div>
      </div>
      <div class="metric">
        <span>Patient FK Readability</span>
        <b>${fkDisplay}</b>
        <div class="metric-sub">${x.patient_fk_grade != null ? 'Grade Level (target ≤ 8.0)' : 'FKGL unavailable'}</div>
      </div>
    </div>
    <div class="result-grid">
      <div>
        <div class="card">
          <h3>Clinician draft</h3>
          <pre>${escapeHtml(JSON.stringify(x.clinician_draft, null, 2))}</pre>
        </div>
        <div class="${patientBoxClass}">
          ${patientHeader}
          <p class="patient-text">${escapeHtml(x.patient_text || 'No explanation available.')}</p>
        </div>
      </div>
      <div>
        <div class="card">
          <h3>Sentence-level attribution & Evidence Trace</h3>
          <p class="section-desc">Traceable evidence source, lexical overlap, semantic similarity, and decision rationale per claim.</p>
          ${citations || '<p>No attribution records.</p>'}
        </div>
        <div class="card">
          <h3>Pipeline Latency Breakdown (ms)</h3>
          <pre>${escapeHtml(JSON.stringify(x.latency_ms, null, 2))}</pre>
        </div>
      </div>
    </div>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));
}

health();
