/**
 * PresentPanel.jsx — Center column: WHAT THEY ARE SEEING
 * Clean reel viewer with exact details, real interactions, and clean detected interest tag.
 */
import React, { useState, useEffect } from "react";

export default function PresentPanel({ reel, onInteract, recommendation, loading }) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [replayed, setReplayed] = useState(false);
  const [followed, setFollowed] = useState(false);
  const [watchProgress, setWatchProgress] = useState(0);

  const duration = parseFloat(reel?.duration_seconds || 30);

  useEffect(() => {
    if (!reel) return;
    const inter = reel._user_interaction;
    if (inter) {
      setLiked(Boolean(parseInt(inter.liked)));
      setSaved(Boolean(parseInt(inter.saved)));
      setReplayed(Boolean(parseInt(inter.replayed)));
      setFollowed(Boolean(parseInt(inter.followed_creator)));
      setWatchProgress(parseFloat(inter.watch_percentage || 50));
    } else {
      setLiked(false);
      setSaved(false);
      setReplayed(false);
      setFollowed(false);
      setWatchProgress(0);
    }
  }, [reel?.reel_id]);

  // Auto-advance watch progress
  useEffect(() => {
    const iv = setInterval(() => {
      setWatchProgress((p) => (p >= 100 ? 100 : p + 100 / (duration * 10)));
    }, 100);
    return () => clearInterval(iv);
  }, [duration, reel?.reel_id]);

  if (!reel) {
    return (
      <div className="present-col">
        <div className="col-header">
          <span className="col-label present">WHAT THEY ARE SEEING</span>
        </div>
        <div className="present-body" style={{ alignItems: "center", justifyContent: "center" }}>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Select a user to begin</p>
        </div>
      </div>
    );
  }

  const buildPayload = (overrides = {}) => ({
    reel_id: reel.reel_id,
    watch_percentage: watchProgress,
    liked: liked ? 1 : 0,
    saved: saved ? 1 : 0,
    shared: 0,
    replayed: replayed ? 1 : 0,
    skipped: 0,
    followed_creator: followed ? 1 : 0,
    ...overrides
  });

  const contentLang = reel.content_language || "English";
  const progLangs = reel.programming_languages ? reel.programming_languages.split("|").filter(Boolean) : [];
  const techs = reel.technologies ? reel.technologies.split("|").filter(Boolean) : [];
  const topics = reel.topics ? reel.topics.split("|").filter(Boolean) : [];

  return (
    <div className="present-col">
      <div className="col-header">
        <span className="col-label present">WHAT THEY ARE SEEING</span>
      </div>

      <div className="present-body">
        {/* Reel Content Card */}
        <div className="reel-display">
          {/* Watch Progress Bar */}
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${watchProgress}%` }} />
          </div>

          <div className="reel-bottom">
            {/* Creator info */}
            <div className="reel-creator">
              {reel.creator?.creator_name || reel.creator_id || "Creator"}
              <span>@{reel.creator?.handle || reel.creator_id} · {duration}s</span>
            </div>

            {/* Reel Title */}
            <div className="reel-title-text" style={{ fontSize: "0.95rem", fontWeight: 700, margin: "6px 0" }}>
              {reel.title}
            </div>

            {/* Transcript or Caption */}
            {(reel.transcript || reel.caption) && (
              <div className="reel-desc" style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginBottom: 8 }}>
                {reel.transcript || reel.caption}
              </div>
            )}

            {/* Metadata Tags */}
            <div className="reel-tags">
              <span className="tag tag-lang">{contentLang}</span>
              {progLangs.map((pl) => (
                <span key={pl} className="tag tag-tech">{pl}</span>
              ))}
              {techs.slice(0, 3).map((t) => (
                <span key={t} className="tag tag-tech">{t}</span>
              ))}
              {topics.slice(0, 2).map((t) => (
                <span key={t} className="tag tag-intent">{t}</span>
              ))}
            </div>

            {/* OCR On-Screen Text if present */}
            {reel.ocr_text && (
              <div style={{ marginTop: 8, padding: "6px 8px", background: "rgba(0,0,0,0.35)", borderRadius: 6, fontSize: "0.68rem", fontFamily: "var(--mono)", color: "var(--cyan)" }}>
                <span style={{ color: "var(--text-muted)", fontSize: "0.6rem", textTransform: "uppercase" }}>OCR: </span>
                {reel.ocr_text}
              </div>
            )}
          </div>
        </div>

        {/* Real Engagement Actions */}
        <div className="engagement-row">
          <button
            className={`eng-btn ${liked ? "liked" : ""}`}
            onClick={() => {
              setLiked(!liked);
              onInteract(buildPayload({ liked: !liked ? 1 : 0 }));
            }}
          >
            ♥ {liked ? "Liked" : "Like"}
          </button>

          <button
            className={`eng-btn ${saved ? "saved" : ""}`}
            onClick={() => {
              setSaved(!saved);
              onInteract(buildPayload({ saved: !saved ? 1 : 0 }));
            }}
          >
            ★ {saved ? "Saved" : "Save"}
          </button>

          <button
            className={`eng-btn ${replayed ? "on" : ""}`}
            onClick={() => {
              setReplayed(true);
              setWatchProgress(0);
              onInteract(buildPayload({ replayed: 1, watch_percentage: 100 }));
            }}
          >
            ↻ Replay
          </button>

          <button
            className={`eng-btn ${followed ? "on" : ""}`}
            onClick={() => {
              setFollowed(!followed);
              onInteract(buildPayload({ followed_creator: !followed ? 1 : 0 }));
            }}
          >
            {followed ? "✓ Following" : "+ Follow"}
          </button>

          <button
            className="eng-btn skip-btn"
            onClick={() => {
              onInteract(buildPayload({ skipped: 1, watch_percentage: Math.min(watchProgress, 15), liked: 0, saved: 0, replayed: 0 }));
            }}
          >
            ▸ Skip
          </button>
        </div>

        {/* Inferred Interest Badge */}
        {recommendation && !loading && (
          <div
            style={{
              padding: "10px 14px",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between"
            }}
          >
            <span style={{ fontSize: "0.68rem", fontFamily: "var(--mono)", color: "var(--text-muted)", textTransform: "uppercase" }}>
              Inferred Interest:
            </span>
            <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--cyan)" }}>
              {recommendation.interest_detected}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
