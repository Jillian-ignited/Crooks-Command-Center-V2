import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [culturalMoments, setCulturalMoments] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("campaigns"); // campaigns, calendar, create

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [campaignsRes, calendarRes] = await Promise.all([
        fetch(`${API_BASE_URL}/campaigns/`).then(r => r.json()),
        fetch(`${API_BASE_URL}/campaigns/cultural-calendar?days_ahead=90`).then(r => r.json())
      ]);
      
      setCampaigns(campaignsRes.campaigns || []);
      setCulturalMoments(calendarRes.by_timeframe?.next_30_days || []);
    } catch (err) {
      console.error("Failed to load:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCampaign(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      const response = await fetch(`${API_BASE_URL}/campaigns/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          name: formData.get('name'),
          description: formData.get('description'),
          theme: formData.get('theme'),
          launch_date: formData.get('launch_date'),
          cultural_moment: formData.get('cultural_moment'),
          target_audience: formData.get('target_audience'),
          generate_suggestions: 'true'
        })
      });
      
      if (response.ok) {
        setShowCreateForm(false);
        loadData();
        alert('Campaign created with AI suggestions!');
      }
    } catch (err) {
      alert('Failed to create campaign');
    }
  }

  async function viewCampaign(campaignId) {
    try {
      const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}`);
      const data = await response.json();
      setSelectedCampaign(data);
    } catch (err) {
      console.error("Failed to load campaign:", err);
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

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>🎯 Campaigns</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Plan culturally relevant campaigns with AI-powered content suggestions</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Tabs */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", borderBottom: "1px solid #2a2a2a" }}>
          <button onClick={() => setActiveTab("campaigns")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "campaigns" ? "#6aa6ff" : "#888", borderBottom: activeTab === "campaigns" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📋 My Campaigns ({campaigns.length})
          </button>
          <button onClick={() => setActiveTab("calendar")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "calendar" ? "#6aa6ff" : "#888", borderBottom: activeTab === "calendar" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📅 Cultural Calendar
          </button>
          <button onClick={() => { setActiveTab("create"); setShowCreateForm(true); }} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "create" ? "#6aa6ff" : "#888", borderBottom: activeTab === "create" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            ➕ Create Campaign
          </button>
        </div>

        {/* MY CAMPAIGNS TAB */}
        {activeTab === "campaigns" && !selectedCampaign && (
          <div>
            {campaigns.length === 0 ? (
              <div style={{ textAlign: "center", padding: "4rem 2rem", background: "#1a1a1a", borderRadius: "12px" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎯</div>
                <h2 style={{ marginBottom: "1rem" }}>No campaigns yet</h2>
                <p style={{ color: "#888", marginBottom: "2rem" }}>Create your first campaign to get AI-powered content suggestions</p>
                <button onClick={() => { setActiveTab("create"); setShowCreateForm(true); }} style={{ padding: "12px 24px", background: "#6aa6ff", color: "#fff", border: "none", borderRadius: "6px", fontSize: "1rem", cursor: "pointer" }}>
                  Create First Campaign
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gap: "1rem" }}>
                {campaigns.map(c => (
                  <div key={c.id} onClick={() => viewCampaign(c.id)} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", cursor: "pointer", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.borderColor = "#6aa6ff"} onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div>
                        <h3 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>{c.name}</h3>
                        <p style={{ color: "#888", fontSize: "0.9rem" }}>{c.description}</p>
                      </div>
                      <span style={{ padding: "4px 12px", background: c.status === "active" ? "#1a2a1a" : "#2a2a1a", color: c.status === "active" ? "#4ade80" : "#888", borderRadius: "12px", fontSize: "0.85rem" }}>
                        {c.status}
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: "2rem", fontSize: "0.9rem", color: "#888" }}>
                      {c.theme && <div>🎨 {c.theme}</div>}
                      {c.cultural_moment && <div>📅 {c.cultural_moment}</div>}
                      {c.has_suggestions && <div style={{ color: "#4ade80" }}>✨ AI Suggestions Ready</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* SELECTED CAMPAIGN DETAIL */}
        {activeTab === "campaigns" && selectedCampaign && (
          <div>
            <button onClick={() => setSelectedCampaign(null)} style={{ marginBottom: "1rem", color: "#6aa6ff", background: "none", border: "none", cursor: "pointer", fontSize: "1rem" }}>
              ← Back to campaigns
            </button>
            
            <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>{selectedCampaign.name}</h2>
              <p style={{ color: "#888", marginBottom: "2rem" }}>{selectedCampaign.description}</p>
              
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
                <div>
                  <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Theme</div>
                  <div>{selectedCampaign.theme || "—"}</div>
                </div>
                <div>
                  <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Launch Date</div>
                  <div>{selectedCampaign.launch_date ? new Date(selectedCampaign.launch_date).toLocaleDateString() : "—"}</div>
                </div>
                <div>
                  <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Cultural Moment</div>
                  <div>{selectedCampaign.cultural_moment || "—"}</div>
                </div>
              </div>

              {selectedCampaign.target_audience && (
                <div style={{ marginBottom: "2rem" }}>
                  <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Target Audience</div>
                  <div>{selectedCampaign.target_audience}</div>
                </div>
              )}
            </div>

            {/* AI SUGGESTIONS */}
            {selectedCampaign.content_suggestions && selectedCampaign.content_suggestions.suggestions && (
              <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px" }}>
                <h3 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>🤖 AI Content Suggestions</h3>
                
                {selectedCampaign.content_suggestions.suggestions.map((s, i) => (
                  <div key={i} style={{ background: "#0a0b0d", padding: "1.5rem", borderRadius: "8px", marginBottom: "1rem", border: "1px solid #2a2a2a" }}>
                    <h4 style={{ fontSize: "1.1rem", marginBottom: "0.75rem", color: "#6aa6ff" }}>{i + 1}. {s.title}</h4>
                    <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>{s.description}</p>
                    
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem", fontSize: "0.9rem" }}>
                      <div>
                        <strong style={{ color: "#888" }}>Platform:</strong> {s.platform}
                      </div>
                      <div>
                        <strong style={{ color: "#888" }}>Timing:</strong> {s.timing}
                      </div>
                      <div style={{ gridColumn: "1 / -1" }}>
                        <strong style={{ color: "#888" }}>Why it works:</strong> {s.why_it_works}
                      </div>
                      {s.cultural_connection && (
                        <div style={{ gridColumn: "1 / -1", padding: "0.75rem", background: "#1a2a1a", borderRadius: "6px", borderLeft: "3px solid #4ade80" }}>
                          <strong style={{ color: "#4ade80" }}>Cultural Connection:</strong> {s.cultural_connection}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {selectedCampaign.content_suggestions.timing_strategy && (
                  <div style={{ marginTop: "2rem", padding: "1.5rem", background: "#2a1a1a", borderRadius: "8px", borderLeft: "3px solid #6aa6ff" }}>
                    <strong>⏰ Timing Strategy:</strong>
                    <p style={{ marginTop: "0.5rem", color: "#ccc" }}>{selectedCampaign.content_suggestions.timing_strategy}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* CULTURAL CALENDAR TAB */}
        {activeTab === "calendar" && (
          <div>
            <div style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>📅 Upcoming Cultural Moments</h2>
              <p style={{ color: "#888" }}>Next 30 days of hip hop, urban, and streetwear opportunities</p>
            </div>
            
            <div style={{ display: "grid", gap: "1rem" }}>
              {culturalMoments.map((m, i) => (
                <div key={i} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                    <div>
                      <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>{m.name}</h3>
                      <div style={{ color: "#888", fontSize: "0.9rem" }}>
                        {m.formatted_date} • {m.days_away} days away
                      </div>
                    </div>
                    <span style={{ padding: "4px 12px", background: "#2a1a2a", color: m.days_away <= 7 ? "#ff6b6b" : "#6aa6ff", borderRadius: "12px", fontSize: "0.85rem" }}>
                      {m.planning_window}
                    </span>
                  </div>
                  <p style={{ color: "#ccc", lineHeight: "1.6" }}>{m.opportunity}</p>
                  <div style={{ marginTop: "1rem", display: "inline-block", padding: "4px 12px", background: "#0a0b0d", borderRadius: "6px", fontSize: "0.85rem" }}>
                    {m.category}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CREATE CAMPAIGN TAB */}
        {activeTab === "create" && (
          <div>
            <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", maxWidth: "800px" }}>
              <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Create New Campaign</h2>
              
              <form onSubmit={handleCreateCampaign}>
                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Campaign Name *</label>
                  <input name="name" required placeholder="e.g., Holiday Drop 2025" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem" }} />
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Description *</label>
                  <textarea name="description" required rows={3} placeholder="What's this campaign about?" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem", fontFamily: "inherit" }} />
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Theme</label>
                  <input name="theme" placeholder="e.g., Y2K Holiday Nostalgia" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem" }} />
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Launch Date</label>
                  <input name="launch_date" type="date" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem" }} />
                </div>

                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Cultural Moment</label>
                  <input name="cultural_moment" placeholder="e.g., Holiday Party Season, NBA All-Star Weekend" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem" }} />
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Target Audience *</label>
                  <input name="target_audience" required placeholder="e.g., Gen Z streetwear enthusiasts, 18-30" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontSize: "1rem" }} />
                </div>

                <div style={{ padding: "1rem", background: "#1a2a1a", borderRadius: "6px", marginBottom: "2rem", borderLeft: "3px solid #4ade80" }}>
                  <div style={{ fontSize: "0.9rem", color: "#4ade80", marginBottom: "0.5rem" }}>✨ AI-Powered Suggestions</div>
                  <div style={{ fontSize: "0.85rem", color: "#ccc" }}>When you create this campaign, AI will analyze your intelligence data and generate culturally relevant content suggestions for hip hop & streetwear audiences.</div>
                </div>

                <button type="submit" style={{ width: "100%", padding: "14px", background: "#6aa6ff", color: "#fff", border: "none", borderRadius: "6px", fontSize: "1rem", fontWeight: "600", cursor: "pointer" }}>
                  🚀 Create Campaign with AI Suggestions
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
