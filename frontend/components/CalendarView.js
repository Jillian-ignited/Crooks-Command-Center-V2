import { useState, useEffect } from 'react';

export default function CalendarView() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [timeframe, setTimeframe] = useState(60); // Default to 60 days
  
  // Define API base URL with /api prefix
  const API = process.env.NEXT_PUBLIC_API_BASE || "/api";
  
  useEffect(() => {
    const fetchCalendarData = async () => {
      setLoading(true);
      try {
        // Use API prefix for the fetch call - map timeframe to correct endpoint
        let endpoint;
        if (timeframe === 7) {
          endpoint = `${API}/calendar/tactical7`;
        } else if (timeframe === 30) {
          endpoint = `${API}/calendar/strategic30`;
        } else if (timeframe === 60) {
          endpoint = `${API}/calendar/strategic60`;
        } else {
          endpoint = `${API}/calendar/strategic90`;
        }
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
          throw new Error(`Failed to load calendar data: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        console.error("Calendar data fetch error:", err);
        setError(`Failed to load calendar data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCalendarData();
  }, [timeframe, API]); // Include API in dependencies
  
  const handleTimeframeChange = (days) => {
    setTimeframe(days);
  };
  
  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h2>Campaign Calendar</h2>
        <div className="timeframe-selector">
          <button 
            className={timeframe === 7 ? 'active' : ''} 
            onClick={() => handleTimeframeChange(7)}
          >
            7-Day Tactical
          </button>
          <button 
            className={timeframe === 30 ? 'active' : ''} 
            onClick={() => handleTimeframeChange(30)}
          >
            30-Day Strategic
          </button>
          <button 
            className={timeframe === 60 ? 'active' : ''} 
            onClick={() => handleTimeframeChange(60)}
          >
            60-Day Cultural
          </button>
          <button 
            className={timeframe === 90 ? 'active' : ''} 
            onClick={() => handleTimeframeChange(90)}
          >
            90+ Day Long-term
          </button>
        </div>
      </div>
      
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading calendar data...</p>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => handleTimeframeChange(timeframe)}>Retry</button>
        </div>
      )}
      
      {!loading && !error && data && (
        <div className="calendar-content">
          <h3 className="title">Cultural Calendar (Next {data.range_days} days)</h3>
          {data.events?.length ? (
            <ul className="event-list">
              {data.events.map((e, i) => (
                <li key={i} className="event-item">
                  <div className="event-date">{e.date}</div>
                  <div className="event-details">
                    <div className="event-title">{e.title}</div>
                    <span className="pill">{e.category}</span>
                    {e.opportunity_score && (
                      <span className="opportunity-score">
                        Opportunity: {e.opportunity_score}/10
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="muted">No events in range.</div>
          )}
          
          {data.agency_deliverables && (
            <div className="agency-deliverables">
              <h3>Agency Deliverables</h3>
              <ul className="deliverable-list">
                {data.agency_deliverables.map((d, i) => (
                  <li key={i} className="deliverable-item">
                    <div className="deliverable-title">{d.title}</div>
                    <div className="deliverable-status">
                      <span className={`status-pill ${d.status.toLowerCase()}`}>
                        {d.status}
                      </span>
                      <span className="due-date">Due: {d.due_date}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {data.compliance_metrics && (
            <div className="compliance-dashboard">
              <h3>Compliance Dashboard</h3>
              <div className="metrics-grid">
                {Object.entries(data.compliance_metrics).map(([key, value]) => (
                  <div key={key} className="metric-card">
                    <div className="metric-title">{key.replace(/_/g, ' ')}</div>
                    <div className="metric-value">{value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
