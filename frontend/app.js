const output = document.getElementById('output');

const els = {
  backendUrl: document.getElementById('backendUrl'),
  supabaseUrl: document.getElementById('supabaseUrl'),
  supabaseAnonKey: document.getElementById('supabaseAnonKey'),
  email: document.getElementById('email'),
  password: document.getElementById('password'),
  authState: document.getElementById('authState'),
  currentMode: document.getElementById('currentMode'),
  currentBackend: document.getElementById('currentBackend'),
  currentUser: document.getElementById('currentUser'),
  agentInput: document.getElementById('agentInput'),
  agentContext: document.getElementById('agentContext'),
  productName: document.getElementById('productName'),
  market: document.getElementById('market'),
  activeSubstance: document.getElementById('activeSubstance'),
  strength: document.getElementById('strength'),
  dosageForm: document.getElementById('dosageForm'),
  dossierPayload: document.getElementById('dossierPayload'),
  emaFile: document.getElementById('emaFile'),
  versionSourceId: document.getElementById('versionSourceId'),
  versionPayload: document.getElementById('versionPayload'),
  btnLogout: document.getElementById('btnLogout'),
};

const LS_KEYS = {
  backendUrl: 'qualipharma.backendUrl',
  supabaseUrl: 'qualipharma.supabaseUrl',
  supabaseAnonKey: 'qualipharma.supabaseAnonKey'
};

const DEFAULT_BACKEND_URL = (window.QUALIPHARMA_CONFIG && window.QUALIPHARMA_CONFIG.apiDefault) || 'http://localhost:8000/api/v1';

let supabaseClient = null;
let accessToken = null;
let currentUserEmail = null;
let authSubscription = null;

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

function setOutput(value) {
  output.textContent = typeof value === 'string' ? value : pretty(value);
}

function setStatus({ authenticated = false, email = 'Guest', mode = 'Local UI' } = {}) {
  els.authState.textContent = authenticated ? 'Autenticado' : 'No autenticado';
  els.currentUser.textContent = authenticated ? email : 'Guest';
  els.currentMode.textContent = authenticated ? `${mode} / Auth` : mode;
  if (els.btnLogout) els.btnLogout.classList.toggle('hidden', !authenticated);
}

function readConfig() {
  els.backendUrl.value = localStorage.getItem(LS_KEYS.backendUrl) || DEFAULT_BACKEND_URL;
  els.supabaseUrl.value = localStorage.getItem(LS_KEYS.supabaseUrl) || '';
  els.supabaseAnonKey.value = localStorage.getItem(LS_KEYS.supabaseAnonKey) || '';
  els.currentBackend.textContent = els.backendUrl.value;
  setStatus({ authenticated: false, email: 'Guest', mode: 'Local UI' });
}

function saveConfig() {
  localStorage.setItem(LS_KEYS.backendUrl, els.backendUrl.value.trim());
  localStorage.setItem(LS_KEYS.supabaseUrl, els.supabaseUrl.value.trim());
  localStorage.setItem(LS_KEYS.supabaseAnonKey, els.supabaseAnonKey.value.trim());
  els.currentBackend.textContent = els.backendUrl.value.trim() || DEFAULT_BACKEND_URL;
  setOutput({ ok: true, message: 'Configuración guardada.' });
  initSupabase().catch((err) => setOutput({ error: err.message }));
}

function getSupabaseClient() {
  const url = els.supabaseUrl.value.trim();
  const key = els.supabaseAnonKey.value.trim();

  if (!url || !key) return null;
  if (!window.supabase || typeof window.supabase.createClient !== 'function') return null;

  return window.supabase.createClient(url, key, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: false,
      flowType: 'pkce',
    },
  });
}

function clearSessionState() {
  accessToken = null;
  currentUserEmail = null;
  setStatus({ authenticated: false, email: 'Guest', mode: 'Local UI' });
}

async function syncSession() {
  if (!supabaseClient) {
    clearSessionState();
    els.authState.textContent = 'Supabase no configurado';
    return;
  }

  const { data, error } = await supabaseClient.auth.getSession();
  if (error) {
    console.error('getSession error:', error);
    clearSessionState();
    return;
  }

  const session = data?.session;
  accessToken = session?.access_token || null;
  currentUserEmail = session?.user?.email || null;

  if (accessToken) {
    setStatus({ authenticated: true, email: currentUserEmail || 'Usuario', mode: 'Supabase' });
  } else {
    clearSessionState();
  }
}

