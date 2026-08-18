/**
 * PresentPanel.jsx — Center column: WHAT THEY ARE SEEING
 * Clean reel viewer with simulated video screen, real interactions,
 * accessible progress bar, and AI latent interest reasoning.
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
      <section className="present-col" aria-label="Currently Playing Reel View">
        <div className="col-header">
          <h2 className="col-label present" style={{ margin: 0, fontSize: "0.7rem" }}>
            WHAT THEY ARE SEEING
          </h2>
        </div>
        <div className="present-body" style={{ alignItems: "center", justifyContent: "center" }}>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Select a user to begin</p>
        </div>
      </section>
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
    <section className="present-col" aria-label="Currently Playing Reel View">
      <div className="col-header">
        <h2 className="col-label present" style={{ margin: 0, fontSize: "0.7rem" }}>
          WHAT THEY ARE SEEING
        </h2>
      </div>

      <div className="present-body">
        {/* Reel Content Card */}
        <article className="reel-display" aria-label={`Current reel: ${reel.title}`}>
          {/* Simulated Screen / Video Canvas */}
          <div className="reel-screen">
            <div className="reel-screen-dots" aria-hidden="true">
              <span style={{ background: "#f43f5e" }} />
              <span style={{ background: "#f59e0b" }} />
              <span style={{ background: "#22c55e" }} />
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", boxShadow: "0 0 8px var(--cyan)" }} />
                <span style={{ fontSize: "0.64rem", color: "var(--cyan)", fontFamily: "var(--mono)", fontWeight: 800 }}>
                  SIMULATED REEL · {Math.round(watchProgress)}%
                </span>
              </div>
            </div>

            <div style={{ margin: "auto 0", padding: "10px 0" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#ffffff", lineHeight: 1.35, marginBottom: 8 }}>
                {reel.title}
              </h3>
              <p style={{ fontSize: "0.78rem", color: "var(--text-dim)", lineHeight: 1.55 }}>
                {reel.transcript || reel.caption || "Educational short-form technology reel analyzing architecture, algorithms, and practical implementation."}
              </p>
            </div>
          </div>

          {/* Accessible Watch Progress Bar */}
          <div
            className="progress-bar"
            role="progressbar"
            aria-valuenow={Math.round(watchProgress)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Reel playback progress"
          >
            <div className="progress-fill" style={{ width: `${watchProgress}%` }} />
          </div>

          <div className="reel-bottom">
            {/* Creator info */}
            <div className="reel-creator">
              <div
                aria-hidden="true"
                style={{ width: 24, height: 24, borderRadius: 6, background: "rgba(0, 212, 255, 0.2)", border: "1px solid rgba(0, 212, 255, 0.5)", display: "flex", alignItems: "center", justifyContent: "center", color: "#ffffff", fontSize: "0.72rem", fontWeight: 800 }}
              >
                {(reel.creator?.creator_name || "C")[0]}
              </div>
              <span>{reel.creator?.creator_name || reel.creator_id || "Creator"}</span>
              <span>@{reel.creator?.handle || reel.creator_id} · {duration}s</span>
            </div>

            {/* Metadata Tags */}
            <div className="tag-row" aria-label="Reel Metadata Tags">
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
              <div style={{ marginTop: 10, padding: "8px 10px", background: "rgba(4, 10, 24, 0.6)", borderRadius: 8, fontSize: "0.7rem", fontFamily: "var(--mono)", color: "var(--cyan)", border: "1px solid var(--glass-border)" }}>
                <span style={{ color: "var(--text-muted)", fontSize: "0.62rem", textTransform: "uppercase", fontWeight: 800 }}>OCR Text: </span>
                {reel.ocr_text}
              </div>
            )}
          </div>
        </article>

        {/* Real Engagement Actions */}
        <div className="engagement-row" role="group" aria-label="Reel Engagement Actions">
          <button
            className={`eng-btn ${liked ? "liked" : ""}`}
            aria-pressed={liked}
            aria-label={liked ? "Liked reel" : "Like reel"}
            onClick={() => {
              setLiked(!liked);
              onInteract(buildPayload({ liked: !liked ? 1 : 0 }));
            }}
          >
            ♥ {liked ? "Liked" : "Like"}
          </button>

          <button
            className={`eng-btn ${saved ? "saved" : ""}`}
            aria-pressed={saved}
            aria-label={saved ? "Saved reel" : "Save reel"}
            onClick={() => {
              setSaved(!saved);
              onInteract(buildPayload({ saved: !saved ? 1 : 0 }));
            }}
          >
            ★ {saved ? "Saved" : "Save"}
          </button>

          <button
            className={`eng-btn ${replayed ? "on" : ""}`}
            aria-label="Replay reel from beginning"
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
            aria-pressed={followed}
            aria-label={followed ? "Following creator" : "Follow creator"}
            onClick={() => {
              setFollowed(!followed);
              onInteract(buildPayload({ followed_creator: !followed ? 1 : 0 }));
            }}
          >
            {followed ? "✓ Following" : "+ Follow"}
          </button>

          <button
            className="eng-btn skip-btn"
            aria-label="Skip to next reel"
            onClick={() => {
              onInteract(buildPayload({ skipped: 1, watch_percentage: Math.min(watchProgress, 15), liked: 0, saved: 0, replayed: 0 }));
            }}
          >
            ▸ Skip
          </button>
        </div>

        {/* AI Latent Interest Inference Card */}
        {recommendation && !loading && (
          <aside className="analysis-card" aria-label="AI Latent Interest Analysis" aria-live="polite">
            <h3 className="analysis-title" style={{ margin: 0 }}>
              🧠 AI Latent Interest Inference
            </h3>
            <div className="analysis-interest">
              {recommendation.interest_detected}
            </div>
            <div className="analysis-evidence">
              {recommendation.why_recommendation || "Inferred from cumulative watch-time, engagement signals, and underlying concept relationships."}
            </div>
          </aside>
        )}
      </div>
    </section>
  );
}
