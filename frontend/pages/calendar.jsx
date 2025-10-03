import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Calendar() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("30-day");

  const loadEvents = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/calendar/events`);
      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
      }
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Campaign Calendar</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Campaign Planning Calendar</h1>
        <div style={{ display: "flex", gap: "1rem" }}>
          <select 
            value={view} 
            onChange={(e) => setView(e.target.value)}
            style={{ padding: "8px 12px" }}
          >
            <option value="7-day">7-Day Tactical</option>
            <option value="30-day">30-Day Strategic</option>
            <option value="60-day">60-Day Opportunities</option>
            <option value="90-day">90-Day Vision</option>
          </select>
          <button onClick={loadEvents} style={{ padding: "8px 16px", cursor: "pointer" }}>
            Refresh
          </button>
        </div>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <ViewDescription view={view} />
      </div>

      <div style={{ display: "grid", gap: "1rem" }}>
        {events.length === 0 ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>
            No campaign events scheduled. Start planning your street culture content calendar.
          </div>
        ) : (
          events.map((event, i) => (
            <EventCard key={i} event={event} />
          ))
        )}
        
        <DefaultEvents view={view} />
      </div>
    </div>
  );
}

function ViewDescription({ view }) {
  const descriptions = {
    "7-day": "Detailed posts with assets, timing, and targets for immediate execution",
    "30-day": "Interactive drag-and-drop scheduling for strategic content planning",
    "60-day": "Cultural moments, BFCM, holidays, and seasonal opportunities",
    "90-day": "TikTok Shop launch, annual planning, and long-term vision"
  };

  return (
    <div style={{ 
      background: "#f9fafb", 
      border: "1px solid #e5e7eb", 
      borderRadius: "8px", 
      padding: "1rem" 
    }}>
      <h2 style={{ margin: "0 0 0.5rem 0" }}>{view.charAt(0).toUpperCase() + view.slice(1)} View</h2>
      <p style={{ margin: 0, color: "#6b7280" }}>{descriptions[view]}</p>
    </div>
  );
}

function EventCard({ event }) {
  return (
    <div style={{
      background: "white",
      border: "1px solid #e5e7eb",
      borderRadius: "8px",
      padding: "1rem"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
        <div>
          <h3 style={{ margin: "0 0 0.5rem 0" }}>{event.title}</h3>
          <p style={{ margin: "0 0 0.5rem 0", color: "#6b7280" }}>{event.description}</p>
          <div style={{ fontSize: "0.875rem", color: "#6b7280" }}>
            <span>📅 {event.date}</span>
            {event.category && <span style={{ marginLeft: "1rem" }}>🏷️ {event.category}</span>}
          </div>
        </div>
        <span style={{
          background: event.priority === "high" ? "#ef4444" : event.priority === "medium" ? "#f59e0b" : "#10b981",
          color: "white",
          padding: "0.25rem 0.75rem",
          borderRadius: "9999px",
          fontSize: "0.75rem",
          textTransform: "capitalize"
        }}>
          {event.priority} Priority
        </span>
      </div>
    </div>
  );
}

function DefaultEvents({ view }) {
  const getDefaultEvents = () => {
    switch (view) {
      case "7-day":
        return [
          {
            title: "Heritage Content Series",
            description: "Create 3 posts showcasing Crooks & Castles legacy",
            date: "Next 7 days",
            category: "Content Creation",
            priority: "high"
          }
        ];
      case "30-day":
        return [
          {
            title: "Monthly Content Calendar",
            description: "Plan 15-20 posts for authentic street culture engagement",
            date: "This month",
            category: "Strategic Planning",
            priority: "medium"
          }
        ];
      case "60-day":
        return [
          {
            title: "Black Friday Cyber Monday",
            description: "BFCM campaign planning and cultural moment alignment",
            date: "November 2024",
            category: "Cultural Moment",
            priority: "high"
          }
        ];
      case "90-day":
        return [
          {
            title: "TikTok Shop Launch",
            description: "Prepare for TikTok Shop integration and social commerce",
            date: "Q1 2025",
            category: "Platform Expansion",
            priority: "medium"
          }
        ];
      default:
        return [];
    }
  };

  return (
    <>
      {getDefaultEvents().map((event, i) => (
        <EventCard key={`default-${i}`} event={event} />
      ))}
    </>
  );
}
