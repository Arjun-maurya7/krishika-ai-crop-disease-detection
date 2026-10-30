import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function EncyclopediaView() {
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [diseases, setDiseases] = useState([]);
  const [loadingDiseases, setLoadingDiseases] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCrops();
  }, []);

  const loadCrops = async () => {
    setLoading(true);
    try {
      const data = await api.getCrops();
      const list = Array.isArray(data) ? data : (data.crops || []);
      setCrops(list);
      if (list.length > 0) {
        handleSelectCrop(list[0]);
      }
    } catch (err) {
      console.warn('Failed to load crop catalog, using fallback list:', err);
      const fallback = [
        {
          key: 'Tomato',
          name: 'Tomato',
          description: 'High-value horticultural crop susceptible to foliar blights and bacterial wilts.',
          growing_information: { season: 'Kharif/Rabi', soil_type: 'Well-drained loam', water_needs: 'Moderate', harvest_days: '90-120' },
          supported_diseases: ['Early Blight', 'Late Blight', 'Bacterial Spot', 'Leaf Mold', 'Healthy']
        },
        {
          key: 'Rice',
          name: 'Rice',
          description: 'Primary grain staple requiring high water retention and warm humid weather.',
          growing_information: { season: 'Kharif (Monsoon)', soil_type: 'Clayey loam', water_needs: 'Very High', harvest_days: '120-150' },
          supported_diseases: ['Bacterial Leaf Blight', 'Brown Spot', 'Leaf Blast', 'Healthy']
        },
        {
          key: 'Corn',
          name: 'Corn (Maize)',
          description: 'Widely cultivated cereal grain used for human consumption, livestock feed, and industrial starch.',
          growing_information: { season: 'Kharif/Rabi', soil_type: 'Deep fertile loam', water_needs: 'Moderate', harvest_days: '60-100' },
          supported_diseases: ['Gray Leaf Spot', 'Holcus Leaf Spot', 'Common Rust', 'Healthy']
        },
        {
          key: 'Potato',
          name: 'Potato',
          description: 'Underground tuber crop with high economic return during winter/rabi seasons.',
          growing_information: { season: 'Rabi (Winter)', soil_type: 'Loose sandy loam', water_needs: 'Moderate', harvest_days: '70-120' },
          supported_diseases: ['Early Blight', 'Late Blight', 'Nematode Damage', 'Healthy']
        },
        {
          key: 'Apple',
          name: 'Apple',
          description: 'Premier temperate fruit crop grown predominantly in Kashmir and Himachal Pradesh.',
          growing_information: { season: 'Temperate Spring-Summer', soil_type: 'Well-drained loam', water_needs: 'Moderate', harvest_days: '140-180' },
          supported_diseases: ['Apple Scab', 'Black Spot', 'Brown Spot', 'Healthy']
        }
      ];
      setCrops(fallback);
      handleSelectCrop(fallback[0]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCrop = async (crop) => {
    setSelectedCrop(crop);
    setLoadingDiseases(true);
    try {
      const cropIdentifier = crop.key || crop.name || crop.crop_id;
      const details = await api.getCropDiseases(cropIdentifier);
      setDiseases(Array.isArray(details) ? details : []);
    } catch (err) {
      console.warn('Could not load pathogen details:', err);
      // Fallback
      setDiseases([
        {
          disease_name: `${crop.name} Early Blight`,
          severity: 'high',
          symptoms: ['Dark concentric rings on older leaves', 'Yellowing margins'],
          remedies: 'Apply Mancozeb or Copper Oxychloride 50 WP @ 2.5g/L. Remove lower infected foliage.'
        },
        {
          disease_name: `${crop.name} Leaf Spot`,
          severity: 'medium',
          symptoms: ['Small circular brown lesions', 'Chlorotic halo'],
          remedies: 'Apply Chlorothalonil or Azoxystrobin. Practice field sanitation.'
        }
      ]);
    } finally {
      setLoadingDiseases(false);
    }
  };

  const filteredCrops = crops.filter((c) =>
    (c.name || c.key || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '40px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '8px' }}>
            Crop Care <span style={{ color: 'var(--emerald-400)' }}>Library & Guide</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Explore growing parameters, soil preferences, and known pathogen treatments across 17 crops.
          </p>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search crop by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input-control"
          style={{ width: '260px', padding: '9px 14px', fontSize: '0.88rem' }}
        />
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-secondary)' }}>
          Loading crop catalog...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 340px) 1fr', gap: '28px' }}>
          {/* Left: Crop List */}
          <div className="card" style={{ padding: '20px', maxHeight: '720px', overflowY: 'auto' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '14px', textTransform: 'uppercase' }}>
              Supported Crops ({filteredCrops.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {filteredCrops.map((crop) => {
                const isSelected = (selectedCrop?.key || selectedCrop?.name) === (crop.key || crop.name);
                return (
                  <button
                    key={crop.crop_id || crop.key || crop.name}
                    onClick={() => handleSelectCrop(crop)}
                    style={{
                      padding: '14px 16px',
                      borderRadius: 'var(--radius-md)',
                      textAlign: 'left',
                      background: isSelected ? 'var(--bg-elevated)' : 'transparent',
                      border: isSelected ? '1px solid var(--emerald-500)' : '1px solid transparent',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, color: isSelected ? 'var(--emerald-400)' : '#fff', fontSize: '0.96rem' }}>
                        {crop.name || crop.key}
                      </span>
                      {crop.growing_information?.season && (
                        <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                          {crop.growing_information.season}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      {crop.supported_diseases?.length || crop.disease_count || 'Multiple'} recognized conditions
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Selected Crop & Disease Cards */}
          {selectedCrop ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Crop Profile Overview */}
              <div className="card" style={{ padding: '28px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                  <div>
                    <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff' }}>
                      {selectedCrop.name || selectedCrop.key}
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginTop: '6px' }}>
                      {selectedCrop.description}
                    </p>
                  </div>
                </div>

                {/* 4-Box Agronomic Parameters */}
                {selectedCrop.growing_information && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '14px', marginTop: '20px' }}>
                    <div style={{ background: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Sowing Season</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, marginTop: '4px', color: '#fff' }}>
                        {selectedCrop.growing_information.season || 'Kharif / Rabi'}
                      </div>
                    </div>

                    <div style={{ background: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Optimal Soil</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, marginTop: '4px', color: '#fff' }}>
                        {selectedCrop.growing_information.soil_type || 'Loamy soil'}
                      </div>
                    </div>

                    <div style={{ background: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Water Needs</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, marginTop: '4px', color: '#fff' }}>
                        {selectedCrop.growing_information.water_needs || 'Moderate'}
                      </div>
                    </div>

                    <div style={{ background: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Harvest Duration</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, marginTop: '4px', color: '#fff' }}>
                        {selectedCrop.growing_information.harvest_days || '90-120'} days
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Disease Profiles List */}
              <div className="card" style={{ padding: '28px' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '18px' }}>
                  Diagnosable Conditions for {selectedCrop.name || selectedCrop.key}
                </h3>

                {loadingDiseases ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                    Loading condition profiles...
                  </div>
                ) : diseases.length === 0 ? (
                  <div style={{ color: 'var(--text-secondary)', padding: '20px 0' }}>
                    Select a crop to browse its symptoms and remedies.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {diseases.map((d, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'var(--bg-surface)',
                          padding: '18px',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <div style={{ fontWeight: 700, fontSize: '1rem', color: '#fff' }}>
                            {d.disease_name?.replace(/_/g, ' ')}
                          </div>
                          <span className={`badge ${d.severity?.toLowerCase() === 'high' ? 'badge-danger' : 'badge-warning'}`}>
                            {d.severity ? `${d.severity} Risk` : 'Moderate'}
                          </span>
                        </div>

                        {/* Symptoms */}
                        {d.symptoms && d.symptoms.length > 0 && (
                          <div style={{ fontSize: '0.84rem', color: '#cbd5e1', marginBottom: '8px' }}>
                            <strong style={{ color: 'var(--text-secondary)' }}>Symptoms: </strong>
                            {Array.isArray(d.symptoms) ? d.symptoms.join(', ') : d.symptoms}
                          </div>
                        )}

                        {/* Remedy */}
                        {d.remedies && (
                          <div style={{ fontSize: '0.84rem', color: '#e2e8f0', background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', marginTop: '8px' }}>
                            <strong style={{ color: 'var(--emerald-400)' }}>Action / Remedy: </strong>
                            {d.remedies}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
