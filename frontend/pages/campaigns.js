import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [calendar, setCalendar] = useState(null);
  const [activeTab, setActiveTab] = useState("calendar"); // calendar, campaigns, create
  const [timeFilter, setTimeFilter] = useState(90); // 7, 30, 60, 90 days
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [timeFilter]);

  async function loadData() {
    try {
      setLoading(true);
      const [campaignsRes, calendarRes] = await Promise.all([
        fetch(`${API_BASE_URL}/campaigns/`).then(r => r.json()).catch(() => ({ campaigns: [] })),
        fetch(`${API_BASE_URL}/campaigns/cultural-calendar?days_ahead=${timeFilter}`).then(r => r.json()).catch(() => null)
      ]);
      
      setCampaigns(campaignsRes.campaigns || []);
      setCalendar(calendarRes);
    } catch (err) {
      console.error("Failed to load campaigns:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading campaigns...</div>
        </div>
      </div>
    );
  }

  // Filter events by category
  const filteredEvents = calendar?.events?.filter(e => 
    categoryFilter === "all" || e.category === categoryFilter
  ) || [];

  // Group events by planning window
  const groupedEvents = {
    immediate: filteredEvents.filter(e => e.planning_window === "immediate"),
    week: filteredEvents.filter(e => e.planning_window === "week"),
    two_weeks: filteredEvents.filter(e => e.planning_window === "two_weeks"),
    month: filteredEvents.filter(e => e.planning_window === "month"),
    future: filteredEvents.filter(e => e.planning_window === "future")
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem", color: "#e9edf2" }}>🎯 Campaigns & Cultural Calendar</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Plan campaigns around authentic street culture moments</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Tabs */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", borderBottom: "1px solid #2a2a2a" }}>
          <button onClick={() => setActiveTab("calendar")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "calendar" ? "#6aa6ff" : "#888", borderBottom: activeTab === "calendar" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📅 Cultural Calendar
          </button>
          <button onClick={() => setActiveTab("campaigns")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "campaigns" ? "#6aa6ff" : "#888", borderBottom: activeTab === "campaigns" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            🎯 Your Campaigns ({campaigns.length})
          </button>
        </div>

        {/* CULTURAL CALENDAR TAB */}
        {activeTab === "calendar" && (
          <>
            {/* Time Filter Buttons */}
            <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
              <div style={{ display: "flex", gap: "0.5rem", background: "#1a1a1a", padding: "0.5rem", borderRadius: "8px" }}>
                <button 
                  onClick={() => setTimeFilter(7)} 
                  style={{ 
                    padding: "0.5rem 1rem", 
                    background: timeFilter === 7 ? "#6aa6ff" : "transparent", 
                    color: timeFilter === 7 ? "#fff" : "#888", 
                    border: "none", 
                    borderRadius: "6px", 
                    cursor: "pointer",
                    fontWeight: timeFilter === 7 ? "600" : "400"
                  }}
                >
                  Next 7 Days
                </button>
                <button 
                  onClick={() => setTimeFilter(30)} 
                  style={{ 
                    padding: "0.5rem 1rem", 
                    background: timeFilter === 30 ? "#6aa6ff" : "transparent", 
                    color: timeFilter === 30 ? "#fff" : "#888", 
                    border: "none", 
                    borderRadius: "6px", 
                    cursor: "pointer",
                    fontWeight: timeFilter === 30 ? "600" : "400"
                  }}
                >
                  Next 30 Days
                </button>
                <button 
                  onClick={() => setTimeFilter(60)} 
                  style={{ 
                    padding: "0.5rem 1rem", 
                    background: timeFilter === 60 ? "#6aa6ff" : "transparent", 
                    color: timeFilter === 60 ? "#fff" : "#888", 
                    border: "none", 
                    borderRadius: "6px", 
                    cursor: "pointer",
                    fontWeight: timeFilter === 60 ? "600" : "400"
                  }}
                >
                  Next 60 Days
                </button>
                <button 
                  onClick={() => setTimeFilter(90)} 
                  style={{ 
                    padding: "0.5rem 1rem", 
                    background: timeFilter === 90 ? "#6aa6ff" : "transparent", 
                    color: timeFilter === 90 ? "#fff" : "#888", 
                    border: "none", 
                    borderRadius: "6px", 
                    cursor: "pointer",
                    fontWeight: timeFilter === 90 ? "600" : "400"
                  }}
                >
                  Next 90 Days
                </button>
              </div>

              {/* Category Filter */}
              <select 
                value={categoryFilter} 
                onChange={(e) => setCategoryFilter(e.target.value)}
                style={{ 
                  padding: "0.5rem 1rem", 
                  background: "#1a1a1a", 
                  color: "#e9edf2", 
                  border: "1px solid #2a2a2a", 
                  borderRadius: "8px",
                  cursor: "pointer"
                }}
              >
                <option value="all">All Categories</option>
                <option value="hip-hop">🎤 Hip-Hop</option>
                <option value="streetwear">👟 Streetwear</option>
                <option value="sports">🏀 Sports</option>
                <option value="culture">🎨 Culture</option>
                <option value="latino-culture">🌮 Latino Culture</option>
                <option value="festival">🎪 Festivals</option>
                <option value="retail">🛍️ Retail</option>
              </select>
            </div>

            {/* Summary Stats */}
            {calendar && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
                <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📅 Total Events</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{filteredEvents.length}</div>
                </div>
                <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #ff6b6b20", borderLeft: "3px solid #ff6b6b" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>🔥 Immediate (0-7d)</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ff6b6b" }}>{groupedEvents.immediate.length}</div>
                </div>
                <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #f59e0b20", borderLeft: "3px solid #f59e0b" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>⚡ This Month (8-30d)</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#f59e0b" }}>{groupedEvents.week.length + groupedEvents.two_weeks.length + groupedEvents.month.length}</div>
                </div>
                <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #4ade8020", borderLeft: "3px solid #4ade80" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📆 Future (30d+)</div>
                  <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80" }}>{groupedEvents.future.length}</div>
                </div>
              </div>
            )}

            {/* Events by Planning Window */}
            {filteredEvents.length === 0 ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📅</div>
                <h3 style={{ marginBottom: "0.5rem", color: "#e9edf2" }}>No Events in This Timeframe</h3>
                <p style={{ color: "#888" }}>Try adjusting your filters or extending the date range</p>
              </div>
            ) : (
              <>
                {/* Immediate Events (0-7 days) */}
                {groupedEvents.immediate.length > 0 && (
                  <div style={{ marginBottom: "2rem" }}>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#ff6b6b" }}>🔥 IMMEDIATE - Act Now (0-7 Days)</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {groupedEvents.immediate.map((event, idx) => (
                        <div key={idx} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", borderLeft: "3px solid #ff6b6b" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                            <div>
                              <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e9edf2", marginBottom: "0.5rem" }}>
                                {event.name}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                                📅 {new Date(event.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888" }}>
                                {event.relevance}
                              </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                              <div style={{ fontSize: "0.85rem", color: "#ff6b6b", background: "#2a1a1a", padding: "4px 12px", borderRadius: "6px", marginBottom: "0.5rem", fontWeight: "600" }}>
                                {event.days_until === 0 ? "TODAY" : `${event.days_until} days`}
                              </div>
                              <div style={{ fontSize: "0.75rem", color: "#666", textTransform: "uppercase" }}>
                                {event.category}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* This Week (8-14 days) */}
                {groupedEvents.week.length > 0 && (
                  <div style={{ marginBottom: "2rem" }}>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#f59e0b" }}>⚡ THIS WEEK - Start Planning (8-14 Days)</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {groupedEvents.week.map((event, idx) => (
                        <div key={idx} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", borderLeft: "3px solid #f59e0b" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                            <div>
                              <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e9edf2", marginBottom: "0.5rem" }}>
                                {event.name}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                                📅 {new Date(event.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888" }}>
                                {event.relevance}
                              </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                              <div style={{ fontSize: "0.85rem", color: "#f59e0b", background: "#2a2310", padding: "4px 12px", borderRadius: "6px", marginBottom: "0.5rem", fontWeight: "600" }}>
                                {event.days_until} days
                              </div>
                              <div style={{ fontSize: "0.75rem", color: "#666", textTransform: "uppercase" }}>
                                {event.category}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Next Two Weeks + Month (15-60 days) */}
                {(groupedEvents.two_weeks.length > 0 || groupedEvents.month.length > 0) && (
                  <div style={{ marginBottom: "2rem" }}>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#6aa6ff" }}>📆 THIS MONTH - Begin Ideation (15-60 Days)</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {[...groupedEvents.two_weeks, ...groupedEvents.month].map((event, idx) => (
                        <div key={idx} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", borderLeft: "3px solid #6aa6ff" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                            <div>
                              <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e9edf2", marginBottom: "0.5rem" }}>
                                {event.name}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                                📅 {new Date(event.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888" }}>
                                {event.relevance}
                              </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                              <div style={{ fontSize: "0.85rem", color: "#6aa6ff", background: "#1a1a2a", padding: "4px 12px", borderRadius: "6px", marginBottom: "0.5rem", fontWeight: "600" }}>
                                {event.days_until} days
                              </div>
                              <div style={{ fontSize: "0.75rem", color: "#666", textTransform: "uppercase" }}>
                                {event.category}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Future Events (60+ days) */}
                {groupedEvents.future.length > 0 && (
                  <div>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#4ade80" }}>🌱 FUTURE - Long-Term Planning (60+ Days)</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {groupedEvents.future.map((event, idx) => (
                        <div key={idx} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", borderLeft: "3px solid #4ade80" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                            <div>
                              <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e9edf2", marginBottom: "0.5rem" }}>
                                {event.name}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                                📅 {new Date(event.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                              </div>
                              <div style={{ fontSize: "0.9rem", color: "#888" }}>
                                {event.relevance}
                              </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                              <div style={{ fontSize: "0.85rem", color: "#4ade80", background: "#1a2a1a", padding: "4px 12px", borderRadius: "6px", marginBottom: "0.5rem", fontWeight: "600" }}>
                                {event.days_until} days
                              </div>
                              <div style={{ fontSize: "0.75rem", color: "#666", textTransform: "uppercase" }}>
                                {event.category}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* YOUR CAMPAIGNS TAB */}
        {activeTab === "campaigns" && (
          <div>
            {campaigns.length === 0 ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎯</div>
                <h3 style={{ marginBottom: "1rem", color: "#e9edf2" }}>No Campaigns Yet</h3>
                <p style={{ color: "#888", marginBottom: "2rem" }}>Create your first campaign based on cultural calendar events</p>
                <button style={{ padding: "12px 24px", background: "#6aa6ff", color: "#fff", border: "none", borderRadius: "8px", fontSize: "1rem", cursor: "pointer", fontWeight: "600" }}>
                  Create Campaign
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gap: "1rem" }}>
                {campaigns.map(campaign => (
                  <div key={campaign.id} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div>
                        <h3 style={{ fontSize: "1.25rem", marginBottom: "0.5rem", color: "#e9edf2" }}>{campaign.name}</h3>
                        <p style={{ color: "#888", marginBottom: "0.5rem" }}>{campaign.description}</p>
                        <div style={{ fontSize: "0.85rem", color: "#666" }}>
                          {campaign.start_date && `Start: ${new Date(campaign.start_date).toLocaleDateString()}`}
                        </div>
                      </div>
                      <div style={{ 
                        padding: "4px 12px", 
                        borderRadius: "6px", 
                        fontSize: "0.85rem", 
                        fontWeight: "600",
                        background: campaign.status === "active" ? "#1a2a1a" : campaign.status === "planning" ? "#2a2310" : "#2a1a1a",
                        color: campaign.status === "active" ? "#4ade80" : campaign.status === "planning" ? "#f59e0b" : "#888"
                      }}>
                        {campaign.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}