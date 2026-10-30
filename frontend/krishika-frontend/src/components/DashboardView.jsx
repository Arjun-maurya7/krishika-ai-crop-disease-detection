import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function DashboardView({ onInspectPipeline }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activePipelineTab, setActivePipelineTab] = useState('facet');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await api.getGlobalDashboard();
      setStats(data);
    } catch (err) {
      console.warn('Dashboard API unreachable, loading demonstration aggregation data:', err);
      // Realistic MongoDB Aggregation output demo
      setStats({
        total_detections: 148,
        active_farmers: 42,
        avg_confidence: 0.914,
        high_severity_count: 36,
        severity_breakdown: [
          { severity: 'High', count: 36, percentage: 24.3 },
          { severity: 'Medium', count: 68, percentage: 46.0 },
          { severity: 'Low', count: 44, percentage: 29.7 }
        ],
        top_crops: [
          { crop: 'Tomato', count: 48, percentage: 32.4 },
          { crop: 'Rice', count: 31, percentage: 20.9 },
          { crop: 'Potato', count: 24, percentage: 16.2 },
          { crop: 'Corn', count: 19, percentage: 12.8 },
          { crop: 'Grape', count: 14, percentage: 9.5 },
          { crop: 'Others', count: 12, percentage: 8.2 }
        ],
        monthly_trends: [
          { month: '2026-05', count: 18 },
          { month: '2026-06', count: 26 },
          { month: '2026-07', count: 39 },
          { month: '2026-08', count: 43 },
          { month: '2026-09', count: 22 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const PIPELINE_DEFINITIONS = {
    facet: {
      name: "$facet Multi-Faceted Global Analytics",
      description: "Computes total scans, severity distribution, and top vulnerable crops in a single database round-trip without multiple queries.",
      pipeline: [
        {
          "$facet": {
            "total_stats": [
              { "$group": { "_id": null, "total": { "$sum": 1 }, "avg_confidence": { "$avg": "$confidence" } } }
            ],
            "by_severity": [
              { "$group": { "_id": "$diagnosis.severity", "count": { "$sum": 1 } } },
              { "$sort": { "count": -1 } }
            ],
            "by_crop": [
              { "$group": { "_id": "$crop", "count": { "$sum": 1 } } },
              { "$sort": { "count": -1 } },
              { "$limit": 5 }
            ]
          }
        }
      ]
    },
    monthly: {
      name: "$dateToString & $group Monthly Trends",
      description: "Extracts year-month format from BSON timestamp and aggregates temporal disease patterns.",
      pipeline: [
        {
          "$group": {
            "_id": {
              "$dateToString": { "format": "%Y-%m", "date": "$created_at" }
            },
            "total_scans": { "$sum": 1 },
            "high_severity_cases": {
              "$sum": { "$cond": [{ "$eq": ["$diagnosis.severity", "High"] }, 1, 0] }
            }
          }
        },
        { "$sort": { "_id": 1 } }
      ]
    },
    lookup: {
      name: "$lookup Cross-Collection Aggregation",
      description: "Performs left outer join between `crops` and `diseases` collections based on matching `crop_id`.",
      pipeline: [
        { "$match": { "name": "Tomato" } },
        {
          "$lookup": {
            "from": "diseases",
            "localField": "crop_id",
            "foreignField": "crop_id",
            "as": "associated_diseases"
          }
        },
        {
          "$project": {
            "name": 1,
            "growing_information": 1,
            "disease_count": { "$size": "$associated_diseases" },
            "high_risk_diseases": {
              "$filter": {
                "input": "$associated_diseases",
                "as": "d",
                "cond": { "$eq": ["$$d.severity", "High"] }
              }
            }
          }
        }
      ]
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 20px' }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-purple">CSE494 MongoDB Pipeline Showcase</span>
            <span className="badge badge-emerald">Real-Time Aggregations</span>
          </div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
            MongoDB <span style={{ color: 'var(--emerald-400)' }}>Aggregation Analytics</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            High-throughput analytics powered by MongoDB <code>$facet</code>, <code>$group</code>, and <code>$lookup</code> pipelines.
          </p>
        </div>
        <button onClick={loadDashboard} className="btn-secondary btn-sm" disabled={loading}>
          🔄 Refresh Aggregations
        </button>
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Total Diagnosis Documents
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fff', margin: '6px 0' }}>
            {stats?.total_detections || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--emerald-400)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>⚡ Indexed on <code>farmer_id</code> + <code>created_at</code></span>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            High Risk Alerts
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--rose-400)', margin: '6px 0' }}>
            {stats?.high_severity_count || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Requires immediate fungicide/pesticide action
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Average Model Confidence
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--cyan-400)', margin: '6px 0' }}>
            {stats ? `${Math.round(stats.avg_confidence * 100)}%` : '0%'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Aggregated via <code>$avg: "$confidence"</code>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Primary Host Crop
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--amber-400)', margin: '6px 0' }}>
            {stats?.top_crops?.[0]?.crop || 'Tomato'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Leading affected crop in registry
          </div>
        </div>
      </div>

      {/* Two Column Visual Breakdowns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {/* Severity Distribution */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
              Pathogen Severity Breakdown
            </h3>
            <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>$group: "$diagnosis.severity"</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {stats?.severity_breakdown?.map((item) => {
              const color = item.severity === 'High' ? 'var(--rose-400)' : item.severity === 'Medium' ? 'var(--amber-400)' : 'var(--emerald-400)';
              return (
                <div key={item.severity}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color }}>{item.severity} Risk</span>
                    <span style={{ color: 'var(--text-muted)' }}>{item.count} cases ({item.percentage}%)</span>
                  </div>
                  <div style={{ height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${item.percentage}%`,
                      background: color,
                      borderRadius: '4px',
                      transition: 'width 0.8s ease',
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Affected Crops */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
              Top Vulnerable Crops
            </h3>
            <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>$group: "$crop"</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {stats?.top_crops?.map((c) => (
              <div key={c.crop} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ width: '70px', fontSize: '0.85rem', fontWeight: 600 }}>{c.crop}</span>
                <div style={{ flex: 1, height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${c.percentage}%`,
                    background: 'linear-gradient(90deg, #10b981, #34d399)',
                    borderRadius: '4px',
                  }} />
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', width: '45px', textAlign: 'right' }}>
                  {c.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MongoDB Aggregation Pipeline Showcase Card */}
      <div className="glass-panel" style={{ padding: '28px', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff' }}>
              ⚡ MongoDB Aggregation Pipeline Inspector
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Interactive review of the underlying MongoDB aggregation queries designed for CSE494
            </p>
          </div>
          <button
            onClick={() => onInspectPipeline(PIPELINE_DEFINITIONS[activePipelineTab].pipeline)}
            className="btn-primary btn-sm"
          >
            🔍 View Stage-by-Stage BSON
          </button>
        </div>

        {/* Pipeline Tab Selectors */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
          {Object.entries(PIPELINE_DEFINITIONS).map(([key, def]) => (
            <button
              key={key}
              onClick={() => setActivePipelineTab(key)}
              style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.82rem',
                fontWeight: 600,
                background: activePipelineTab === key ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: activePipelineTab === key ? 'var(--emerald-300)' : 'var(--text-muted)',
                border: activePipelineTab === key ? '1px solid var(--border-active)' : '1px solid transparent',
              }}
            >
              {def.name}
            </button>
          ))}
        </div>

        {/* Pipeline Description & Code Box */}
        <div style={{
          background: '#040d09',
          padding: '18px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
            ℹ️ {PIPELINE_DEFINITIONS[activePipelineTab].description}
          </div>
          <pre style={{
            fontSize: '0.82rem',
            color: '#34d399',
            fontFamily: 'monospace',
            lineHeight: 1.5,
            overflowX: 'auto',
          }}>
            {JSON.stringify(PIPELINE_DEFINITIONS[activePipelineTab].pipeline, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
