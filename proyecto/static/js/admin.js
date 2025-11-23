// Simple admin UI: carga features y servicios, permite togglear features
async function fetchJSON(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function makeSwitch(enabled){
  const s = document.createElement('div');
  s.className = 'switch' + (enabled ? ' on' : '');
  const knob = document.createElement('div');
  knob.className = 'knob';
  s.appendChild(knob);
  return s;
}

function renderFeatures(features) {
  const el = document.getElementById('features-list');
  el.innerHTML = '';
  for (const [key, info] of Object.entries(features)) {
    if (key === 'admin_console') continue;
    const row = document.createElement('div');
    row.className = 'feature';
    const title = document.createElement('div');
    title.innerHTML = `<div style="font-weight:600">${info.name || key}</div><div style="font-size:12px;color:var(--muted)">${key}</div>`;
    const ctrl = makeSwitch(info.enabled);
    ctrl.onclick = async () => {
      try{
        ctrl.classList.add('disabled');
        await fetchJSON(`/api/v1/features/${encodeURIComponent(key)}`, {
          method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled: !info.enabled})
        });
        info.enabled = !info.enabled;
        if(info.enabled) ctrl.classList.add('on'); else ctrl.classList.remove('on');
        updateSummary();
      }catch(e){ alert('Error: '+e.message) }
      finally{ ctrl.classList.remove('disabled') }
    };
    row.appendChild(title);
    row.appendChild(ctrl);
    el.appendChild(row);
  }
}

async function loadServices() {
  const el = document.getElementById('services-status');
  try {
    const data = await fetchJSON('/api/v1/services/status');
    el.innerHTML = '';
    let up = 0;
    for (const [k, v] of Object.entries(data.services || {})) {
      const d = document.createElement('div');
      d.innerHTML = `<strong>${k}</strong>: <span class="${v ? 'status-ok' : 'status-bad'}">${v ? 'Disponible' : 'No disponible'}</span>`;
      el.appendChild(d);
      if (v) up++;
    }
    document.getElementById('num-services').innerText = up;
  } catch (err) {
    el.innerText = 'Error: ' + err.message;
  }
}

async function loadFeatures(){
  try{
    const data = await fetchJSON('/api/v1/features');
    const f = data.features || {};
    renderFeatures(f);
    let active = Object.values(f).filter(x=>x.enabled).length;
    document.getElementById('num-features').innerText = active;
  }catch(e){
    document.getElementById('features-list').innerText = 'Error: '+e.message;
  }
}

function updateSummary(){
  // quick refresh numbers
  loadFeatures();
  loadServices();
}

// Demo helpers: simulate scan, alerts and export
async function simulateScan() {
  const featuresEl = document.getElementById('features-list');
  const servicesEl = document.getElementById('services-status');
  // Mostrar animación breve
  featuresEl.innerHTML = '<em>Ejecutando análisis... (demo)</em>';
  await new Promise(r => setTimeout(r, 1200));
  // resultados ficticios
  const fake = {
    vulnerabilities: 4,
    critical: 1,
    recommendations: [
      'Actualizar software X (versión obsoleta)',
      'Cambiar contraseñas con baja entropía',
      'Cerrar puerto 3389 en host-demo'
    ],
    score: 72
  };
  // Mostrar en UI
  featuresEl.innerHTML = '';
  fake.recommendations.forEach(r => {
    const d = document.createElement('div');
    d.className = 'feature';
    d.innerHTML = `<div>${r}</div><div class="status-bad">Recomendado</div>`;
    featuresEl.appendChild(d);
  });
  document.getElementById('num-features').innerText = fake.vulnerabilities;
  // actualizar resumen
  document.getElementById('num-services').innerText = document.getElementById('num-services').innerText || '—';
}

async function simulateAlert(seedMsg) {
  const el = document.getElementById('services-status');
  const a = document.createElement('div');
  a.innerHTML = `<strong>ALERTA</strong>: ${seedMsg}`;
  a.style.color = '#ffb86b';
  el.prepend(a);
}

document.addEventListener('DOMContentLoaded', ()=>{
  document.getElementById('refresh').onclick = updateSummary;
  updateSummary();
  setInterval(updateSummary, 30000);

  const scanBtn = document.getElementById('demo-scan');
  if (scanBtn) scanBtn.onclick = () => simulateScan();

  const expBtn = document.getElementById('export-report');
  if (expBtn) expBtn.onclick = () => {
    const report = {
      generated: new Date().toISOString(),
      vulnerabilities: 4,
      summary: ['Demo report — no datos reales']
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'informe-demo.json'; a.click();
    URL.revokeObjectURL(url);
  };
});