async function initSupabase() {
  if (authSubscription && typeof authSubscription.data?.subscription?.unsubscribe === 'function') {
    try { authSubscription.data.subscription.unsubscribe(); } catch (_) {}
  }

  supabaseClient = getSupabaseClient();
  if (!supabaseClient) {
    clearSessionState();
    els.authState.textContent = 'Supabase no configurado';
    return;
  }

  authSubscription = supabaseClient.auth.onAuthStateChange((_event, session) => {
    accessToken = session?.access_token || null;
    currentUserEmail = session?.user?.email || null;
    if (accessToken) {
      setStatus({ authenticated: true, email: currentUserEmail || 'Usuario', mode: 'Supabase' });
    } else {
      clearSessionState();
    }
  });

  await syncSession();
}

function headers(extra = {}) {
  const h = { 'Content-Type': 'application/json', ...extra };
  if (accessToken) h.Authorization = `Bearer ${accessToken}`;
  return h;
}

async function api(path, options = {}) {
  const base = els.backendUrl.value.trim().replace(/\/$/, '');
  const response = await fetch(`${base}${path}`, {
    ...options,
    headers: headers(options.headers || {}),
  });

  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || data?.error || text || `HTTP ${response.status}`);
  }

  return data;
}

async function login() {
  if (!supabaseClient) {
    throw new Error('Completa Supabase URL y Anon Key primero.');
  }
  const email = els.email.value.trim();
  const password = els.password.value;
  if (!email || !password) throw new Error('Completá email y password.');

  const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
  if (error) throw error;

  accessToken = data?.session?.access_token || null;
  currentUserEmail = data?.user?.email || email;
  if (!accessToken) throw new Error('Supabase no devolvió access_token.');

  setStatus({ authenticated: true, email: currentUserEmail || 'Usuario', mode: 'Supabase' });
  setOutput({ ok: true, message: 'Login correcto', user: currentUserEmail });
}

async function register() {
  if (!supabaseClient) {
    throw new Error('Completa Supabase URL y Anon Key primero.');
  }
  const email = els.email.value.trim();
  const password = els.password.value;
  if (!email || !password) throw new Error('Completá email y password.');

  const { data, error } = await supabaseClient.auth.signUp({
    email,
    password,
  });
  if (error) throw error;

  const session = data?.session;
  if (session?.access_token) {
    accessToken = session.access_token;
    currentUserEmail = session.user?.email || email;
    setStatus({ authenticated: true, email: currentUserEmail || 'Usuario', mode: 'Supabase' });
    setOutput({ ok: true, message: 'Usuario creado y sesión iniciada', user: currentUserEmail });
  } else {
    setOutput({
      ok: true,
      message: 'Usuario creado. Revisa el correo si la confirmación está activa en Supabase.',
      user: email,
    });
  }
}

async function logout() {
  if (supabaseClient) {
    await supabaseClient.auth.signOut();
  }
  clearSessionState();
  setOutput({ ok: true, message: 'Sesión cerrada' });
}

function tryParseJson(value, fallback = null) {
  const txt = (value || '').trim();
  if (!txt) return fallback;
  return JSON.parse(txt);
}

