// Simple admin UI: carga features y servicios, permite togglear features
async function fetchJSON(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function renderFeatures(features) {
  const el = document.getElementById('features-list');
  el.innerHTML = '';
  for (const [key, info] of Object.entries(features)) {
    // Skip admin_console if present (removed/deprecated)
    if (key === 'admin_console') continue;

    const row = document.createElement('div');
    row.className = 'feature';
    const title = document.createElement('div');
    title.innerText = info.name || key;
    const controls = document.createElement('div');
    const btn = document.createElement('button');
    btn.className = 'toggle';
    btn.innerText = info.enabled ? 'Desactivar' : 'Activar';
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        await fetchJSON(`/api/v1/features/${encodeURIComponent(key)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: !info.enabled })
        });
        info.enabled = !info.enabled;
        btn.innerText = info.enabled ? 'Desactivar' : 'Activar';
      } catch (err) {
        alert('Error actualizando feature: ' + err.message);
      } finally {
        btn.disabled = false;
      }
    };
    controls.appendChild(btn);
    row.appendChild(title);
    row.appendChild(controls);
    el.appendChild(row);
  }
}

async function loadServices() {
  const el = document.getElementById('services-status');
  try {
    const data = await fetchJSON('/api/v1/services/status');
    el.innerHTML = '';
    for (const [k, v] of Object.entries(data.services || {})) {
      const d = document.createElement('div');
      d.innerHTML = `<strong>${k}</strong>: <span class="${v ? 'status-ok' : 'status-bad'}">${v ? 'Disponible' : 'No disponible'}</span>`;
      el.appendChild(d);
    }
  } catch (err) {
    el.innerText = 'Error cargando estado de servicios: ' + err.message;
  }
}

async function loadFeatures() {
  try {
    const data = await fetchJSON('/api/v1/features');
    renderFeatures(data.features || {});
  } catch (err) {
    document.getElementById('features-list').innerText = 'Error cargando features: ' + err.message;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadFeatures();
  loadServices();
  // refrescar cada 30s
  setInterval(() => { loadFeatures(); loadServices(); }, 30000);
});