import React, { useState } from 'react';

export default function MongoInspectorModal({ isOpen, onClose, title, documentData, pipelineData, schemaData }) {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState(documentData ? 'document' : pipelineData ? 'pipeline' : 'schema');

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      background: 'rgba(2, 8, 6, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '780px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid var(--border-glow)',
        boxShadow: 'var(--shadow-glow-lg)',
        overflow: 'hidden',
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '18px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(4, 13, 9, 0.5)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.4rem' }}>🍃</span>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                {title || 'MongoDB Document & Pipeline Inspector'}
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--emerald-400)' }}>
                CSE494 Academic Verification: Live MongoDB BSON / JSON Structure
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              color: 'var(--text-muted)',
              fontSize: '1.5rem',
              lineHeight: 1,
              padding: '4px 8px',
            }}
          >
            ×
          </button>
        </div>

        {/* Tab Selectors */}
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '12px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'rgba(7, 22, 16, 0.4)',
        }}>
          {documentData && (
            <button
              onClick={() => setActiveTab('document')}
              className={activeTab === 'document' ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'}
            >
              📄 Embedded Document (BSON)
            </button>
          )}
          {pipelineData && (
            <button
              onClick={() => setActiveTab('pipeline')}
              className={activeTab === 'pipeline' ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'}
            >
              ⚡ Aggregation Pipeline
            </button>
          )}
          <button
            onClick={() => setActiveTab('schema')}
            className={activeTab === 'schema' ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'}
          >
            🛡️ $jsonSchema Validator
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {activeTab === 'document' && documentData && (
            <div>
              <div style={{
                marginBottom: '10px',
                fontSize: '0.82rem',
                color: 'var(--text-muted)',
                display: 'flex',
                justifyContent: 'space-between',
              }}>
                <span>Collection: <strong style={{ color: 'var(--emerald-300)' }}>detections</strong></span>
                <span>Includes embedded <code style={{ color: 'var(--cyan-400)' }}>diagnosis</code> sub-document</span>
              </div>
              <pre style={{
                background: '#040d09',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: '#34d399',
                fontSize: '0.82rem',
                fontFamily: 'monospace',
                overflowX: 'auto',
                lineHeight: 1.5,
              }}>
                {JSON.stringify(documentData, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === 'pipeline' && pipelineData && (
            <div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                Executed on MongoDB using <strong style={{ color: 'var(--emerald-400)' }}>db.collection.aggregate([ ... ])</strong>:
              </p>
              <pre style={{
                background: '#040d09',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: '#60a5fa',
                fontSize: '0.82rem',
                fontFamily: 'monospace',
                overflowX: 'auto',
                lineHeight: 1.5,
              }}>
                {typeof pipelineData === 'string' ? pipelineData : JSON.stringify(pipelineData, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === 'schema' && (
            <div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                Strict MongoDB collection validation enforced at database level via <strong style={{ color: 'var(--purple-400)' }}>$jsonSchema</strong>:
              </p>
              <pre style={{
                background: '#040d09',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: '#c084fc',
                fontSize: '0.82rem',
                fontFamily: 'monospace',
                overflowX: 'auto',
                lineHeight: 1.5,
              }}>
{JSON.stringify(schemaData || {
  $jsonSchema: {
    bsonType: "object",
    required: ["crop", "disease", "confidence", "created_at"],
    properties: {
      crop: { bsonType: "string", description: "Name of the crop" },
      disease: { bsonType: "string", description: "Predicted disease label" },
      confidence: { bsonType: "double", minimum: 0.0, maximum: 1.0 },
      diagnosis: {
        bsonType: "object",
        required: ["severity", "remedy"],
        properties: {
          severity: { enum: ["Low", "Medium", "High", "Critical"] },
          remedy: { bsonType: "string" },
          cause: { bsonType: "string" },
          preventive_measures: { bsonType: "array" }
        }
      }
    }
  }
}, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'flex-end',
          background: 'rgba(4, 13, 9, 0.5)',
        }}>
          <button onClick={onClose} className="btn-secondary btn-sm">
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
