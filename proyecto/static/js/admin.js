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

// Devices CRUD client
async function fetchDevices() {
  try {
    const res = await fetch('/api/v1/devices');
    const j = await res.json();
    renderDevices(j.devices || []);
  } catch (e) {
    document.getElementById('devices-list').innerText = 'Error cargando dispositivos: ' + e.message;
  }
}

function renderDevices(devices) {
  const el = document.getElementById('devices-list');
  el.innerHTML = '';
  if (devices.length === 0) {
    el.innerText = 'No hay dispositivos registrados.';
    return;
  }
  devices.forEach(d => {
    const row = document.createElement('div');
    row.className = 'feature';
    row.innerHTML = `<div>
        <div style="font-weight:600">${d.hostname} <span style="font-size:12px;color:var(--muted)">(${d.ip_address || '—'})</span></div>
        <div style="font-size:12px;color:var(--muted)">${d.os || ''} • Últ. conexión: ${d.last_seen? d.last_seen.split('T')[0] : '—'}</div>
      </div>`;
    const controls = document.createElement('div');
    const edit = document.createElement('button');
    edit.className = 'btn';
    edit.innerText = 'Editar';
    edit.onclick = () => showDeviceForm(d);
    const del = document.createElement('button');
    del.className = 'btn ghost';
    del.innerText = 'Eliminar';
    del.onclick = async () => {
      if (!confirm('Eliminar dispositivo?')) return;
      await fetch(`/api/v1/devices/${d.id}`, { method: 'DELETE' });
      fetchDevices();
    };
    controls.appendChild(edit);
    controls.appendChild(del);
    row.appendChild(controls);
    el.appendChild(row);
  });
}

function showDeviceForm(d) {
  document.getElementById('device-form').style.display = 'block';
  document.getElementById('device-id').value = d?.id || '';
  document.getElementById('device-hostname').value = d?.hostname || '';
  document.getElementById('device-ip').value = d?.ip_address || '';
  document.getElementById('device-os').value = d?.os || '';
}

function hideDeviceForm() {
  document.getElementById('device-form').style.display = 'none';
  document.getElementById('device-id').value = '';
  document.getElementById('device-hostname').value = '';
  document.getElementById('device-ip').value = '';
  document.getElementById('device-os').value = '';
}

async function saveDevice() {
  const id = document.getElementById('device-id').value;
  const payload = {
    hostname: document.getElementById('device-hostname').value,
    ip_address: document.getElementById('device-ip').value,
    os: document.getElementById('device-os').value,
  };
  try {
    if (id) {
      await fetch(`/api/v1/devices/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    } else {
      await fetch('/api/v1/devices', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    }
    hideDeviceForm();
    fetchDevices();
  } catch (e) {
    alert('Error guardando dispositivo: ' + e.message);
  }
}

// Hook device UI
document.addEventListener('DOMContentLoaded', () => {
  const addBtn = document.getElementById('add-device-btn');
  if (addBtn) addBtn.onclick = () => showDeviceForm({});
  const cancel = document.getElementById('device-cancel');
  if (cancel) cancel.onclick = () => hideDeviceForm();
  const save = document.getElementById('device-save');
  if (save) save.onclick = () => saveDevice();

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

  // Ensure devices load with other data
  fetchDevices();
});