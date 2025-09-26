import { useState } from "react";
import ExecutiveSummaryCard from "../components/ExecutiveSummaryCard";

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function SummaryPage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const generateSummary = async () => {
    if (!brands.trim()) {
      setError("Please enter at least one brand name");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const brandList = brands.split(",").map(s => s.trim()).filter(Boolean);
      
      if (brandList.length === 0) {
        throw new Error("Please enter valid brand names");
      }

      const body = { 
        brands: brandList, 
        lookback_days: Number(days) 
      };

      const res = await fetch(`${API}/summary`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify(body) 
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Summary generation failed: HTTP ${res.status} - ${errorText}`);
      }

      const result = await res.json();
      setReport(result);
      setSuccess("Executive summary generated successfully!");
      
      // Auto-clear success message
      setTimeout(() => setSuccess(null), 5000);

    } catch (err) {
      console.error('Summary generation failed:', err);
      setError(`Failed to generate summary: ${err.message}`);
      
      // Set fallback data for development/testing
      setReport({
        narrative: `Executive summary generation failed: ${err.message}. This is fallback data for development.`,
        key_moves: [
          "Unable to analyze key moves - backend connection required",
          "Upload social media data to get actual insights",
          "Configure data sources for comprehensive analysis"
        ],
        risks: [
          "Missing data sources prevent accurate risk assessment",
          "Backend connectivity issues detected",
          "Consider uploading recent social media and e-commerce data"
        ],
        timeframe_days: days
      });
    } finally {
      setLoading(false);
    }
  };

  // Clear messages when user starts new actions
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="grid">
      {/* Status Messages */}
      {error && (
        <div className="card" style={{ border: '1px solid var(--danger)', background: 'rgba(239, 68, 68, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--danger)', margin: '0 0 8px 0' }}>Error</h3>
              <div style={{ color: 'var(--danger)' }}>{error}</div>
            </div>
            <button 
              className="button" 
              onClick={() => setError(null)}
              style={{ background: 'var(--danger)', minWidth: 'auto', padding: '6px 12px' }}
            >
              ×
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

      {/* Summary Generation Form */}
      <div className="card">
        <h3 className="title">Generate Executive Summary</h3>
        <div className="row" style={{ marginBottom: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{ flex: '1', minWidth: 200 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14, color: 'var(--muted)' }}>
              Brand Names (comma-separated)
            </label>
            <input 
              type="text"
              value={brands} 
              onChange={(e) => {
                setBrands(e.target.value);
                clearMessages();
              }}
              placeholder="e.g., Crooks & Castles, Stussy, Supreme"
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
          
          <div style={{ minWidth: 120 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14, color: 'var(--muted)' }}>
              Analysis Period (days)
            </label>
            <input 
              type="number" 
              min="1" 
              max="365" 
              value={days} 
              onChange={(e) => {
                setDays(Math.max(1, Math.min(365, parseInt(e.target.value) || 1)));
                clearMessages();
              }}
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
          
          <div style={{ alignSelf: 'flex-end' }}>
            <button 
              className="button" 
              onClick={() => {
                clearMessages();
                generateSummary();
              }}
              disabled={loading || !brands.trim()}
              style={{ padding: '10px 16px' }}
            >
              {loading ? 'Generating...' : 'Generate Summary'}
            </button>
          </div>
        </div>

        <div className="muted">
          {brands.trim() ? 
            `Will analyze last ${days} days for: ${brands}` : 
            'Enter brand names to generate an executive summary'
          }
        </div>

        {/* Analysis Parameters */}
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          background: 'rgba(255,255,255,0.02)', 
          borderRadius: 8,
          border: '1px solid var(--line)'
        }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: 14, color: 'var(--muted)' }}>
            What This Summary Includes:
          </h4>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13, color: 'var(--muted)' }}>
            <li>Competitive landscape overview and positioning</li>
            <li>Key strategic moves and market developments</li>
            <li>Risk assessment and potential challenges</li>
            <li>Performance metrics and engagement analysis</li>
            <li>Strategic recommendations and next steps</li>
          </ul>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card">
          <h3 className="title">Generating Executive Summary...</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="muted">
              Analyzing {brands} over the last {days} days. This may take a moment...
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ 
              width: '100%', 
              height: 4, 
              background: 'var(--line)', 
              borderRadius: 2, 
              overflow: 'hidden' 
            }}>
              <div style={{ 
                width: '30%', 
                height: '100%', 
                background: 'var(--brand)', 
                borderRadius: 2,
                animation: 'loading 2s infinite ease-in-out'
              }} />
            </div>
          </div>
        </div>
      )}

      {/* Executive Summary Display */}
      <ExecutiveSummaryCard report={report} />

      {/* Additional Summary Stats */}
      {report && (
        <div className="card">
          <h3 className="title">Summary Statistics</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--brand)' }}>
                {brands.split(',').map(b => b.trim()).filter(Boolean).length}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Brands Analyzed</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--ok)' }}>
                {report.key_moves?.length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Key Moves</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--warn)' }}>
                {report.risks?.length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Risk Factors</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: 'var(--muted)' }}>
                {report.timeframe_days || days}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Days Analyzed</div>
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="card">
        <h3 className="title">About Executive Summaries</h3>
        <div className="muted" style={{ lineHeight: 1.5, marginBottom: 12 }}>
          Executive summaries provide high-level strategic insights by analyzing social media 
          performance, competitive positioning, and market trends. Use these reports to inform 
          business strategy and identify opportunities or risks.
        </div>
        
        <div style={{ 
          padding: 12, 
          background: 'rgba(106, 166, 255, 0.1)', 
          borderRadius: 8,
          border: '1px solid var(--brand)'
        }}>
          <div style={{ color: 'var(--brand)', marginBottom: 4, fontSize: 14, fontWeight: 'bold' }}>
            Pro Tip
          </div>
          <div className="muted" style={{ fontSize: 13 }}>
            For best results, ensure you have uploaded recent social media data via the Intelligence 
            page before generating summaries. More data leads to more accurate insights.
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  );
}
