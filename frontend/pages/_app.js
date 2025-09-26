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
        background: '#0a0b0d',
        color: '#e9edf2',
        padding: 24
      }}>
        <div style={{
          maxWidth: 600,
          padding: 32,
          background: '#0f1217',
          borderRadius: 16,
          border: '1px solid #ef4444',
          textAlign: 'center'
        }}>
          <h2 style={{ 
            color: '#ef4444', 
            marginBottom: 16, 
            fontSize: 24 
          }}>
            Application Error
          </h2>
          
          <div style={{ 
            marginBottom: 24, 
            color: '#a1a8b3', 
            lineHeight: 1.5 
          }}>
            Something went wrong. The application encountered an unexpected error.
          </div>
          
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button 
              onClick={() => {
                setHasError(false);
                setError(null);
              }}
              style={{
                background: '#6aa6ff',
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
                background: '#1c2230',
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
        background: '#0a0b0d',
        color: '#e9edf2'
      }}>
        <div style={{
          textAlign: 'center',
          padding: 32
        }}>
          <div style={{ 
            fontSize: 24, 
            marginBottom: 16,
            color: '#6aa6ff'
          }}>
            Loading Command Center...
          </div>
        </div>
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
