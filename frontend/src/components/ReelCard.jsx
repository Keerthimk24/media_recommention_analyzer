/**
 * frontend/src/components/ReelCard.jsx
 * Simulated vertical Reel video player with animated canvas, syntax/whiteboard visuals,
 * transcript overlay, OCR banner, audio language badge, and interactive engagement tray.
 */

import React, { useState, useEffect } from "react";
import {
  Heart,
  Bookmark,
  Share2,
  RotateCcw,
  SkipForward,
  UserCheck,
  UserPlus,
  Play,
  Pause,
  Code2,
  Terminal,
  Cpu,
  Globe,
  Layers,
  Volume2
} from "lucide-react";

export default function ReelCard({
  reel,
  onInteract,
  onNextReel,
  isActive
}) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [watchProgress, setWatchProgress] = useState(0);
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [shared, setShared] = useState(false);
  const [replayed, setReplayed] = useState(false);
  const [followed, setFollowed] = useState(false);

  const duration = parseFloat(reel.duration_seconds || 30);

  // Initialize interaction state if historical reel has interaction attached
  useEffect(() => {
    if (reel._user_interaction) {
      const inter = reel._user_interaction;
      setLiked(Boolean(parseInt(inter.liked)));
      setSaved(Boolean(parseInt(inter.saved)));
      setShared(Boolean(parseInt(inter.shared)));
      setReplayed(Boolean(parseInt(inter.replayed)));
      setFollowed(Boolean(parseInt(inter.followed_creator)));
      setWatchProgress(parseFloat(inter.watch_percentage || 50));
    } else {
      setLiked(false);
      setSaved(false);
      setShared(false);
      setReplayed(false);
      setFollowed(false);
      setWatchProgress(0);
    }
  }, [reel.reel_id]);

  // Video playback simulator loop
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setWatchProgress((prev) => {
        if (prev >= 100) {
          return 100;
        }
        return prev + (100 / (duration * 10));
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, duration]);

  const handleToggleLike = () => {
    const nextVal = !liked;
    setLiked(nextVal);
    onInteract({
      reel_id: reel.reel_id,
      watch_percentage: watchProgress,
      liked: nextVal ? 1 : 0,
      saved: saved ? 1 : 0,
      shared: shared ? 1 : 0,
      replayed: replayed ? 1 : 0,
      skipped: 0,
      followed_creator: followed ? 1 : 0
    });
  };

  const handleToggleSave = () => {
    const nextVal = !saved;
    setSaved(nextVal);
    onInteract({
      reel_id: reel.reel_id,
      watch_percentage: watchProgress,
      liked: liked ? 1 : 0,
      saved: nextVal ? 1 : 0,
      shared: shared ? 1 : 0,
      replayed: replayed ? 1 : 0,
      skipped: 0,
      followed_creator: followed ? 1 : 0
    });
  };

  const handleReplay = () => {
    setReplayed(true);
    setWatchProgress(0);
    setIsPlaying(true);
    onInteract({
      reel_id: reel.reel_id,
      watch_percentage: 100,
      liked: liked ? 1 : 0,
      saved: saved ? 1 : 0,
      shared: shared ? 1 : 0,
      replayed: 1,
      skipped: 0,
      followed_creator: followed ? 1 : 0
    });
  };

  const handleSkip = () => {
    onInteract({
      reel_id: reel.reel_id,
      watch_percentage: Math.min(watchProgress, 15),
      liked: 0,
      saved: 0,
      shared: 0,
      replayed: 0,
      skipped: 1,
      followed_creator: 0
    });
    if (onNextReel) onNextReel();
  };

  const handleToggleFollow = () => {
    const nextVal = !followed;
    setFollowed(nextVal);
    onInteract({
      reel_id: reel.reel_id,
      watch_percentage: watchProgress,
      liked: liked ? 1 : 0,
      saved: saved ? 1 : 0,
      shared: shared ? 1 : 0,
      replayed: replayed ? 1 : 0,
      skipped: 0,
      followed_creator: nextVal ? 1 : 0
    });
  };

  const category = reel.category || "tech_educational";
  const contentLang = reel.content_language || "English";
  const progLangs = reel.programming_languages ? reel.programming_languages.split("|").filter(Boolean) : [];
  const techs = reel.technologies ? reel.technologies.split("|").filter(Boolean) : [];

  return (
    <div className="reel-card glass-panel">
      {/* Video Simulation Canvas */}
      <div className="reel-video-simulation" onClick={() => setIsPlaying(!isPlaying)}>
        <div className="simulated-screen">
          <div className="screen-header">
            <div className="traffic-dot dot-red"></div>
            <div className="traffic-dot dot-yellow"></div>
            <div className="traffic-dot dot-green"></div>
            <span style={{ marginLeft: "auto", fontSize: "0.72rem", color: "#64748b" }}>
              {reel.creator?.handle || "@tech_creator"} • {duration}s
            </span>
          </div>

          {/* Visual Simulation Display based on Category */}
          <div className="screen-content">
            {category === "tech_educational" || category === "HLD" ? (
              <div>
                <div style={{ color: "#38bdf8", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Terminal size={14} />
                  <span>// SYSTEM ARCHITECTURE & LOGIC</span>
                </div>
                <div style={{ color: "#94a3b8", fontSize: "0.8rem", marginBottom: "6px" }}>
                  {">"} {reel.title}
                </div>
                <div style={{ color: "#34d399", fontSize: "0.78rem" }}>
                  [OK] High concurrency pipeline initialized
                </div>
                <div style={{ color: "#a855f7", fontSize: "0.75rem", marginTop: "4px" }}>
                  {"func Scale(requests uint64) (Latency, Error)"}
                </div>
              </div>
            ) : category === "programming_meme" || category === "entertainment" ? (
              <div style={{ textAlign: "center", padding: "12px 0" }}>
                <div style={{ fontSize: "2rem", marginBottom: "6px" }}>☕ 💻 🐛</div>
                <div style={{ color: "#f43f5e", fontWeight: 600, fontSize: "0.85rem" }}>
                  POV: Debugging in Production
                </div>
                <div style={{ color: "#94a3b8", fontSize: "0.75rem", marginTop: "4px" }}>
                  "It works on my machine!"
                </div>
              </div>
            ) : category === "hype" ? (
              <div style={{ textAlign: "center", padding: "12px 0", border: "1px dashed #f43f5e", borderRadius: "8px" }}>
                <div style={{ fontSize: "1.6rem", marginBottom: "4px" }}>⚡ 🚨 💰</div>
                <div style={{ color: "#fb7185", fontWeight: 700, fontSize: "0.85rem" }}>
                  ⚠️ DETECTED HYPE CONTENT
                </div>
                <div style={{ color: "#cbd5e1", fontSize: "0.75rem" }}>
                  Superlative Claims / Fast Track Guarantee
                </div>
              </div>
            ) : (
              <div>
                <div style={{ color: "#a855f7", marginBottom: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Code2 size={14} />
                  <span>// {reel.topics || "Software Engineering"}</span>
                </div>
                <div style={{ color: "#cbd5e1", fontSize: "0.8rem" }}>
                  {reel.visual_description || "Technical diagram walkthrough"}
                </div>
              </div>
            )}
          </div>

          {/* OCR Text Banner Overlay */}
          {reel.ocr_text && (
            <div className="ocr-banner">
              <span style={{ fontSize: "0.68rem", textTransform: "uppercase", color: "#64748b", display: "block" }}>
                OCR Code On Screen:
              </span>
              <code>{reel.ocr_text}</code>
            </div>
          )}
        </div>

        {/* Play/Pause Float Indicator */}
        {!isPlaying && (
          <div
            style={{
              position: "absolute",
              background: "rgba(0,0,0,0.7)",
              borderRadius: "50%",
              padding: "16px",
              backdropFilter: "blur(8px)"
            }}
          >
            <Play size={32} color="#ffffff" />
          </div>
        )}
      </div>

      {/* Playback Progress Bar */}
      <div
        className="playback-bar"
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const clickX = e.clientX - rect.left;
          const newPct = (clickX / rect.width) * 100;
          setWatchProgress(newPct);
        }}
      >
        <div className="playback-fill" style={{ width: `${watchProgress}%` }}></div>
      </div>

      {/* Floating Info Overlay (Bottom Left) */}
      <div className="reel-overlay-info">
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
          <span style={{ fontWeight: 600, fontSize: "0.85rem", color: "#ffffff" }}>
            {reel.creator?.creator_name || reel.creator_id || "Creator"}
          </span>
          <span style={{ fontSize: "0.72rem", color: "#94a3b8" }}>
            {reel.creator?.handle}
          </span>
        </div>

        <h3 className="reel-title">{reel.title}</h3>
        <p className="reel-caption">{reel.transcript || reel.caption}</p>

        {/* Badges: Human Language, Programming Language, Intent */}
        <div className="badge-row">
          <span className="tech-badge badge-lang" title="Human spoken language (decoupled from code)">
            <Globe size={11} style={{ display: "inline", marginRight: "3px" }} />
            {contentLang}
          </span>

          {progLangs.map((pl) => (
            <span key={pl} className="tech-badge" style={{ borderColor: "#38bdf8", color: "#38bdf8" }}>
              {pl}
            </span>
          ))}

          {techs.slice(0, 2).map((t) => (
            <span key={t} className="tech-badge">
              {t}
            </span>
          ))}

          <span className="tech-badge badge-intent">
            {reel.intent || (category === "hype" ? "Hype" : category === "programming_meme" ? "Meme" : "Education")}
          </span>
        </div>
      </div>

      {/* Vertical Engagement Action Tray (Right Side) */}
      <div className="action-tray">
        {/* Creator Follow Button */}
        <button
          className={`tray-btn ${followed ? "liked" : ""}`}
          onClick={handleToggleFollow}
          title={followed ? "Following Creator" : "Follow Creator (+1.0 Signal)"}
        >
          {followed ? <UserCheck size={18} /> : <UserPlus size={18} />}
          <span className="tray-label">{followed ? "Following" : "Follow"}</span>
        </button>

        {/* Like */}
        <button
          className={`tray-btn ${liked ? "liked" : ""}`}
          onClick={handleToggleLike}
          title="Like (+0.5 Signal)"
        >
          <Heart size={18} fill={liked ? "#f72585" : "none"} />
          <span className="tray-label">{liked ? "Liked" : "Like"}</span>
        </button>

        {/* Save */}
        <button
          className={`tray-btn ${saved ? "saved" : ""}`}
          onClick={handleToggleSave}
          title="Save to Library (+0.9 Very Strong Signal)"
        >
          <Bookmark size={18} fill={saved ? "#f59e0b" : "none"} />
          <span className="tray-label">{saved ? "Saved" : "Save"}</span>
        </button>

        {/* Replay */}
        <button
          className={`tray-btn ${replayed ? "replayed" : ""}`}
          onClick={handleReplay}
          title="Replay Video (+0.8 Signal)"
        >
          <RotateCcw size={18} />
          <span className="tray-label">Replay</span>
        </button>

        {/* Skip */}
        <button
          className="tray-btn"
          onClick={handleSkip}
          title="Skip (< 2s = -0.8 Strong Negative Signal)"
          style={{ borderColor: "rgba(244, 63, 94, 0.4)" }}
        >
          <SkipForward size={18} color="#fb7185" />
          <span className="tray-label" style={{ color: "#fb7185" }}>Skip</span>
        </button>
      </div>
    </div>
  );
}
