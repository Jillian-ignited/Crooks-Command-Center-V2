import Link from "next/link";

export default function Layout({ children }) {
  return (
    <div className="container">
      <header className="row" style={{justifyContent:'space-between', marginBottom:16}}>
        <div className="row" style={{gap:10}}>
          <div className="pill">Crooks Command Center</div>
          <nav className="row" style={{gap:6, flexWrap: 'wrap', fontSize: '14px'}}>
            <Link href="/">Dashboard</Link>
            <Link href="/executive" style={{ 
              fontWeight: 'bold',
              color: 'var(--brand)',
              textDecoration: 'underline'
            }}>
              Executive Overview
            </Link>
            <Link href="/intelligence">Intelligence</Link>
            <Link href="/summary">Executive Summary</Link>
            <Link href="/shopify">Shopify</Link>
            <Link href="/competitive">Competitive Intelligence</Link>
            <Link href="/content">Content Creation</Link>
            <Link href="/media">Media Library</Link>
            <Link href="/calendar">Calendar</Link>
            <Link href="/agency">Agency</Link>
            <Link href="/ingest">Data Ingest</Link>
          </nav>
        </div>
        <div className="muted">v2.1</div>
      </header>
      {children}
    </div>
  );
}
