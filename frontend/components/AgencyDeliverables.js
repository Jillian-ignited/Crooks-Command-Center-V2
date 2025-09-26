import { useState, useEffect } from 'react';

export default function AgencyDeliverables() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deliverables, setDeliverables] = useState([]);
  const [projects, setProjects] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [filter, setFilter] = useState('all');
  
  // Define API base URL with /api prefix
  const API = process.env.NEXT_PUBLIC_API_BASE || "/api";
  
  useEffect(() => {
    const fetchAgencyData = async () => {
      setLoading(true);
      try {
        // Use API prefix for all fetch calls
        const [deliverablesRes, projectsRes, metricsRes] = await Promise.all([
          fetch(`${API}/agency/deliverables`),
          fetch(`${API}/agency/projects`),
          fetch(`${API}/agency/metrics`)
        ]);
        
        if (!deliverablesRes.ok) {
          throw new Error(`Failed to load deliverables: ${deliverablesRes.status}`);
        }
        
        if (!projectsRes.ok) {
          throw new Error(`Failed to load projects: ${projectsRes.status}`);
        }
        
        if (!metricsRes.ok) {
          throw new Error(`Failed to load metrics: ${metricsRes.status}`);
        }
        
        const deliverablesData = await deliverablesRes.json();
        const projectsData = await projectsRes.json();
        const metricsData = await metricsRes.json();
        
        setDeliverables(deliverablesData.deliverables || []);
        setProjects(projectsData.projects || []);
        setMetrics(metricsData);
        setError(null);
      } catch (err) {
        console.error("Agency data fetch error:", err);
        setError(`Failed to load agency data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAgencyData();
  }, [API]); // Include API in dependencies
  
  const filteredDeliverables = filter === 'all' 
    ? deliverables 
    : deliverables.filter(d => d.status.toLowerCase() === filter);
  
  const handleStatusUpdate = async (id, newStatus) => {
    try {
      // Use API prefix for the update call
      const response = await fetch(`${API}/agency/deliverables/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update status: ${response.status}`);
      }
      
      // Update local state
      setDeliverables(deliverables.map(d => 
        d.id === id ? { ...d, status: newStatus } : d
      ));
    } catch (err) {
      console.error("Status update error:", err);
      alert(`Failed to update status: ${err.message}`);
    }
  };
  
  return (
    <div className="agency-container">
      <div className="agency-header">
        <h2>Agency Deliverables</h2>
        <div className="filter-controls">
          <button 
            className={filter === 'all' ? 'active' : ''} 
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'pending' ? 'active' : ''} 
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button 
            className={filter === 'in progress' ? 'active' : ''} 
            onClick={() => setFilter('in progress')}
          >
            In Progress
          </button>
          <button 
            className={filter === 'completed' ? 'active' : ''} 
            onClick={() => setFilter('completed')}
          >
            Completed
          </button>
        </div>
      </div>
      
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading agency data...</p>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}
      
      {!loading && !error && (
        <>
          {metrics && (
            <div className="metrics-dashboard">
              <div className="metric-card">
                <h3>Completion Rate</h3>
                <div className="metric-value">{metrics.completion_rate}%</div>
                <div className="metric-trend">
                  {metrics.completion_trend > 0 ? '↑' : '↓'} {Math.abs(metrics.completion_trend)}%
                </div>
              </div>
              
              <div className="metric-card">
                <h3>On-Time Delivery</h3>
                <div className="metric-value">{metrics.on_time_rate}%</div>
                <div className="metric-trend">
                  {metrics.on_time_trend > 0 ? '↑' : '↓'} {Math.abs(metrics.on_time_trend)}%
                </div>
              </div>
              
              <div className="metric-card">
                <h3>Quality Score</h3>
                <div className="metric-value">{metrics.quality_score}/10</div>
                <div className="metric-trend">
                  {metrics.quality_trend > 0 ? '↑' : '↓'} {Math.abs(metrics.quality_trend)}
                </div>
              </div>
              
              <div className="metric-card">
                <h3>Active Projects</h3>
                <div className="metric-value">{metrics.active_projects}</div>
              </div>
            </div>
          )}
          
          <div className="deliverables-list">
            <h3>Deliverables ({filteredDeliverables.length})</h3>
            {filteredDeliverables.length > 0 ? (
              <table className="deliverables-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Project</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDeliverables.map((deliverable) => (
                    <tr key={deliverable.id}>
                      <td>{deliverable.title}</td>
                      <td>{deliverable.project}</td>
                      <td>{deliverable.due_date}</td>
                      <td>
                        <span className={`status-pill ${deliverable.status.toLowerCase()}`}>
                          {deliverable.status}
                        </span>
                      </td>
                      <td>
                        <select 
                          value={deliverable.status}
                          onChange={(e) => handleStatusUpdate(deliverable.id, e.target.value)}
                        >
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="muted">No deliverables match the current filter.</div>
            )}
          </div>
          
          <div className="projects-section">
            <h3>Active Projects</h3>
            <div className="projects-grid">
              {projects.map((project) => (
                <div key={project.id} className="project-card">
                  <h4>{project.name}</h4>
                  <div className="project-meta">
                    <div>Client: {project.client}</div>
                    <div>Timeline: {project.start_date} - {project.end_date}</div>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${project.completion_percentage}%` }}
                    ></div>
                  </div>
                  <div className="progress-label">
                    {project.completion_percentage}% Complete
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
