/**
 * HistoryPanel.jsx — Left column: WHAT THEY SAW
 * Complete chronological history of watched reels with interactive filters,
 * watch percentage indicators, keyboard accessibility, and semantic markup.
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
    <aside className="history-col" aria-label="Viewing History Timeline">
      <div className="col-header" style={{ flexDirection: "column", alignItems: "flex-start", gap: 6 }}>
        <div style={{ display: "flex", width: "100%", justifyContent: "space-between", alignItems: "center" }}>
          <h2 className="col-label past" style={{ margin: 0, fontSize: "0.7rem" }}>
            WHAT THEY HAVE SEEN
          </h2>
          <span className="col-count" aria-label={`${reels.length} reels watched`}>
            {reels.length} watched
          </span>
        </div>

        {/* Quick Filter Chips */}
        <div
          role="group"
          aria-label="Filter watched reels by engagement"
          style={{ display: "flex", gap: 4, width: "100%", marginTop: 2 }}
        >
          {["all", "liked", "saved", "skipped"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              aria-pressed={filter === f}
              aria-label={`Filter by ${f} reels`}
              style={{
                fontSize: "0.64rem",
                padding: "3px 8px",
                borderRadius: 6,
                border: "1px solid var(--glass-border)",
                background: filter === f ? "rgba(0, 212, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
                color: filter === f ? "#ffffff" : "var(--text-muted)",
                cursor: "pointer",
                textTransform: "capitalize",
                fontFamily: "var(--mono)",
                fontWeight: filter === f ? 800 : 600
              }}
            >
              {f === "all" ? `All (${reels.length})` : f}
            </button>
          ))}
        </div>
      </div>

      <div
        className="history-list"
        role="feed"
        aria-label="Watched Reels List"
        tabIndex={0}
      >
        {filteredReels.length === 0 ? (
          <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)", fontSize: "0.78rem" }}>
            No reels found for this filter.
          </div>
        ) : (
          filteredReels.map((reel) => {
            const originalIndex = reel._index !== undefined ? reel._index : reels.indexOf(reel);
            const isActive = originalIndex === activeIndex;
            const inter = reel._user_interaction;
            const liked = inter && parseInt(inter.liked) === 1;
            const saved = inter && parseInt(inter.saved) === 1;
            const replayed = inter && parseInt(inter.replayed) === 1;
            const skipped = inter && parseInt(inter.skipped) === 1;
            const watchPct = inter ? parseInt(inter.watch_percentage || 0) : 0;
            const progLang = reel.programming_languages ? reel.programming_languages.split("|")[0] : null;

            return (
              <article
                key={reel.reel_id || originalIndex}
                className={`history-item ${isActive ? "active" : ""}`}
                onClick={() => onSelect(originalIndex)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(originalIndex);
                  }
                }}
                tabIndex={0}
                role="button"
                aria-pressed={isActive}
                aria-label={`Reel ${originalIndex + 1}: ${reel.title}`}
              >
                <div className="history-index" aria-hidden="true">{originalIndex + 1}</div>
                <div className="history-info">
                  <div className="history-title">{reel.title}</div>
                  <div className="history-meta">
                    {reel.creator?.creator_name || reel.creator_id || "Creator"} · {reel.duration_seconds || 30}s
                    {progLang && <span style={{ marginLeft: 6, color: "var(--cyan)" }}>[{progLang}]</span>}
                  </div>

                  {/* Interaction Badges & Watch Progress */}
                  <div className="history-signals" style={{ marginTop: 4 }}>
                    {watchPct > 0 && (
                      <span
                        className={`signal-dot ${
                          watchPct >= 80 ? "positive" : watchPct <= 30 ? "negative" : ""
                        }`}
                        aria-label={`Watched ${watchPct} percent`}
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
              </article>
            );
          })
        )}
      </div>
    </aside>
  );
}
