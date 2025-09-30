import React, { useState, useEffect } from 'react';

const Calendar = () => {
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [selectedDays, setSelectedDays] = useState(7);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const timeRanges = [
    { label: '7d', value: 7 },
    { label: '30d', value: 30 },
    { label: '60d', value: 60 },
    { label: 'Qtr', value: 90 }
  ];

  const fetchCalendarData = async () => {
    setError('');
    setLoading(true);

    try {
      // Fetch calendar status with proper API path
      const statusResponse = await fetch('/api/calendar/status');
      if (!statusResponse.ok) {
        throw new Error(`Status API error: ${statusResponse.status}`);
      }
      const statusData = await statusResponse.json();
      setStatus(statusData);
    } catch (err) {
      setError(prev => (prev ? prev + ' | ' : '') + `Status: ${err.message}`);
    }

    try {
      // Fetch calendar events with proper API path
      const eventsResponse = await fetch(`/api/calendar/events?days=${selectedDays}`);
      if (!eventsResponse.ok) {
        throw new Error(`Events API error: ${eventsResponse.status}`);
      }
      const eventsData = await eventsResponse.json();
      setEvents(Array.isArray(eventsData) ? eventsData : []);
    } catch (err) {
      setError(prev => (prev ? prev + ' | ' : '') + `Events: ${err.message}`);
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchCalendarData();
  }, [selectedDays]);

  const formatDate = (dateString) => {
    return dateString ? new Date(dateString).toLocaleString() : '—';
  };

  const handleTimeRangeChange = (days) => {
    setSelectedDays(days);
  };

  return (
    <main style={{ maxWidth: 1000, margin: '40px auto', padding: 20 }}>
      <h1 style={{ marginBottom: 12 }}>Calendar</h1>
      
      {error && (
        <div style={{
          background: '#fee',
          border: '1px solid #f99',
          padding: 10,
          borderRadius: 8,
          marginBottom: 16,
          color: '#c33'
        }}>
          {error}
        </div>
      )}

      <section style={sectionStyle}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
          <strong>View:</strong>
          {timeRanges.map(range => (
            <button
              key={range.value}
              onClick={() => handleTimeRangeChange(range.value)}
              style={{
                ...buttonStyle,
                ...(selectedDays === range.value ? activeButtonStyle : {})
              }}
            >
              {range.label}
            </button>
          ))}
          <span style={{ marginLeft: 'auto', fontSize: 12, color: '#666' }}>
            {status?.connected ? 'Google connected' : 'Google not connected'}
          </span>
        </div>

        {loading ? (
          <p>Loading…</p>
        ) : events.length ? (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {events.map((event, index) => (
              <li key={index} style={eventItemStyle}>
                <div style={{ width: 160, color: '#555' }}>
                  {formatDate(event.start)} – {formatDate(event.end)}
                </div>
                <div style={{ fontWeight: 600 }}>
                  {event.title || 'Untitled'}
                </div>
                {event.location && (
                  <div style={{ marginLeft: 'auto', color: '#777' }}>
                    {event.location}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p>No events in range.</p>
        )}
      </section>

      <section style={sectionStyle}>
        <h2 style={{ marginTop: 0 }}>Culturally Relevant Drops & Moments</h2>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          <li>Streetwear collab calendar (Tentpole)</li>
          <li>Music festival dates (Audience overlap)</li>
          <li>Sneaker release windows (Traffic spikes)</li>
          <li>Creator content hooks (TikTok trends)</li>
        </ul>
        <p style={{ color: '#666', fontSize: 12, marginTop: 8 }}>
          (We'll enrich this from your ingested datasets once available.)
        </p>
      </section>
    </main>
  );
};

const buttonStyle = {
  border: '1px solid #ddd',
  padding: '6px 10px',
  borderRadius: 999,
  background: '#fff',
  cursor: 'pointer'
};

const activeButtonStyle = {
  borderColor: '#111',
  background: '#111',
  color: '#fff'
};

const sectionStyle = {
  background: '#fff',
  border: '1px solid #eee',
  borderRadius: 12,
  padding: 16,
  marginBottom: 16,
  boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
};

const eventItemStyle = {
  display: 'flex',
  gap: 12,
  alignItems: 'center',
  padding: '10px 0',
  borderBottom: '1px solid #f3f3f3'
};

export default Calendar;
