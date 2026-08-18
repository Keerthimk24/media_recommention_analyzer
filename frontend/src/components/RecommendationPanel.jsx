/**
 * frontend/src/components/RecommendationPanel.jsx
 * Clean, scannable AI recommendation panel following Spec A.9 schema.
 */

import React, { useState } from "react";
import {
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Flame,
  Ban,
  Globe,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  BarChart2
} from "lucide-react";

export default function RecommendationPanel({ recommendation, onFeedback, loading }) {
  const [showScores, setShowScores] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(null);

  if (loading || !recommendation) {
    return (
      <div className="schema-card glass-panel" style={{ textAlign: "center", padding: "30px 20px" }}>
        <Sparkles size={22} color="#00e5ff" className="pulse-glow" style={{ margin: "0 auto 12px" }} />
        <h3 style={{ fontSize: "0.95rem", color: "#f1f5f9", marginBottom: 6 }}>
          Analyzing Viewing Behavior...
        </h3>
        <p style={{ fontSize: "0.78rem", color: "#64748b" }}>
          Extracting multimodal features and inferring latent interests.
        </p>
      </div>
    );
  }

  const handleFeedback = (type, topic, detail = null) => {
    onFeedback({ feedback_type: type, topic_or_category: topic, detail });
    setFeedbackSuccess(type);
    setTimeout(() => setFeedbackSuccess(null), 2500);
  };

  const bd = recommendation.score_breakdown || {};

  return (
    <div className="schema-card glass-panel fade-in">
      {/* Header */}
      <div className="schema-header">
        <div className="schema-title">AI Recommendation (A.9)</div>
        <span
          className={`confidence-pill ${
            recommendation.confidence === "High" ? "conf-high" :
            recommendation.confidence === "Medium" ? "conf-medium" : "conf-low"
          }`}
        >
          {recommendation.confidence}
        </span>
      </div>

      {/* CURRENT REEL */}
      <div className="schema-field">
        <div className="field-label">Current Reel</div>
        <div className="field-value" style={{ color: "#94a3b8", fontSize: "0.82rem" }}>
          {recommendation.current_reel_title || "Developer Video"}
        </div>
      </div>

      {/* INTEREST DETECTED */}
      <div className="schema-field">
        <div className="field-label">Interest Detected</div>
        <div className="field-value" style={{ color: "#38bdf8", fontWeight: 700, fontSize: "1rem" }}>
          {recommendation.interest_detected}
        </div>
      </div>

      {/* WHY */}
      <div className="schema-field">
        <div className="field-label">Why (Evidence)</div>
        <div style={{
          fontSize: "0.8rem",
          color: "#cbd5e1",
          background: "rgba(0,0,0,0.2)",
          padding: "8px 10px",
          borderRadius: 8,
          borderLeft: "2px solid #00e5ff",
          lineHeight: 1.5
        }}>
          {recommendation.why_evidence}
        </div>
      </div>

      {/* RECOMMENDED TECH REEL */}
      <div style={{
        marginTop: 12,
        padding: 12,
        background: "rgba(0, 229, 255, 0.04)",
        borderRadius: 12,
        border: "1px solid rgba(0, 229, 255, 0.15)"
      }}>
        <div className="field-label" style={{ color: "#38bdf8" }}>Recommended Tech Reel</div>
        <div className="rec-target-title">{recommendation.recommended_title}</div>
        <div style={{ display: "flex", gap: 8, marginTop: 6, alignItems: "center" }}>
          <span className="category-tag">{recommendation.category}</span>
          <span style={{ fontSize: "0.7rem", color: "#a855f7", fontFamily: "var(--font-mono)", fontWeight: 600 }}>
            {recommendation.difficulty}
          </span>
        </div>
      </div>

      {/* WHY THIS RECOMMENDATION */}
      <div className="schema-field" style={{ marginTop: 12 }}>
        <div className="field-label">Why This Recommendation</div>
        <div style={{
          fontSize: "0.8rem",
          color: "#cbd5e1",
          background: "rgba(0,0,0,0.2)",
          padding: "8px 10px",
          borderRadius: 8,
          borderLeft: "2px solid #a855f7",
          lineHeight: 1.5
        }}>
          {recommendation.why_recommendation}
        </div>
      </div>

      {/* SCORE BREAKDOWN (collapsible) */}
      <div className="score-breakdown">
        <div
          style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}
          onClick={() => setShowScores(!showScores)}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: "0.7rem", color: "#64748b", fontWeight: 600 }}>
            <BarChart2 size={13} color="#00e5ff" />
            <span>7-Factor Score Breakdown</span>
          </div>
          {showScores ? <ChevronUp size={14} color="#64748b" /> : <ChevronDown size={14} color="#64748b" />}
        </div>

        {showScores && (
          <div className="neu-inset" style={{ padding: 10, marginTop: 8 }}>
            <ScoreRow label="Interest Relevance (0.40)" value={bd.interest_relevance || 0.85} color="#00e5ff" />
            <ScoreRow label="Content Quality (0.20)" value={bd.content_quality || 0.78} color="#38bdf8" />
            <ScoreRow label="Learning Value (0.15)" value={bd.learning_value || 0.82} color="#a855f7" />
            <ScoreRow label="Diversity / MMR (0.10)" value={bd.diversity || 0.90} color="#10b981" />
            <div className="score-bar-row">
              <span>Hype Penalty</span>
              <span style={{ color: bd.hype_penalty > 0 ? "#f43f5e" : "#10b981", fontFamily: "var(--font-mono)", fontSize: "0.7rem" }}>
                {bd.hype_penalty > 0 ? `-${bd.hype_penalty}` : "0.00 (Clean)"}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* FEEDBACK ACTIONS */}
      <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ fontSize: "0.68rem", color: "#64748b", fontWeight: 600, marginBottom: 6, fontFamily: "var(--font-mono)" }}>
          FEEDBACK LOOP
        </div>
        <div className="feedback-tray">
          <button className="feedback-btn" onClick={() => handleFeedback("useful", recommendation.interest_detected)}>
            <ThumbsUp size={12} color="#10b981" /> Useful
          </button>
          <button className="feedback-btn" onClick={() => handleFeedback("not_useful", recommendation.interest_detected)}>
            <ThumbsDown size={12} color="#f43f5e" /> Not useful
          </button>
          <button className="feedback-btn" onClick={() => handleFeedback("more_like_this", recommendation.category)}>
            <Flame size={12} color="#f59e0b" /> More
          </button>
          <button className="feedback-btn" onClick={() => handleFeedback("dont_show_topic", recommendation.interest_detected)}>
            <Ban size={12} color="#ef4444" /> Block
          </button>
          <button className="feedback-btn" onClick={() => handleFeedback("prefer_language", "Telugu", "Telugu")}>
            <Globe size={12} color="#00e5ff" /> Regional
          </button>
          <button className="feedback-btn" onClick={() => handleFeedback("more_like_this", "HLD")}>
            <TrendingUp size={12} color="#a855f7" /> HLD
          </button>
        </div>

        {feedbackSuccess && (
          <div style={{ marginTop: 6, fontSize: "0.7rem", color: "#10b981", display: "flex", alignItems: "center", gap: 4 }}>
            <CheckCircle size={12} /> Graph updated
          </div>
        )}
      </div>

      {/* ALT CANDIDATES */}
      {recommendation.ranked_alternatives?.length > 0 && (
        <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
          <div style={{ fontSize: "0.68rem", color: "#64748b", fontWeight: 600, marginBottom: 6, fontFamily: "var(--font-mono)" }}>
            MMR ALTERNATIVES
          </div>
          {recommendation.ranked_alternatives.slice(0, 3).map((alt, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "6px 8px",
                background: "rgba(0,0,0,0.15)",
                borderRadius: 8,
                marginBottom: 4,
                fontSize: "0.78rem"
              }}
            >
              <div>
                <div style={{ fontWeight: 500, color: "#e2e8f0" }}>{alt.title}</div>
                <div style={{ fontSize: "0.65rem", color: "#64748b" }}>{alt.category} · {alt.difficulty}</div>
              </div>
              <span style={{ fontSize: "0.68rem", fontFamily: "var(--font-mono)", color: "#00e5ff" }}>
                {alt.score?.toFixed(2) || "0.75"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ScoreRow({ label, value, color }) {
  return (
    <div className="score-bar-row">
      <span>{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <div className="score-progress-track">
          <div className="score-progress-fill" style={{ width: `${value * 100}%`, background: color }} />
        </div>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.68rem", color: "#94a3b8" }}>{value}</span>
      </div>
    </div>
  );
}
