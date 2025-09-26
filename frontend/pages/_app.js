import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import "../styles/globals.css";

// Global Error Boundary Component
function ErrorBoundary({ children }) {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleError = (event) => {
      console.error('Global error caught:', event.error);
      setHasError(true);
      setError(event.error);
    };

    const handleUnhandledRejection = (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      setHasError(true);
      setError(new Error(`Promise rejection: ${event.reason}`));
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  if (hasError) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg)',
        color: '#e9edf2',
        padding: 24
      }}>
        <div style={{
          maxWidth: 600,
          padding: 32,
          background: 'var(--panel)',
          borderRadius: 16,
          border: '1px solid var(--danger)',
          textAlign: 'center'
        }}>
          <h2 style={{ 
            color: 'var(--danger)', 
            marginBottom: 16, 
            fontSize: 24 
          }}>
            Application Error
          </h2>
          
          <div style={{ 
            marginBottom: 24, 
            color: 'var(--muted)', 
            lineHeight: 1.5 
          }}>
            Something went wrong. The application encountered an unexpected error.
          </div>
          
          <details style={{ 
            marginBottom: 24, 
            textAlign: 'left',
            background: 'rgba(0,0,0,0.3)',
            padding: 12,
            borderRadius: 8,
            fontSize: 13,
            color: 'var(--muted)'
          }}>
            <summary style={{ 
              cursor: 'pointer', 
              marginBottom: 8,
              color: 'var(--danger)'
            }}>
              Error Details
            </summary>
            <pre style={{ 
              whiteSpace: 'pre-wrap', 
              wordBreak: 'break-word',
              margin: 0,
              fontSize: 12
            }}>
              {error?.stack || error?.message || 'Unknown error'}
            </pre>
          </details>
          
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button 
              onClick={() => {
                setHasError(false);
                setError(null);
              }}
              style={{
                background: 'var(--brand)',
                color: 'white',
                border: 'none',
                padding: '12px 20px',
                borderRadius: 12,
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              Try Again
            </button>
            
            <button 
              onClick={() => window.location.reload()}
              style={{
                background: 'var(--line)',
                color: '#e9edf2',
                border: 'none',
                padding: '12px 20px',
                borderRadius: 12,
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              Reload Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return children;
}

// Main App Component
export default function App({ Component, pageProps }) {
  const [mounted, setMounted] = useState(false);

  // Handle client-side mounting to prevent hydration mismatches
  useEffect(() => {
    setMounted(true);
  }, []);

  // Show loading state during initial mount
  if (!mounted) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg)',
        color: '#e9edf2'
      }}>
        <div style={{
          textAlign: 'center',
          padding: 32
        }}>
          <div style={{ 
            fontSize: 24, 
            marginBottom: 16,
            background: 'linear-gradient(135deg, var(--brand), var(--brand-2))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Loading Command Center...
          </div>
          <div style={{
            width: 40,
            height: 4,
            background: 'var(--line)',
            borderRadius: 2,
            margin: '0 auto',
            overflow: 'hidden'
          }}>
            <div style={{
              width: '100%',
              height: '100%',
              background: 'var(--brand)',
              animation: 'loading 1.5s infinite ease-in-out'
            }} />
          </div>
        </div>

        <style jsx>{`
          @keyframes loading {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </ErrorBoundary>
  );
}