async function handleAgentDecision() {
  const payload = {
    user_input: els.agentInput.value.trim(),
    dossier_context: tryParseJson(els.agentContext.value, {}),
  };
  const data = await api('/agent/decision', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setOutput(data);
}

async function handleCompare() {
  const payload = {
    product_name: els.productName.value.trim() || 'Producto sin nombre',
    market: els.market.value.trim() || 'EU',
    dossier_text: els.agentInput.value.trim() || null,
    dossier_payload: tryParseJson(els.dossierPayload.value, {}),
  };
  const data = await api('/dossiers/compare', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setOutput(data);
}

async function handleCreateDossier() {
  const payload = {
    product_name: els.productName.value.trim(),
    active_substance: els.activeSubstance.value.trim() || null,
    dosage_form: els.dosageForm.value.trim() || null,
    strength: els.strength.value.trim() || null,
    market: els.market.value.trim() || 'EU',
    dossier_mode: 'create',
    notes: null,
    dossier_payload: tryParseJson(els.dossierPayload.value, {}),
  };
  if (!payload.product_name) {
    throw new Error('Completá el nombre del producto.');
  }
  const data = await api('/dossiers/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setOutput(data);
}

async function handleVersion() {
  const dossier_id = els.versionSourceId.value.trim();
  if (!dossier_id) {
    throw new Error('Completá el ID del dossier origen.');
  }
  const payload = tryParseJson(els.versionPayload.value, {});
  const data = await api(`/dossiers/${encodeURIComponent(dossier_id)}/version`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setOutput(data);
}

async function handleReindex() {
  const data = await api('/admin/reindex', {
    method: 'POST',
    body: JSON.stringify({}),
  });
  setOutput(data);
}

async function handleIngestEma() {
  const file = els.emaFile.files?.[0];
  if (!file) {
    throw new Error('Seleccioná un PDF primero.');
  }
  const base = els.backendUrl.value.trim().replace(/\/$/, '');
  const form = new FormData();
  form.append('file', file);

  const hdrs = {};
  if (accessToken) hdrs.Authorization = `Bearer ${accessToken}`;

  const res = await fetch(`${base}/admin/ingest-ema`, {
    method: 'POST',
    headers: hdrs,
    body: form,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }

  if (!res.ok) throw new Error(data?.detail || data?.error || text || `HTTP ${res.status}`);
  setOutput(data);
}

async function testHealth() {
  const base = els.backendUrl.value.trim().replace(/\/$/, '');
  const healthUrl = base.replace(/\/api\/v1$/, '') + '/health';
  const res = await fetch(healthUrl);
  const text = await res.text();
  try {
    setOutput(text ? JSON.parse(text) : {});
  } catch {
    setOutput(text || 'OK');
  }
}

function loadDemo() {
  els.agentInput.value = 'Crear dossier para ibuprofeno 400 mg para mercado EU, incluyendo evaluación de excipientes y packaging.';
  els.agentContext.value = pretty({
    product_name: 'Ibuprofeno Pharma',
    market: 'EU',
    dossier_id: null,
    dossier_mode: 'create',
  });
  els.productName.value = 'Ibuprofeno Pharma';
  els.market.value = 'EU';
  els.activeSubstance.value = 'Ibuprofeno';
  els.strength.value = '400 mg';
  els.dosageForm.value = 'Comprimidos recubiertos';
  els.dossierPayload.value = pretty({
    composition: [{ component: 'Ibuprofeno', type: 'API', strength: '400 mg' }],
    excipients: ['lactose', 'starch'],
    packaging: ['blister PVC/PVDC'],
  });
  els.versionPayload.value = pretty({ updated: true, notes: 'Cambio de excipiente por normativa' });
  setOutput({
    message: 'Demo cargada',
    next_steps: [
      'Crear usuario en Supabase o iniciar sesión',
      'Clasificar acción',
      'Crear dossier',
      'Comparar dossier',
      'Probar ingesta EMA'
    ],
  });
}

async function copyOutput() {
  await navigator.clipboard.writeText(output.textContent);
  setOutput({ ok: true, message: 'JSON copiado al portapapeles.' });
}

function bind(id, handler) {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('click', () => handler().catch((err) => setOutput({ error: err.message })));
}

bind('btnSaveConfig', async () => saveConfig());
bind('btnLogin', login);
bind('btnRegister', register);
bind('btnLogout', logout);
bind('btnDecide', handleAgentDecision);
bind('btnCompare', handleCompare);
bind('btnCreate', handleCreateDossier);
bind('btnVersion', handleVersion);
bind('btnIngestEma', handleIngestEma);
bind('btnReindex', handleReindex);
bind('btnRefresh', async () => initSupabase());
bind('btnTestHealth', testHealth);
bind('btnLoadDemo', async () => loadDemo());
bind('btnClear', async () => setOutput('Listo para comenzar.'));
bind('btnCopy', copyOutput);

document.addEventListener('DOMContentLoaded', async () => {
  readConfig();
  try {
    await initSupabase();
  } catch (err) {
    setOutput({ error: err.message });
  }
});
