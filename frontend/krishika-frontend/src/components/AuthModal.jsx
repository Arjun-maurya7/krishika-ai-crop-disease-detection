import React, { useState } from 'react';
import { api } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  if (!isOpen) return null;

  const [isRegister, setIsRegister] = useState(false);
  const [phone, setPhone] = useState('9876543210');
  const [password, setPassword] = useState('FarmerPass123!');
  const [fullName, setFullName] = useState('Ramesh Patel');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Nashik');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        const payload = {
          phone,
          password,
          full_name: fullName,
          state,
          district,
        };
        const res = await api.register(payload);
        onAuthSuccess(res.farmer);
        onClose();
      } else {
        const res = await api.login(phone, password);
        onAuthSuccess(res.farmer);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = () => {
    const demoFarmer = {
      id: 'demo-farmer-01',
      phone: '9876543210',
      full_name: 'Ramesh Patel',
      state: 'Maharashtra',
      district: 'Nashik',
      crops_grown: ['Tomato', 'Grape', 'Corn'],
    };
    localStorage.setItem('krishika_token', 'demo-jwt-token');
    localStorage.setItem('krishika_farmer', JSON.stringify(demoFarmer));
    onAuthSuccess(demoFarmer);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      background: 'rgba(5, 8, 10, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
    }}>
      <div className="card" style={{
        width: '100%',
        maxWidth: '440px',
        padding: '32px',
        boxShadow: 'var(--shadow-glow)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#fff' }}>
              {isRegister ? 'Create Farmer Account' : 'Welcome Back'}
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Sign in to save and access your plant health records
            </p>
          </div>
          <button onClick={onClose} style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>
            ×
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.25)',
            color: 'var(--rose-400)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.85rem',
            marginBottom: '16px',
          }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {isRegister && (
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-control"
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Mobile Phone
            </label>
            <input
              type="tel"
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="input-control"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-control"
            />
          </div>

          {isRegister && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  State
                </label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="input-control"
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  District
                </label>
                <input
                  type="text"
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="input-control"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', marginTop: '6px' }}
          >
            {loading ? 'Authenticating...' : isRegister ? 'Register' : 'Sign In'}
          </button>
        </form>

        <div style={{
          marginTop: '18px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          textAlign: 'center',
        }}>
          <button
            onClick={() => setIsRegister(!isRegister)}
            style={{ fontSize: '0.85rem', color: 'var(--emerald-400)' }}
          >
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Create one"}
          </button>

          <button
            type="button"
            onClick={handleDemoSignIn}
            className="btn-secondary btn-sm"
            style={{ fontSize: '0.82rem' }}
          >
            Quick 1-Click Guest Access
          </button>
        </div>
      </div>
    </div>
  );
}
