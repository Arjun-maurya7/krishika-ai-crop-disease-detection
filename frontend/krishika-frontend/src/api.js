// api.js — Krishika AI Client Layer

const API_BASE = '/api';

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
      throw new Error(err.detail || 'Registration failed');
    }
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('krishika_token', data.access_token);
      localStorage.setItem('krishika_farmer', JSON.stringify(data.farmer));
    }
    return data;
  },

  async login(phone, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Invalid phone or password' }));
      throw new Error(err.detail || 'Invalid phone or password');
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
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  logout() {
    localStorage.removeItem('krishika_token');
    localStorage.removeItem('krishika_farmer');
  },

  // ── Plant Health & Disease Diagnosis ──
  async detect(file, crop) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('crop', crop);

    const res = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Detection failed' }));
      throw new Error(err.detail || 'Detection failed');
    }
    return res.json();
  },

  // ── Diagnosis History ──
  async getHistory(page = 1, limit = 12, crop = null, severity = null) {
    const params = new URLSearchParams({ page, limit });
    if (crop) params.append('crop', crop);
    if (severity) params.append('severity', severity);

    const res = await fetch(`${API_BASE}/history?${params.toString()}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load history');
    return res.json();
  },

  async deleteHistory(detectionId) {
    const res = await fetch(`${API_BASE}/history/${detectionId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to delete diagnosis');
    return res.json();
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
