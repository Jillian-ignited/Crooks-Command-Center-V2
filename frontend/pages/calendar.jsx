// frontend/pages/calendar.jsx
import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

const Calendar = () => {
  const [calendarData, setCalendarData] = useState(null);
  const [selectedDays, setSelectedDays] = useState(7);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const timeRanges = [
    { label: '7d', value: 7, description: 'Detailed daily execution' },
    { label: '30d', value: 30, description: 'Weekly themes & campaigns' },
    { label: '60d', value: 60, description: 'Major campaign planning' },
    { label: 'Qtr', value: 90, description: 'Strategic quarterly view' }
  ];

  const fetchCalendarData = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/calendar/events?days=${selectedDays}`);
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setCalendarData(data);
    } catch (err) {
      setError(`Failed to load calendar: ${err.message}`);
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchCalendarData();
  }, [selectedDays]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      weekday: selectedDays <= 7 ? 'short' : undefined
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      hip_hop_history: '#9333ea',
      hip_hop_legend: '#dc2626',
      contemporary_culture: '#0ea5e9',
      cultural: '#16a34a',
      music: '#f59e0b',
      sports: '#ef4444',
      fashion: '#ec4899',
      sneaker_culture: '#8b5cf6',
      gaming: '#06b6d4',
      anime: '#f97316',
      skate_culture: '#14b8a6',
      holiday: '#10b981',
      retail: '#eab308'
    };
    return colors[category] || '#6b7280';
  };

  const currentRange = timeRanges.find(r => r.value === selectedDays);

  return (
    <main style={{ maxWidth: 1400, margin: '0 auto', padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Content Calendar</h1>
          <p style={{ color: '#666', margin: '0.5rem 0 0 0' }}>{currentRange?.description}</p>
        </div>
        <button onClick={fetchCalendarData} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Refresh
        </button>
      </div>

      {error && (
        <div style={{
          background: '#fee',
          border: '1px solid #f99',
          padding: '1rem',
          borderRadius: 8,
          marginBottom: '1rem',
          color: '#c33'
        }}>
          {error}
        </div>
      )}

      {/* Time Range Selector */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '2rem' }}>
        {timeRanges.map(range => (
          <button
            key={range.value}
            onClick={() => setSelectedDays(range.value)}
            style={{
              padding: '10px 20px',
              borderRadius: 8,
              border: selectedDays === range.value ? '2px solid #000' : '1px solid #ddd',
              background: selectedDays === range.value ? '#000' : '#fff',
              color: selectedDays === range.value ? '#fff' : '#000',
              cursor: 'pointer',
              fontWeight: selectedDays === range.value ? 'bold' : 'normal'
            }}
          >
            {range.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading calendar...</p>
      ) : (
        <>
          {/* 7-Day View: Detailed Daily Posts */}
          {selectedDays <= 7 && calendarData?.detailed_posts?.length > 0 && (
            <section style={{ marginBottom: '2rem' }}>
              <h2>📅 This Week's Content Schedule</h2>
              <div style={{ display: 'grid', gap: '1rem' }}>
                {calendarData.detailed_posts.map((post, i) => (
                  <div key={i} style={{
                    background: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: 12,
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                          {formatDate(post.date)} {post.time && `• ${post.time}`}
                        </div>
                        <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                          {post.platform}
                        </div>
                      </div>
                      <div style={{
                        background: '#f3f4f6',
                        padding: '4px 12px',
                        borderRadius: 6,
                        fontSize: '0.85rem',
                        height: 'fit-content'
                      }}>
                        {post.post_type}
                      </div>
                    </div>
                    
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong>Content:</strong> {post.content}
                    </div>
                    
                    {post.caption && (
                      <div style={{ marginBottom: '0.5rem', color: '#555' }}>
                        <strong>Caption:</strong> "{post.caption}"
                      </div>
                    )}
                    
                    {post.hashtags && (
                      <div style={{ marginBottom: '0.5rem', color: '#0ea5e9' }}>
                        {post.hashtags.join(' ')}
                      </div>
                    )}
                    
                    {post.visual && (
                      <div style={{ fontSize: '0.9rem', color: '#666' }}>
                        <strong>Visual:</strong> {post.visual}
                      </div>
                    )}
                    
                    {post.cta && (
                      <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: '#fef3c7', borderRadius: 6, fontSize: '0.9rem' }}>
                        <strong>CTA:</strong> {post.cta}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Cultural Moments & Campaign Ideas */}
          {calendarData?.cultural_moments?.length > 0 && (
            <section>
              <h2>🎯 Cultural Moments & Campaign Opportunities</h2>
              <p style={{ color: '#666', marginBottom: '1.5rem' }}>
                {selectedDays <= 7 
                  ? 'Immediate opportunities this week'
                  : `${calendarData.cultural_moments.length} strategic moments in the next ${selectedDays} days`
                }
              </p>
              
              <div style={{ display: 'grid', gap: '1rem' }}>
                {calendarData.cultural_moments.map((moment, i) => (
                  <div key={i} style={{
                    background: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: 12,
                    padding: '1.5rem',
                    borderLeft: `4px solid ${getCategoryColor(moment.category)}`
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                          {moment.title}
                        </div>
                        <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                          {formatDate(moment.date)}
                        </div>
                      </div>
                      <div style={{
                        background: getCategoryColor(moment.category),
                        color: '#fff',
                        padding: '4px 12px',
                        borderRadius: 6,
                        fontSize: '0.8rem',
                        textTransform: 'capitalize'
                      }}>
                        {moment.category.replace(/_/g, ' ')}
                      </div>
                    </div>
                    
                    <div style={{
                      background: '#f9fafb',
                      padding: '1rem',
                      borderRadius: 8,
                      marginTop: '1rem'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: '#374151' }}>
                        💡 Campaign Idea:
                      </div>
                      <div style={{ color: '#555' }}>
                        {moment.campaign_idea}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '0.5rem' }}>
                        Content Type: {moment.content_type.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Empty State */}
          {!loading && (!calendarData?.cultural_moments?.length && !calendarData?.detailed_posts?.length) && (
            <div style={{
              padding: '3rem',
              textAlign: 'center',
              background: '#f9fafb',
              borderRadius: 12,
              border: '1px dashed #d1d5db'
            }}>
              <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>
                No events scheduled for this period
              </p>
            </div>
          )}

          {/* Summary Footer */}
          {calendarData && (
            <div style={{
              marginTop: '2rem',
              padding: '1rem',
              background: '#f3f4f6',
              borderRadius: 8,
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              <div>
                Period: {formatDate(calendarData.start_date)} - {formatDate(calendarData.end_date)}
              </div>
              <div>
                Total Events: {calendarData.total_events}
              </div>
            </div>
          )}
        </>
      )}
    </main>
  );
};

export default Calendar;
