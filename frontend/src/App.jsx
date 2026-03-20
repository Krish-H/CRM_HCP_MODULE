import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import axios from 'axios';
import { Mail } from 'lucide-react';
import LogInteractionScreen from './components/LogInteractionScreen';

function App() {
  const [followups, setFollowups] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  
  // Refetch when logs list changes (meaning a new form was autosaved)
  const logs = useSelector((state) => state.interactions?.logs || []);

  const fetchFollowups = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/followups/today');
      setFollowups(res.data.followups || []);
    } catch (error) {
      console.error("Failed to fetch followups", error);
    }
  };

  useEffect(() => {
    fetchFollowups();
  }, [logs.length]);

  return (
    <div className="app-container">
      <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>AI-First CRM</h1>
          <div className="subtitle">HCP Log Module</div>
        </div>
        
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          <div onClick={() => setShowDropdown(!showDropdown)} style={{ position: 'relative' }}>
            <Mail size={26} color="var(--primary-color)" />
            {followups.length > 0 && (
              <span style={{
                position: 'absolute', top: -5, right: -10, 
                backgroundColor: '#ef4444', color: 'white', 
                borderRadius: '50%', padding: '2px 6px', 
                fontSize: '0.75rem', fontWeight: 'bold'
              }}>
                {followups.length}
              </span>
            )}
          </div>
          
          {showDropdown && (
            <div style={{
              position: 'absolute', top: '40px', right: 0, 
              width: '300px', backgroundColor: 'white', 
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)', 
              borderRadius: '8px', padding: '15px', 
              zIndex: 1000, border: '1px solid #e2e8f0'
            }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '1.05rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', color: '#1e293b' }}>
                Today's Follow-ups
              </h3>
              {followups.length === 0 ? (
                <p style={{ margin: 0, fontSize: '0.9rem', color: '#64748b' }}>No follow-ups for today.</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: '300px', overflowY: 'auto' }}>
                  {followups.map(f => (
                    <li key={f.id} style={{ marginBottom: '12px', paddingBottom: '12px', borderBottom: '1px solid #f1f5f9' }}>
                      <strong style={{ color: '#0f172a' }}>{f.doctor}</strong>
                      <p style={{ margin: '5px 0 0 0', fontSize: '0.85rem', color: '#475569', lineHeight: '1.4' }}>{f.notes || 'No notes provided'}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </header>
      <main className="main-content">
        <LogInteractionScreen />
      </main>
    </div>
  );
}

export default App;
