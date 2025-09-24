import Link from "next/link";
import "../styles/globals.css";

export default function Layout({ children }) {
  return (
    <div className="container">
      <header className="row" style={{justifyContent:'space-between', marginBottom:16}}>
        <div className="row" style={{gap:10}}>
          <div className="pill">Crooks Command Center</div>
          <nav className="row" style={{gap:10}}>
            <Link href="/">Dashboard</Link>
            <Link href="/intelligence">Intelligence</Link>
            <Link href="/summary">Executive Summary</Link>
            <Link href="/calendar">Calendar</Link>
            <Link href="/agency">Agency</Link>
          </nav>
        </div>
        <div className="muted">v1.0</div>
      </header>
      {children}
    </div>
  );
}
