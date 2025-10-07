import Link from "next/link";

export default function Layout({ children }) {
  return (
    <div className="container">
      <header className="row" style={{justifyContent:'space-between', marginBottom:16}}>
        <div className="row" style={{gap:10}}>
          <div className="pill">Crooks Command Center</div>
          <nav className="row" style={{gap:12, flexWrap: 'wrap', fontSize: '14px'}}>
            <Link href="/" style={{ fontWeight: '600' }}>Dashboard</Link>
            <Link href="/intelligence">Intelligence</Link>
            <Link href="/upload">Upload</Link>
            <Link href="/campaigns">Campaigns</Link>
            <Link href="/deliverables">Deliverables</Link>
            <Link href="/shopify">Shopify</Link>
            <Link href="/competitive" style={{ color: '#888' }}>Competitive (Soon)</Link>
          </nav>
        </div>
        <div className="muted">v3.0</div>
      </header>
      {children}
    </div>
  );
}
