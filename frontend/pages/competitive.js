import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function CompetitivePage() {
  const [dashboard, setDashboard] = useState(null);
  const [brands, setBrands] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedThreat, setSelectedThreat] = useState("all");
  const [competitiveData, setCompetitiveData] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [manualCompetitorName, setManualCompetitorName] = useState("");

  useEffect(() => {
    loadData();
  }, [selectedThreat]);

  async function loadData() {
    try {
      setLoading(true);
      
      const threatParam = selectedThreat !== "all" ? `&threat_level=${selectedThreat}` : "";
      
      const [dashboardRes, brandsRes, dataRes] = await Promise.all([
        fetch(`${API_BASE_URL}/competitive/dashboard?days=30${threatParam}`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE_URL}/competitive/brands`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE_URL}/competitive/data?limit=100`).then(r => r.json()).catch(() => ({ data: [] }))
      ]);
      
      setDashboard(dashboardRes);
      setBrands(brandsRes);
      setCompetitiveData(dataRes.data || []);
    } catch (err) {
      console.error("Failed to load competitive data:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    if (manualCompetitorName.trim()) {
      formData.append('competitor_name', manualCompetitorName.trim());
    }

    try {
      const response = await fetch(`${API_BASE_URL}/competitive/upload`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        alert(`✅ Success!\n${result.message}\nAnalyzed: ${result.records_parsed} posts`);
        setManualCompetitorName("");
        loadData();
        setActiveTab("overview");
      } else {
        alert(`❌ Error: ${result.detail || 'Upload failed'}`);
      }
    } catch (err) {
      alert(`❌ Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  }

  async function deleteIntelEntry(id, competitorName) {
    if (!confirm(`Delete intelligence entry for "${competitorName}"?\n\nThis will permanently remove the entry and associated file.`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/competitive/intel/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert(`✅ Deleted entry for ${competitorName}`);
        loadData();
      } else {
        alert(`❌ Failed to delete: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      alert(`❌ Delete failed: ${err.message}`);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading competitive intelligence...</div>
        </div>
      </div>
    );
  }

  const hasData = dashboard && dashboard.total_data_points > 0;
  
  const aggregateByThreat = {};
  if (dashboard && dashboard.competitors && Array.isArray(dashboard.competitors)) {
    dashboard.competitors.forEach(comp => {
      const threat = comp.threat_level || 'unknown';
      if (!aggregateByThreat[threat]) {
        aggregateByThreat[threat] = {
          total_posts: 0,
          total_engagement: 0,
          brands_count: 0,
          avg_engagement: 0
        };
      }
      aggregateByThreat[threat].total_posts += comp.total_posts || 0;
      aggregateByThreat[threat].total_engagement += (comp.avg_engagement || 0) * (comp.total_posts || 0);
      aggregateByThreat[threat].brands_count += 1;
    });
    
    Object.keys(aggregateByThreat).forEach(threat => {
      const data = aggregateByThreat[threat];
      data.avg_engagement = data.total_posts > 0 ? Math.round(data.total_engagement / data.total_posts) : 0;
    });
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem", color: "#e9edf2" }}>🔍 Competitive Intelligence</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Track competitor activity and engagement across channels</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", borderBottom: "1px solid #2a2a2a" }}>
          <button onClick={() => setActiveTab("overview")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "overview" ? "#6aa6ff" : "#888", borderBottom: activeTab === "overview" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📊 Overview
          </button>
          <button onClick={() => setActiveTab("brands")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "brands" ? "#6aa6ff" : "#888", borderBottom: activeTab === "brands" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            🏢 Brands
          </button>
          <button onClick={() => setActiveTab("comparison")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "comparison" ? "#6aa6ff" : "#888", borderBottom: activeTab === "comparison" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            ⚔️ Crooks vs Competitors
          </button>
          <button onClick={() => setActiveTab("upload")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "upload" ? "#6aa6ff" : "#888", borderBottom: activeTab === "upload" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📤 Upload Data
          </button>
        </div>

        {activeTab === "overview" && (
          <>
            {!hasData ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🔍</div>
                <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#e9edf2" }}>No Competitive Data Yet</h2>
                <p style={{ color: "#888", marginBottom: "2rem", maxWidth: "500px", margin: "0 auto 2rem" }}>
                  Upload competitive intelligence from Apify scrapes (Instagram, TikTok, etc.) to track competitor activity
                </p>
                <button onClick={() => setActiveTab("upload")} style={{ padding: "12px 24px", background: "#6aa6ff", color: "#fff", border: "none", borderRadius: "8px", fontSize: "1rem", cursor: "pointer", fontWeight: "600" }}>
                  Upload Competitive Data
                </button>
              </div>
            ) : (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📊 Total Data Points</div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard?.total_data_points || 0}</div>
                  </div>
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>🏢 Competitors Tracked</div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard?.competitors_tracked || 0}</div>
                  </div>
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>⚠️ High Threat Brands</div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ff6b6b" }}>
                      {brands?.brands?.high_threat?.length || 0}
                    </div>
                  </div>
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📅 Period</div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>30 days</div>
                  </div>
                </div>

                {dashboard?.competitors && Array.isArray(dashboard.competitors) && dashboard.competitors.length > 0 && (
                  <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "#e9edf2" }}>🏆 Most Active Competitors</h3>
                    <div style={{ display: "grid", gap: "1rem" }}>
                      {dashboard.competitors.slice(0, 10).map((comp, index) => {
                        const intelEntry = competitiveData.find(d => d.competitor === comp.competitor);
                        
                        return (
                          <div key={comp.competitor} style={{ background: "#0a0b0d", padding: "1.5rem", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "1rem", flex: 1 }}>
                                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#6aa6ff", background: "#0a0b0d", width: "40px", height: "40px", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid #2a2a2a" }}>
                                  #{index + 1}
                                </div>
                                <div style={{ flex: 1 }}>
                                  <div style={{ fontWeight: "600", fontSize: "1.1rem", marginBottom: "0.25rem", color: "#e9edf2" }}>
                                    {comp.competitor}
                                  </div>
                                  <div style={{ fontSize: "0.85rem", color: "#888" }}>
                                    <span style={{ 
                                      padding: "2px 8px", 
                                      borderRadius: "6px", 
                                      background: comp.threat_level === 'high' ? '#2a1a1a' : comp.threat_level === 'medium' ? '#2a2310' : '#1a2a1a',
                                      color: comp.threat_level === 'high' ? '#ff6b6b' : comp.threat_level === 'medium' ? '#f59e0b' : '#4ade80'
                                    }}>
                                      {comp.threat_level === 'high' ? 'High Threat' : comp.threat_level === 'medium' ? 'Medium Threat' : 'Low Threat'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                                <div style={{ textAlign: "right" }}>
                                  <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e9edf2" }}>
                                    {comp.total_posts || 0}
                                  </div>
                                  <div style={{ fontSize: "0.85rem", color: "#888" }}>
                                    {comp.avg_engagement || 0} avg engagement
                                  </div>
                                </div>
                                {intelEntry && (
                                  <button
                                    onClick={() => deleteIntelEntry(intelEntry.id, comp.competitor)}
                                    style={{
                                      padding: "8px 12px",
                                      background: "#2a1a1a",
                                      color: "#ff6b6b",
                                      border: "1px solid #3a2a2a",
                                      borderRadius: "6px",
                                      cursor: "pointer",
                                      fontSize: "0.85rem",
                                      fontWeight: "600"
                                    }}
                                    title="Delete this competitor entry"
                                  >
                                    🗑️ Delete
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {activeTab === "brands" && brands && (
          <div>
            <div style={{ marginBottom: "2rem" }}>
              <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#e9edf2" }}>Competitor Brands by Threat Level</h3>
              <p style={{ color: "#888", fontSize: "0.9rem" }}>
                Total: {brands?.total || 0} brands • {brands?.threat_levels?.high || 0} high threat • {brands?.threat_levels?.medium || 0} medium • {brands?.threat_levels?.low || 0} low
              </p>
            </div>

            {brands?.brands?.high_threat && Array.isArray(brands.brands.high_threat) && brands.brands.high_threat.length > 0 && (
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "1.5rem" }}>
                <h4 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#ff6b6b" }}>⚠️ High Threat ({brands.brands.high_threat.length})</h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "0.75rem" }}>
                  {brands.brands.high_threat.map(brand => {
                    const intelEntry = competitiveData.find(d => d.competitor === brand);
                    return (
                      <div key={brand} style={{ padding: "0.75rem 1rem", background: "#2a1a1a", borderRadius: "6px", color: "#ff6b6b", border: "1px solid #3a2a2a", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>{brand}</span>
                        {intelEntry && (
                          <button
                            onClick={() => deleteIntelEntry(intelEntry.id, brand)}
                            style={{ background: "none", border: "none", color: "#ff6b6b", cursor: "pointer", fontSize: "1rem", padding: "0 4px" }}
                            title="Delete"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {brands?.brands?.medium_threat && Array.isArray(brands.brands.medium_threat) && brands.brands.medium_threat.length > 0 && (
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "1.5rem" }}>
                <h4 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#f59e0b" }}>⚡ Medium Threat ({brands.brands.medium_threat.length})</h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "0.75rem" }}>
                  {brands.brands.medium_threat.map(brand => {
                    const intelEntry = competitiveData.find(d => d.competitor === brand);
                    return (
                      <div key={brand} style={{ padding: "0.75rem 1rem", background: "#2a2310", borderRadius: "6px", color: "#f59e0b", border: "1px solid #3a3320", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>{brand}</span>
                        {intelEntry && (
                          <button
                            onClick={() => deleteIntelEntry(intelEntry.id, brand)}
                            style={{ background: "none", border: "none", color: "#f59e0b", cursor: "pointer", fontSize: "1rem", padding: "0 4px" }}
                            title="Delete"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {brands?.brands?.low_threat && Array.isArray(brands.brands.low_threat) && brands.brands.low_threat.length > 0 && (
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <h4 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#4ade80" }}>✅ Low Threat ({brands.brands.low_threat.length})</h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "0.75rem" }}>
                  {brands.brands.low_threat.map(brand => {
                    const intelEntry = competitiveData.find(d => d.competitor === brand);
                    return (
                      <div key={brand} style={{ padding: "0.75rem 1rem", background: "#1a2a1a", borderRadius: "6px", color: "#4ade80", border: "1px solid #2a3a2a", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>{brand}</span>
                        {intelEntry && (
                          <button
                            onClick={() => deleteIntelEntry(intelEntry.id, brand)}
                            style={{ background: "none", border: "none", color: "#4ade80", cursor: "pointer", fontSize: "1rem", padding: "0 4px" }}
                            title="Delete"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {(!brands?.brands?.high_threat?.length && !brands?.brands?.medium_threat?.length && !brands?.brands?.low_threat?.length) && (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📊</div>
                <h3 style={{ marginBottom: "1rem", color: "#e9edf2" }}>No Brand Data Available</h3>
                <p style={{ color: "#888" }}>Upload competitive intelligence to see brand categorization</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "comparison" && (
          <div>
            {!hasData ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⚔️</div>
                <h3 style={{ marginBottom: "1rem", color: "#e9edf2" }}>No Data for Comparison</h3>
                <p style={{ color: "#888" }}>Upload competitive intelligence to compare Crooks & Castles against competitors</p>
              </div>
            ) : (
              <>
                <div style={{ marginBottom: "2rem" }}>
                  <h3 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#e9edf2" }}>⚔️ Crooks & Castles vs Competitors</h3>
                  <p style={{ color: "#888", fontSize: "0.9rem" }}>
                    Compare engagement, activity, and sentiment
                  </p>
                </div>

                <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "2rem" }}>
                  <h4 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "#e9edf2" }}>
                    🏰 Crooks & Castles vs All Competitors
                  </h4>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
                    <div>
                      <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>Crooks & Castles</div>
                      <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#6aa6ff", marginBottom: "1rem" }}>
                        Track Here
                      </div>
                      <div style={{ fontSize: "0.85rem", color: "#888" }}>
                        Add Crooks data to see comparison
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                        All Competitors Combined
                      </div>
                      <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#ff6b6b", marginBottom: "1rem" }}>
                        {dashboard?.total_data_points || 0}
                      </div>
                      <div style={{ fontSize: "0.85rem", color: "#888" }}>
                        {dashboard?.competitors_tracked || 0} brands • Last 30 days
                      </div>
                    </div>
                  </div>
                </div>

                {dashboard?.competitors && Array.isArray(dashboard.competitors) && dashboard.competitors.length > 0 && (
                  <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <h4 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "#e9edf2" }}>
                      🏰 Crooks vs Individual Brands
                    </h4>
                    
                    {dashboard.competitors.map(comp => (
                      <div key={comp.competitor} style={{ background: "#0a0b0d", padding: "1.5rem", borderRadius: "8px", marginBottom: "1rem", border: "1px solid #2a2a2a" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", alignItems: "center" }}>
                          <div>
                            <div style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.5rem" }}>🏰 Crooks & Castles</div>
                            <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#6aa6ff" }}>—</div>
                            <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}>Add data to compare</div>
                          </div>
                          <div style={{ borderLeft: "1px solid #2a2a2a", paddingLeft: "2rem" }}>
                            <div style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.5rem" }}>
                              {comp.competitor}
                              <span style={{ 
                                marginLeft: "0.5rem",
                                padding: "2px 8px", 
                                borderRadius: "6px", 
                                fontSize: "0.75rem",
                                background: comp.threat_level === 'high' ? '#2a1a1a' : comp.threat_level === 'medium' ? '#2a2310' : '#1a2a1a',
                                color: comp.threat_level === 'high' ? '#ff6b6b' : comp.threat_level === 'medium' ? '#f59e0b' : '#4ade80'
                              }}>
                                {comp.threat_level}
                              </span>
                            </div>
                            <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e9edf2" }}>
                              {comp.total_posts || 0} posts
                            </div>
                            <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}>
                              {comp.avg_engagement || 0} avg engagement
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "upload" && (
          <div>
            <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a", maxWidth: "700px", margin: "0 auto" }}>
              <h3 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", color: "#e9edf2" }}>📤 Upload Competitive Intelligence</h3>
              
              <div style={{ marginBottom: "2rem" }}>
                <h4 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#e9edf2" }}>How to Import Data:</h4>
                <ol style={{ color: "#888", lineHeight: "1.8", paddingLeft: "1.5rem" }}>
                  <li>Use <strong style={{ color: "#e9edf2" }}>Apify</strong> to scrape competitor Instagram, TikTok, or other social data</li>
                  <li>Export the scrape results as <strong style={{ color: "#e9edf2" }}>JSON</strong></li>
                  <li><strong style={{ color: "#e9edf2" }}>Optional:</strong> Enter the competitor brand name below</li>
                  <li>Upload the JSON file</li>
                  <li>System will automatically analyze engagement and sentiment</li>
                </ol>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={{ display: "block", marginBottom: "0.5rem", color: "#e9edf2", fontWeight: "600" }}>
                  Competitor Brand Name (Optional)
                </label>
                <input 
                  type="text"
                  placeholder="e.g., Supreme, Stussy, BAPE..."
                  value={manualCompetitorName}
                  onChange={(e) => setManualCompetitorName(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: "#0a0b0d",
                    border: "1px solid #2a2a2a",
                    borderRadius: "8px",
                    color: "#e9edf2",
                    fontSize: "1rem"
                  }}
                />
                <div style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#888" }}>
                  Leave blank to auto-detect from filename or data
                </div>
              </div>

              <div style={{ border: "2px dashed #2a2a2a", borderRadius: "12px", padding: "2rem", textAlign: "center", background: "#0a0b0d" }}>
                <input 
                  type="file" 
                  accept=".json,.jsonl" 
                  onChange={handleFileUpload}
                  disabled={uploading}
                  style={{ display: "none" }}
                  id="competitive-upload"
                />
                <label 
                  htmlFor="competitive-upload" 
                  style={{ 
                    display: "inline-block",
                    padding: "14px 28px", 
                    background: uploading ? "#444" : "#6aa6ff", 
                    color: "#fff", 
                    borderRadius: "8px", 
                    cursor: uploading ? "not-allowed" : "pointer",
                    fontWeight: "600",
                    fontSize: "1rem"
                  }}
                >
                  {uploading ? "Uploading..." : "📁 Choose JSON File"}
                </label>
                <div style={{ marginTop: "1rem", fontSize: "0.9rem", color: "#888" }}>
                  Supports .json and .jsonl files from Apify
                </div>
              </div>

              {hasData && (
                <div style={{ marginTop: "2rem", padding: "1rem", background: "#1a2a1a", borderRadius: "8px", borderLeft: "3px solid #4ade80" }}>
                  <div style={{ color: "#4ade80", fontWeight: "600", marginBottom: "0.5rem" }}>✅ Data Already Imported</div>
                  <div style={{ fontSize: "0.9rem", color: "#888" }}>
                    You have {dashboard?.total_data_points || 0} data points from {dashboard?.competitors_tracked || 0} competitors. Upload more to expand your intelligence.
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
