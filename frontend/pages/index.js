import Link from "next/link";

export default function Home() {
  const links = [
    { href: "/executive", label: "Executive Overview" },
    { href: "/intelligence", label: "Intelligence" },
    { href: "/content", label: "Content Creation" },
    { href: "/media", label: "Asset Library" },
    { href: "/upload", label: "Upload (Data & Media)" },
    { href: "/calendar", label: "Calendar" },
    { href: "/summary", label: "Summary" },
    { href: "/agency", label: "Agency" },
    { href: "/shopify", label: "Shopify" }
  ];
  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Crooks Command Center</h1>
      <p style={{opacity:.8}}>Choose a module:</p>
      <ul style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",gap:12,listStyle:"none",padding:0}}>
        {links.map(l=>(
          <li key={l.href}>
            <Link href={l.href} style={{display:"block",padding:"12px 14px",border:"1px solid #ddd",borderRadius:10,textDecoration:"none"}}>
              {l.label} →
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
