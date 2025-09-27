export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "48px auto", padding: 24 }}>
      <h1>Crooks Command Center</h1>
      <ul>
        <li><a href="/api-check">API Health Check</a></li>
        <li><a href="/upload">Upload Intelligence Data</a></li>
      </ul>
      <p style={{ opacity: 0.8 }}>Static site is served by FastAPI with API under /api.</p>
    </main>
  );
}
