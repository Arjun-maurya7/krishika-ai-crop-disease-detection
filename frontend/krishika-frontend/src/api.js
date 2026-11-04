// api.js — Krishika AI Client Layer
const API_BASE = (
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? 'https://krishika-ai-api.onrender.com/api' : '/api')
).replace(/\/+$/, '');

function extractErrorDetail(data, fallback = 'Request failed') {
  if (!data) return fallback;
  const detail = data.detail;
  if (!detail) return data.message || fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(item => {
      if (typeof item === 'string') return item;
      const field = item.loc ? item.loc.filter(l => l !== 'body').join('.') : '';
      return field ? (field + ": " + item.msg) : (item.msg || JSON.stringify(item));
    }).join('; ');
  }
  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  return String(detail);
}

function getAuthHeader() {
  const token = localStorage.getItem('krishika_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // ── Authentication ──
  async register(formData) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(extractErrorDetail(err, 'Registration failed'));
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('krishika_token', data.access_token);
      localStorage.setItem('krishika_farmer', JSON.stringify(data.farmer));
    }
    return data;
  },

  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Invalid email or password' }));
      throw new Error(extractErrorDetail(err, 'Invalid email or password'));
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('krishika_token', data.access_token);
      localStorage.setItem('krishika_farmer', JSON.stringify(data.farmer));
    }
    return data;
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() },
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      throw new Error(extractErrorDetail(data, 'Not authenticated'));
    }
    if (!data?.farmer_id) throw new Error('The API returned an invalid farmer session.');
    return data;
  },

  logout() {
    localStorage.removeItem('krishika_token');
    localStorage.removeItem('krishika_farmer');
  },

  // ── Plant Health & Disease Diagnosis ──
  async detect(file, crop) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('crop', crop);

    const res = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData,
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = data?.detail;
      throw new Error(
        typeof detail === 'string' ? detail : `Detection failed (${res.status})`
      );
    }
    if (!data || typeof data !== 'object' || !data.predicted_disease || !data.crop_name) {
      throw new Error('The API returned an invalid diagnosis response. Check the backend URL and deployment.');
    }

    return {
      ...data,
      id: data.detection_id,
      crop: data.crop_name,
      disease: data.predicted_disease,
      ...(data.diagnosis || {}),
    };
  },

  // ── Diagnosis History ──
  async getHistory(page = 1, limit = 12, crop = null, severity = null) {
    const params = new URLSearchParams({ page, limit });
    if (crop) params.append('crop', crop);
    if (severity) {
      const s = severity.toLowerCase();
      params.append('severity', s === 'low' ? 'healthy' : s);
    }

    const res = await fetch(`${API_BASE}/history?${params.toString()}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load history');
    const data = await res.json();
    const rawItems = Array.isArray(data?.items) ? data.items : [];
    const items = rawItems.map((item) => ({
      ...item,
      id: item.id || item.detection_id,
      crop: item.crop || item.crop_name,
      disease: item.disease || item.predicted_disease,
      created_at: item.created_at || item.detected_at,
      remedy: item.remedy || item.diagnosis?.remedy || '',
      diagnosis: item.diagnosis || {
        severity: item.severity,
        remedy: item.remedy || '',
      },
    }));
    return { ...data, items };
  },

  async deleteHistory(detectionId) {
    const res = await fetch(`${API_BASE}/history/${detectionId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to delete diagnosis');
    if (res.status === 204) return true;
    return res.json().catch(() => ({}));
  },

  // ── Crop Knowledge Base & Disease Directory ──
  async getCrops() {
    const res = await fetch(`${API_BASE}/crops`);
    if (!res.ok) throw new Error('Failed to load crop catalog');
    const data = await res.json();
    return Array.isArray(data) ? data : (data.crops || []);
  },

  async getCropDiseases(cropName) {
    const res = await fetch(`${API_BASE}/crops/${encodeURIComponent(cropName)}/diseases`);
    if (!res.ok) throw new Error(`Failed to load details for ${cropName}`);
    const data = await res.json();
    return data.disease_details || data.diseases || [];
  },

  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return await res.json();
    } catch {
      return { status: 'offline', version: '2.0.0', ml_ready: false };
    }
  },
};
