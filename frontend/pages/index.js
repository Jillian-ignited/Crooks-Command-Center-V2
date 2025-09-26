import { useState, useEffect } from 'react';
import CalendarView from '../components/CalendarView';
import AgencyDeliverables from '../components/AgencyDeliverables';
import MediaLibrary from '../components/MediaLibrary';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check API status on load
    const checkApiStatus = async () => {
      try {
        const response = await fetch('/api/status');
        if (response.ok) {
          setApiStatus('online');
        } else {
          setApiStatus('offline');
        }
      } catch (error) {
        setApiStatus('offline');
      }
    };

    checkApiStatus();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Crooks & Castles Command Center V2</h1>
        <div className="api-status">
          <span className={`status-indicator ${apiStatus}`}>
            API: {apiStatus}
          </span>
        </div>
      </header>

      <nav className="app-navigation">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'calendar' ? 'active' : ''}
          onClick={() => setActiveTab('calendar')}
        >
          Calendar
        </button>
        <button 
          className={activeTab === 'agency' ? 'active' : ''}
          onClick={() => setActiveTab('agency')}
        >
          Agency
        </button>
        <button 
          className={activeTab === 'media' ? 'active' : ''}
          onClick={() => setActiveTab('media')}
        >
          Media Library
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-view">
            <h2>Dashboard Overview</h2>
            <div className="dashboard-grid">
              <div className="dashboard-card">
                <h3>System Status</h3>
                <p>All systems operational</p>
              </div>
              <div className="dashboard-card">
                <h3>Quick Actions</h3>
                <button onClick={() => setActiveTab('calendar')}>
                  View Calendar
                </button>
                <button onClick={() => setActiveTab('agency')}>
                  Agency Dashboard
                </button>
                <button onClick={() => setActiveTab('media')}>
                  Media Library
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'calendar' && <CalendarView />}
        {activeTab === 'agency' && <AgencyDeliverables />}
        {activeTab === 'media' && <MediaLibrary />}
      </main>

      <style jsx>{`
        .app-container {
          min-height: 100vh;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .app-header {
          background: #1a1a1a;
          color: white;
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .app-header h1 {
          margin: 0;
          font-size: 1.5rem;
        }

        .status-indicator {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .status-indicator.online {
          background: #10b981;
          color: white;
        }

        .status-indicator.offline {
          background: #ef4444;
          color: white;
        }

        .status-indicator.checking {
          background: #f59e0b;
          color: white;
        }

        .app-navigation {
          background: #f3f4f6;
          padding: 0;
          display: flex;
          border-bottom: 1px solid #e5e7eb;
        }

        .app-navigation button {
          background: none;
          border: none;
          padding: 1rem 2rem;
          cursor: pointer;
          font-size: 1rem;
          border-bottom: 3px solid transparent;
          transition: all 0.2s;
        }

        .app-navigation button:hover {
          background: #e5e7eb;
        }

        .app-navigation button.active {
          background: white;
          border-bottom-color: #3b82f6;
          font-weight: 600;
        }

        .app-content {
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .dashboard-view h2 {
          margin-bottom: 2rem;
          color: #1f2937;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
        }

        .dashboard-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .dashboard-card h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          color: #1f2937;
        }

        .dashboard-card button {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          margin-right: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .dashboard-card button:hover {
          background: #2563eb;
        }

        /* Global styles for components */
        :global(.calendar-container),
        :global(.agency-container) {
          background: white;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        :global(.loading-indicator) {
          text-align: center;
          padding: 2rem;
        }

        :global(.spinner) {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f4f6;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        :global(.error-message) {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #dc2626;
          padding: 1rem;
          border-radius: 4px;
          margin: 1rem 0;
        }

        :global(.pill) {
          background: #e5e7eb;
          color: #374151;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        :global(.status-pill) {
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: capitalize;
        }

        :global(.status-pill.completed) {
          background: #d1fae5;
          color: #065f46;
        }

        :global(.status-pill.pending) {
          background: #fef3c7;
          color: #92400e;
        }

        :global(.status-pill.in.progress) {
          background: #dbeafe;
          color: #1e40af;
        }
      `}</style>
    </div>
  );
}
