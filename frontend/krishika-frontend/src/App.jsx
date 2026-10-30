import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DiagnoseView from './components/DiagnoseView';
import HistoryView from './components/HistoryView';
import EncyclopediaView from './components/EncyclopediaView';
import AuthModal from './components/AuthModal';
import { api } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('diagnose');
  const [farmer, setFarmer] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  useEffect(() => {
    const savedFarmer = localStorage.getItem('krishika_farmer');
    if (savedFarmer) {
      try {
        setFarmer(JSON.parse(savedFarmer));
      } catch {
        // ignore
      }
    }
  }, []);

  const handleLogout = () => {
    api.logout();
    setFarmer(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        farmer={farmer}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      {/* Main Views */}
      <main style={{ flex: 1 }}>
        {activeTab === 'diagnose' && <DiagnoseView />}
        {activeTab === 'library' && <EncyclopediaView />}
        {activeTab === 'history' && <HistoryView />}
      </main>

      {/* Clean Footer */}
      <footer style={{
        marginTop: '60px',
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(8, 12, 14, 0.95)',
        padding: '24px 20px',
        fontSize: '0.82rem',
        color: 'var(--text-muted)',
      }}>
        <div style={{
          maxWidth: '1240px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
        }}>
          <div>
            🌱 <strong>Krishika AI</strong> — Intelligent Plant Health & Crop Disease Diagnosis
          </div>
          <div>
            17 Indian Crops Supported • Certified Treatment Protocols
          </div>
          <div style={{ color: 'var(--emerald-400)' }}>
            &copy; {new Date().getFullYear()} Krishika AI
          </div>
        </div>
      </footer>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(newFarmer) => setFarmer(newFarmer)}
      />
    </div>
  );
}
