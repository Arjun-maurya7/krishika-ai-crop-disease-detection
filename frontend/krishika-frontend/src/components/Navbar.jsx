import React from 'react';

export default function Navbar({ activeTab, setActiveTab, farmer, onOpenAuth, onLogout }) {
  const tabs = [
    { id: 'diagnose', label: 'AI Diagnosis', icon: '🩺' },
    { id: 'library', label: 'Crop Care Library', icon: '🌱' },
    { id: 'history', label: 'Scan History', icon: '📋' },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(11, 16, 20, 0.88)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-subtle)',
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setActiveTab('diagnose')}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
              <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
            </svg>
          </div>
          <div>
            <div style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em', color: '#fff' }}>
              Krishika <span style={{ color: 'var(--emerald-400)' }}>AI</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
              Plant Health & Crop Diagnostics
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(255, 255, 255, 0.03)',
          padding: '4px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '7px 16px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.86rem',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  background: isActive ? 'var(--bg-elevated)' : 'transparent',
                  border: isActive ? '1px solid rgba(255,255,255,0.1)' : '1px solid transparent',
                  transition: 'all 0.15s ease',
                }}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Farmer Profile / Sign In */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {farmer ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ textAlign: 'right', lineHeight: 1.2 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                  {farmer.full_name || farmer.phone}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--emerald-400)' }}>
                  {farmer.district ? `${farmer.district}, ${farmer.state}` : 'Active Member'}
                </div>
              </div>
              <button
                onClick={onLogout}
                className="btn-secondary btn-sm"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn-primary btn-sm"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
