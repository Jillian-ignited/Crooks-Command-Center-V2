import { useEffect, useState } from "react";
import CalendarView from "../components/CalendarView";

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function CalendarPage() {
  const [range, setRange] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const loadCalendarData = async (rangeDays = range) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(`${API}/calendar?range_days=${rangeDays}`);
      
      if (!res.ok) {
        throw new Error(`Failed to load calendar: HTTP ${res.status}`);
      }
      
      const result = await res.json();
      setData(result);
      
      if (result.events && result.events.length > 0) {
        setSuccess(`Loaded ${result.events.length} events for the next ${rangeDays} days`);
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Failed to load calendar:', err);
      setError(`Unable to load calendar data: ${err.message}`);
      
      // Set fallback data for development/testing
      setData({
        range_days: rangeDays,
        events: [
          {
            date: new Date().toISOString().split('T')[0],
            title: "Unable to load events",
            category: "error"
          }
        ],
        week_of: new Date().toISOString().split('T')[0]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRangeChange = (newRange) => {
    const validRange = Math.max(1, Math.min(365, parseInt(newRange) || 30));
    setRange(validRange);
  };

  const handleRefresh = () => {
    loadCalendarData(range);
  };

  useEffect(() => {
    loadCalendarData();
  }, []);

  return (
    <div className="grid">
      {/* Status Messages */}
      {error && (
        <div className="card" style={{ border: '1px solid var(--warn)', background: 'rgba(245, 158, 11, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--warn)', margin: '0 0 8px 0' }}>Connection Issue</h3>
              <div style={{ color: 'var(--warn)' }}>{error}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
                Showing fallback data. Check that the backend server is running.
              </div>
            </div>
            <button 
              className="button" 
              onClick={() => {
                setError(null);
                handleRefresh();
              }}
              style={{ background: 'var(--warn)', minWidth: 'auto', padding: '6px 12px' }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {success && (
        <div className="card" style={{ border: '1px solid var(--ok)', background: 'rgba(52, 211, 153, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--ok)', margin: '0 0 8px 0' }}>Success</h3>
              <div style={{ color: 'var(--ok)' }}>{success}</div>
            </div>
            <button 
              className="button" 
              onClick={() => setSuccess(null)}
              style={{ background: 'var(--ok)', minWidth: 'auto', padding: '6px 12px' }}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Calendar Controls */}
      <div className="card">
        <h3 className="title">Cultural Calendar Settings</h3>
        <div className="row" style={{ alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ minWidth: 150 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14, color: 'var(--muted)' }}>
              Days to Show (1-365)
            </label>
            <input 
              type="number" 
              min="1" 
              max="365" 
              value={range} 
              onChange={(e) => handleRangeChange(e.target.value)}
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
          
          <button 
            className="button" 
            onClick={handleRefresh}
            disabled={loading}
            style={{ padding: '10px 16px' }}
          >
            {loading ? 'Loading...' : 'Load Events'}
          </button>
          
          <div className="muted" style={{ alignSelf: 'center' }}>
            {data ? `Showing ${data.events?.length || 0} events` : 'No data loaded'}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card">
          <h3 className="title">Loading Calendar...</h3>
          <div className="muted">Fetching cultural events and important dates...</div>
        </div>
      )}

      {/* Calendar Display */}
      <CalendarView data={data} />

      {/* Additional Calendar Stats */}
      {data && data.events && data.events.length > 0 && (
        <div className="card">
          <h3 className="title">Event Summary</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 12 }}>
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--brand)' }}>
                {data.events.length}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Total Events</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--ok)' }}>
                {new Set(data.events.map(e => e.category)).size}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Categories</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--warn)' }}>
                {range}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Day Range</div>
            </div>
          </div>
          
          {/* Category Breakdown */}
          <div style={{ marginTop: 16 }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: 14, color: 'var(--muted)' }}>Events by Category</h4>
            <div className="row" style={{ flexWrap: 'wrap', gap: 6 }}>
              {Array.from(new Set(data.events.map(e => e.category))).map(category => (
                <span key={category} className="pill" style={{ 
                  background: 'var(--brand)', 
                  color: 'white',
                  fontSize: 11
                }}>
                  {category} ({data.events.filter(e => e.category === category).length})
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="card">
        <h3 className="title">About Cultural Calendar</h3>
        <div className="muted" style={{ lineHeight: 1.5 }}>
          The cultural calendar tracks important dates, holidays, trends, and events that may impact 
          content strategy and social media planning. Use this data to plan campaigns around 
          relevant cultural moments and seasonal trends.
        </div>
        
        {!data || data.events?.length === 0 ? (
          <div style={{ marginTop: 12, padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
            <div style={{ color: 'var(--warn)', marginBottom: 4 }}>No Events Available</div>
            <div className="muted" style={{ fontSize: 12 }}>
              The calendar system needs to be configured with event data sources. 
              Check with your administrator to enable calendar functionality.
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
