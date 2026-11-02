import React, { useState } from 'react';
import { api } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('Ramesh Patel');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Nashik');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        const payload = {
          name: fullName,
          email,
          password,
          location_state: state,
          location_district: district,
        };
        const res = await api.register(payload);
        const farmer = await api.getMe();
        if (farmer.farmer_id !== res.farmer?.farmer_id) {
          throw new Error('The new account session could not be verified.');
        }
        onAuthSuccess(farmer);
        onClose();
      } else {
        const res = await api.login(email, password);
        const farmer = await api.getMe();
        if (farmer.farmer_id !== res.farmer?.farmer_id) {
          throw new Error('The account session could not be verified.');
        }
        onAuthSuccess(farmer);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    setError(null);
    setLoading(true);
    try {
      const guestEmail = `guest-${crypto.randomUUID()}@guest.krishika.ai`;
      const guestPassword = `${crypto.randomUUID()}${crypto.randomUUID()}`;
      const res = await api.register({
        name: 'Guest Farmer',
        email: guestEmail,
        password: guestPassword,
        location_state: 'Maharashtra',
        location_district: 'Nashik',
      });
      const farmer = await api.getMe();
      if (farmer.farmer_id !== res.farmer?.farmer_id) {
        throw new Error('The guest session could not be verified.');
      }
      onAuthSuccess(farmer);
      onClose();
    } catch (err) {
      setError(err.message || 'Could not create a guest session.');
    } finally {
      setLoading(false);
    }
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
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
            disabled={loading}
            className="btn-secondary btn-sm"
            style={{ fontSize: '0.82rem' }}
          >
            {loading ? 'Creating Guest Session...' : 'Quick 1-Click Guest Access'}
          </button>
        </div>
      </div>
    </div>
  );
}
