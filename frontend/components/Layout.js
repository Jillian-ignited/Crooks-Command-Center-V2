import Link from "next/link";

export default function Layout({ children }) {
  return (
    <div className="container">
      <header className="row" style={{justifyContent:'space-between', marginBottom:16}}>
        <div className="row" style={{gap:10}}>
          <div className="pill">Crooks Command Center</div>
          <nav className="row" style={{gap:12, flexWrap: 'wrap', fontSize: '14px'}}>
            <Link href="/" style={{ fontWeight: '600', textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Dashboard</Link>
            <Link href="/intelligence" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Intelligence</Link>
            <Link href="/upload" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Upload</Link>
            <Link href="/campaigns" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Campaigns</Link>
            <Link href="/deliverables" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Deliverables</Link>
            <Link href="/shopify" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Shopify</Link>
            <Link href="/competitive" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>Competitive</Link>
          </nav>
        </div>
        <div className="muted">v3.0</div>
      </header>
      {children}
    </div>
  );
}
