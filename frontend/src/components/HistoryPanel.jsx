/**
 * HistoryPanel.jsx — Left column: WHAT THEY SAW
 * Complete chronological history of watched reels with interactive filters,
 * watch percentage indicators, and interaction signals.
 */
import React, { useState } from "react";

export default function HistoryPanel({ reels = [], activeIndex, onSelect }) {
  const [filter, setFilter] = useState("all");

  const filteredReels = reels.filter((r) => {
    const inter = r._user_interaction;
    if (!inter) return filter === "all";
    if (filter === "liked") return parseInt(inter.liked) === 1;
    if (filter === "saved") return parseInt(inter.saved) === 1;
    if (filter === "skipped") return parseInt(inter.skipped) === 1;
    return true;
  });

  return (
    <div className="history-col">
      <div className="col-header" style={{ flexDirection: "column", alignItems: "flex-start", gap: 6 }}>
        <div style={{ display: "flex", width: "100%", justifyContent: "space-between", alignItems: "center" }}>
          <span className="col-label past">WHAT THEY HAVE SEEN</span>
          <span className="col-count">{reels.length} watched</span>
        </div>

        {/* Quick Filter Chips */}
        <div style={{ display: "flex", gap: 4, width: "100%", marginTop: 2 }}>
          {["all", "liked", "saved", "skipped"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                fontSize: "0.62rem",
                padding: "2px 7px",
                borderRadius: 4,
                border: "1px solid var(--border)",
                background: filter === f ? "rgba(56, 189, 248, 0.15)" : "transparent",
                color: filter === f ? "var(--cyan)" : "var(--text-muted)",
                cursor: "pointer",
                textTransform: "capitalize",
                fontFamily: "var(--mono)",
                fontWeight: filter === f ? 700 : 500
              }}
            >
              {f === "all" ? `All (${reels.length})` : f}
            </button>
          ))}
        </div>
      </div>

      <div className="history-list">
        {filteredReels.length === 0 ? (
          <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)", fontSize: "0.78rem" }}>
            No reels found for this filter.
          </div>
        ) : (
          filteredReels.map((reel) => {
            const originalIndex = reel._index !== undefined ? reel._index : reels.indexOf(reel);
            const inter = reel._user_interaction;
            const liked = inter && parseInt(inter.liked) === 1;
            const saved = inter && parseInt(inter.saved) === 1;
            const replayed = inter && parseInt(inter.replayed) === 1;
            const skipped = inter && parseInt(inter.skipped) === 1;
            const watchPct = inter ? parseInt(inter.watch_percentage || 0) : 0;
            const progLang = reel.programming_languages ? reel.programming_languages.split("|")[0] : null;

            return (
              <div
                key={reel.reel_id || originalIndex}
                className={`history-item ${originalIndex === activeIndex ? "active" : ""}`}
                onClick={() => onSelect(originalIndex)}
              >
                <div className="history-index">{originalIndex + 1}</div>
                <div className="history-info">
                  <div className="history-title">{reel.title}</div>
                  <div className="history-meta">
                    {reel.creator?.creator_name || reel.creator_id || "Creator"} · {reel.duration_seconds || 30}s
                    {progLang && <span style={{ marginLeft: 6, color: "#38bdf8" }}>[{progLang}]</span>}
                  </div>

                  {/* Interaction Badges & Watch Progress */}
                  <div className="history-signals" style={{ marginTop: 4 }}>
                    {watchPct > 0 && (
                      <span
                        className={`signal-dot ${
                          watchPct >= 80 ? "positive" : watchPct <= 30 ? "negative" : ""
                        }`}
                        title="Watch percentage"
                      >
                        {watchPct}% watched
                      </span>
                    )}
                    {liked && <span className="signal-dot positive">♥ Liked</span>}
                    {saved && <span className="signal-dot positive">★ Saved</span>}
                    {replayed && <span className="signal-dot positive">↻ Replayed</span>}
                    {skipped && <span className="signal-dot negative">Skipped</span>}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
