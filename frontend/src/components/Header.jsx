/**
 * Header.jsx — Minimal top bar with Neu-Glass aesthetics
 */
import React from "react";

export default function Header({ users, selectedUserId, currentUser, onSelectUser, confidence, supabaseStatus, onOpenSupabaseModal, activeTab, setActiveTab }) {
  return (
    <div className="topbar">
      <div className="topbar-brand">
        <div className="brand-icon">⚡</div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span className="brand-name">AI Reels Agent</span>
          <span style={{ fontSize: "0.62rem", color: "var(--text-muted)", fontFamily: "var(--mono)", letterSpacing: "0.4px" }}>
            Latent Interest & Tech Recommender
          </span>
        </div>
      </div>

      <div className="topbar-nav">
        <button className={`nav-btn ${activeTab === "feed" ? "active" : ""}`} onClick={() => setActiveTab("feed")}>
          <span style={{ fontSize: "0.85rem" }}>⏱</span> Timeline
        </button>
        <button className={`nav-btn ${activeTab === "graph" ? "active" : ""}`} onClick={() => setActiveTab("graph")}>
          <span style={{ fontSize: "0.85rem" }}>🕸</span> Interest Graph
        </button>
        <button className={`nav-btn ${activeTab === "traps" ? "active" : ""}`} onClick={() => setActiveTab("traps")}>
          <span style={{ fontSize: "0.85rem" }}>🎯</span> Trap Lab
        </button>
      </div>

      <div className="topbar-right">
        <select className="user-select" value={selectedUserId || currentUser?.user_id || ""} onChange={(e) => onSelectUser(e.target.value)}>
          <optgroup label="Trap Benchmark Personas">
            <option value="TRAP_JAVA_BACKEND">TRAP: Java Meme -&gt; Backend / HLD</option>
            <option value="TRAP_MULTILINGUAL">TRAP: Telugu Spoken -&gt; Python / AI</option>
            <option value="TRAP_ENTERTAINMENT_HEAVY">TRAP: Entertainment -&gt; DSA</option>
          </optgroup>
          <optgroup label="Individual Student Profiles (U001 – U089)">
            {users.filter(u => !u.user_id.startsWith("TRAP_")).map(u => {
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

        <span className={`conf-badge ${confidence === "High" ? "high" : confidence === "Medium" ? "medium" : "low"}`}>
          ● {confidence || "Low"} Conf
        </span>

        <button className="db-btn" onClick={onOpenSupabaseModal}>
          <span style={{ color: supabaseStatus?.is_connected ? "#4ade80" : "var(--text-muted)", marginRight: 4 }}>●</span>
          {supabaseStatus?.is_connected ? "DB Live" : "DB"}
        </button>
      </div>
    </div>
  );
}
