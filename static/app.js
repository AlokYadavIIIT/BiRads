async function health(){
  try{const r=await fetch('/api/health');const x=await r.json();document.getElementById('status').textContent=`Backend: ${x.backend} · corpus: ${x.corpus}`;}catch(e){document.getElementById('status').textContent='Backend unavailable';}
}
function descriptors(){return [...document.querySelectorAll('.desc')].map(x=>x.value.trim()).filter(Boolean)}
document.getElementById('addDesc').onclick=()=>{const x=document.createElement('input');x.className='desc';x.placeholder='descriptor';document.getElementById('descriptors').appendChild(x)};
document.getElementById('run').onclick=async()=>{
 const button=document.getElementById('run');button.disabled=true;button.textContent='Generating…';
 const payload={case_id:document.getElementById('case_id').value,modality:document.getElementById('modality').value,laterality:document.getElementById('laterality').value,breast_density:document.getElementById('density').value||null,pathology:document.getElementById('pathology').value||null,reason_for_exam:document.getElementById('reason').value,lesions:[{kind:document.getElementById('kind').value,location:document.getElementById('location').value,size_mm:document.getElementById('size').value?Number(document.getElementById('size').value):null,descriptors:descriptors()}],reference_birads:null};
 const box=document.getElementById('result');box.classList.remove('hidden');
 try{const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const x=await r.json();render(x)}catch(e){box.innerHTML=`<div class="abstain"><h2>Request failed</h2><p>${e}</p></div>`}
 button.disabled=false;button.textContent='Generate grounded draft';
};
function render(x){const box=document.getElementById('result');
 if(x.abstained){box.innerHTML=`<div class="abstain"><h2>ABSTAIN</h2><p><b>Reason:</b> ${x.reason}</p><p><b>Missing information:</b> ${(x.missing_information||[]).join('; ')}</p></div>`;return}
 const atts=x.attribution||{};const citations=Object.entries(atts).map(([claim,a])=>`<div class="cite"><b>${claim}</b><div>${(a||[]).slice(0,2).map(z=>`${z.passage_id} · ${z.stratum} · ${z.method} · ${Number(z.score).toFixed(3)} · ${z.supported?'supported':'unsupported'}`).join('<br>')}</div></div>`).join('');
 box.innerHTML=`<div class="metric-row"><div class="metric"><span>BI-RADS</span><b>${x.clinician_draft.final_assessment}</b></div><div class="metric"><span>Coverage</span><b>${(x.coverage*100).toFixed(1)}%</b></div><div class="metric"><span>Confidence</span><b>${x.confidence.toFixed(3)}</b></div><div class="metric"><span>Patient FK</span><b>${x.patient_fk_grade.toFixed(2)}</b></div></div><div class="result-grid"><div><div class="card"><h3>Clinician draft</h3><pre>${escapeHtml(JSON.stringify(x.clinician_draft,null,2))}</pre></div><div class="card"><h3>Patient-facing explanation</h3><p>${escapeHtml(x.patient_text)}</p></div></div><div><div class="card"><h3>Sentence-level attribution</h3>${citations||'<p>No attribution records.</p>'}</div><div class="card"><h3>Latency</h3><pre>${escapeHtml(JSON.stringify(x.latency_ms,null,2))}</pre></div></div></div>`;
}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
health();
