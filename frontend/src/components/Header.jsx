/**
 * Header.jsx — Accessible Semantic Top Bar
 * Full ARIA accessibility, keyboard navigability, and responsive layout.
 */
import React from "react";

export default function Header({
  users = [],
  selectedUserId,
  currentUser,
  onSelectUser,
  confidence,
  supabaseStatus,
  onOpenSupabaseModal,
  activeTab,
  setActiveTab
}) {
  return (
    <header className="topbar" role="banner">
      <div className="topbar-brand">
        <div className="brand-icon" aria-hidden="true">⚡</div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <h1 className="brand-name">AI Reels Agent</h1>
          <span style={{ fontSize: "0.62rem", color: "var(--text-muted)", fontFamily: "var(--mono)", letterSpacing: "0.4px" }}>
            Latent Interest & Tech Recommender
          </span>
        </div>
      </div>

      <nav className="topbar-nav" role="tablist" aria-label="Main Navigation Tabs">
        <button
          role="tab"
          id="tab-feed"
          aria-controls="tabpanel-feed"
          aria-selected={activeTab === "feed"}
          className={`nav-btn ${activeTab === "feed" ? "active" : ""}`}
          onClick={() => setActiveTab("feed")}
        >
          <span aria-hidden="true" style={{ fontSize: "0.85rem" }}>⏱</span> Timeline
        </button>
        <button
          role="tab"
          id="tab-graph"
          aria-controls="tabpanel-graph"
          aria-selected={activeTab === "graph"}
          className={`nav-btn ${activeTab === "graph" ? "active" : ""}`}
          onClick={() => setActiveTab("graph")}
        >
          <span aria-hidden="true" style={{ fontSize: "0.85rem" }}>🕸</span> Interest Graph
        </button>
        <button
          role="tab"
          id="tab-traps"
          aria-controls="tabpanel-traps"
          aria-selected={activeTab === "traps"}
          className={`nav-btn ${activeTab === "traps" ? "active" : ""}`}
          onClick={() => setActiveTab("traps")}
        >
          <span aria-hidden="true" style={{ fontSize: "0.85rem" }}>🎯</span> Trap Lab
        </button>
      </nav>

      <div className="topbar-right">
        <label htmlFor="user-selector" className="sr-only" style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0,0,0,0)" }}>
          Select Student Profile
        </label>
        <select
          id="user-selector"
          className="user-select"
          aria-label="Select Student or Persona Profile"
          value={selectedUserId || currentUser?.user_id || ""}
          onChange={(e) => onSelectUser(e.target.value)}
        >
          <optgroup label="Trap Benchmark Personas">
            <option value="TRAP_JAVA_BACKEND">TRAP: Java Meme -&gt; Backend / HLD</option>
            <option value="TRAP_MULTILINGUAL">TRAP: Telugu Spoken -&gt; Python / AI</option>
            <option value="TRAP_ENTERTAINMENT_HEAVY">TRAP: Entertainment -&gt; DSA</option>
          </optgroup>
          <optgroup label="Individual Student Profiles (U001 – U089)">
            {users.filter((u) => !u.user_id?.startsWith("TRAP_")).map((u) => {
              const numStr = u.user_id.replace(/^U0*/, "") || "1";
              const shortId = `U${numStr.padStart(3, "0")}`;
              const label = u.true_primary_interest || u.persona || "Tech Student";
              return (
                <option key={u.user_id} value={u.user_id}>
                  {shortId} ({u.user_id}) — {label}
                </option>
              );
            })}
          </optgroup>
        </select>

        <span
          className={`conf-badge ${confidence === "High" ? "high" : confidence === "Medium" ? "medium" : "low"}`}
          aria-label={`Confidence Level: ${confidence || "Low"}`}
          title="Recommendation Confidence"
        >
          ● {confidence || "Low"} Conf
        </span>

        <button
          className="db-btn"
          onClick={onOpenSupabaseModal}
          aria-label="Open Supabase Cloud Database Configuration"
          title="Supabase Database Status"
        >
          <span style={{ color: supabaseStatus?.is_connected ? "#34d399" : "var(--text-muted)", marginRight: 4 }} aria-hidden="true">
            ●
          </span>
          {supabaseStatus?.is_connected ? "DB Live" : "DB"}
        </button>
      </div>
    </header>
  );
}
