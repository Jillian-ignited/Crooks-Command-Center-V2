// frontend/pages/content.js
import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

export default function Content() {
  const [intelligence, setIntelligence] = useState(null);
  const [brief, setBrief] = useState({
    brand: "Crooks & Castles",
    objective: "",
    audience: "",
    tone: "",
    channels: []
  });
  const [ideaRequest, setIdeaRequest] = useState({
    brand: "Crooks & Castles",
    theme: "",
    count: 5
  });
  const [generatedIdeas, setGeneratedIdeas] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadIntelligence();
  }, []);

  async function loadIntelligence() {
    try {
      const res = await fetch(`${API_BASE}/api/intelligence/summary`);
      const data = await res.json();
      setIntelligence(data);
      
      // Auto-populate theme from trending topics
      if (data.insights?.trending_topics && Array.isArray(data.insights.trending_topics)) {
        const topTopic = data.insights.trending_topics[0];
        setIdeaRequest(prev => ({
          ...prev,
          theme: typeof topTopic === 'string' ? topTopic : topTopic.name || ""
        }));
      }
    } catch (err) {
      console.error('Failed to load intelligence:', err);
    }
  }

  async function generateIdeas(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/content/ideas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ideaRequest)
      });
      const data = await res.json();
      setGeneratedIdeas(data);
    } catch (err) {
      console.error('Failed to generate ideas:', err);
    } finally {
      setLoading(false);
    }
  }

  async function createBrief(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/content/brief`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(brief)
      });
      const data = await res.json();
      alert("Brief created successfully!");
    } catch (err) {
      console.error('Failed to create brief:', err);
      alert("Failed to create brief");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <h1>Content Creation</h1>

      {/* AI Suggestions from Intelligence */}
      {intelligence?.insights?.recommendations && (
        <div style={{ 
          background: "#1a1a1a", 
          padding: "1.5rem", 
          borderRadius: "12px", 
          marginBottom: "2rem",
          border: "2px solid #4ade80"
        }}>
          <h3 style={{ margin: "0 0 1rem 0", color: "#4ade80" }}>💡 AI Content Suggestions</h3>
          <ul style={{ margin: 0, paddingLeft: "1.5rem" }}>
            {Array.isArray(intelligence.insights.recommendations) ? (
              intelligence.insights.recommendations.slice(0, 5).map((rec, i) => (
                <li key={i} style={{ marginBottom: "0.5rem" }}>{rec}</li>
              ))
            ) : (
              <li>{intelligence.insights.recommendations}</li>
            )}
          </ul>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
        {/* Generate Ideas */}
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px" }}>
          <h2 style={{ margin: "0 0 1rem 0" }}>Generate Ideas</h2>
          
          {intelligence?.insights?.trending_topics && (
            <div style={{ 
              background: "#2a2a2a", 
              padding: "0.75rem", 
              borderRadius: "8px", 
              marginBottom: "1rem",
              fontSize: "0.9rem"
            }}>
              <strong>Trending now:</strong> {" "}
              {Array.isArray(intelligence.insights.trending_topics) ? (
                intelligence.insights.trending_topics.slice(0, 3).map((t, i) => 
                  typeof t === 'string' ? t : t.name
                ).join(", ")
              ) : intelligence.insights.trending_topics}
            </div>
          )}

          <form onSubmit={generateIdeas} style={{ display: "grid", gap: "1rem" }}>
            <label>
              Brand
              <input 
                value={ideaRequest.brand} 
                onChange={(e) => setIdeaRequest({...ideaRequest, brand: e.target.value})}
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <label>
              Theme {intelligence?.insights?.trending_topics && (
                <span style={{ fontSize: "0.85rem", color: "#4ade80" }}>(auto-filled from AI)</span>
              )}
              <input 
                value={ideaRequest.theme} 
                onChange={(e) => setIdeaRequest({...ideaRequest, theme: e.target.value})}
                placeholder="e.g., streetwear, urban fashion"
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <label>
              Number of Ideas
              <input 
                type="number"
                value={ideaRequest.count} 
                onChange={(e) => setIdeaRequest({...ideaRequest, count: parseInt(e.target.value)})}
                min="1"
                max="10"
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <button type="submit" disabled={loading} style={{ padding: "10px", cursor: "pointer" }}>
              {loading ? "Generating..." : "Generate Ideas"}
            </button>
          </form>

          {generatedIdeas && (
            <div style={{ marginTop: "1.5rem" }}>
              <h3>Generated Ideas</h3>
              <div style={{ display: "grid", gap: "1rem" }}>
                {generatedIdeas.ideas?.map((idea, i) => (
                  <div key={i} style={{ background: "#2a2a2a", padding: "1rem", borderRadius: "8px" }}>
                    <strong>{idea.title}</strong>
                    <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.9rem", color: "#aaa" }}>
                      {idea.description}
                    </p>
                    <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}>
                      Channels: {idea.channels?.join(", ")}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Create Brief */}
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px" }}>
          <h2 style={{ margin: "0 0 1rem 0" }}>Create Brief</h2>
          
          <form onSubmit={createBrief} style={{ display: "grid", gap: "1rem" }}>
            <label>
              Brand
              <input 
                value={brief.brand} 
                onChange={(e) => setBrief({...brief, brand: e.target.value})}
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <label>
              Objective
              <textarea 
                value={brief.objective} 
                onChange={(e) => setBrief({...brief, objective: e.target.value})}
                rows={3}
                placeholder="What do you want to achieve?"
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <label>
              Target Audience
              <input 
                value={brief.audience} 
                onChange={(e) => setBrief({...brief, audience: e.target.value})}
                placeholder="e.g., 18-34 urban fashion enthusiasts"
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              />
            </label>
            
            <label>
              Tone
              <select 
                value={brief.tone} 
                onChange={(e) => setBrief({...brief, tone: e.target.value})}
                style={{ width: "100%", padding: "8px", marginTop: "4px" }}
              >
                <option value="">Select tone...</option>
                <option value="edgy">Edgy</option>
                <option value="authentic">Authentic</option>
                <option value="aspirational">Aspirational</option>
                <option value="playful">Playful</option>
              </select>
            </label>
            
            <button type="submit" disabled={loading} style={{ padding: "10px", cursor: "pointer" }}>
              {loading ? "Creating..." : "Create Brief"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
