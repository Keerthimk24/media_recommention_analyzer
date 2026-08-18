/**
 * FuturePanel.jsx — Right column: WHAT THEY WILL SEE
 * Clear, distinct queue of what tech reels the student will see next.
 */
import React, { useState } from "react";

const STAGES = [
  [1, "Basics"],
  [2, "DSA"],
  [3, "Backend"],
  [4, "APIs"],
  [5, "HLD"],
  [6, "Cloud"],
  [7, "Architecture"]
];

export default function FuturePanel({ recommendation, onFeedback, loading, progressionStage }) {
  const [fbSuccess, setFbSuccess] = useState(null);
  const currentStageNum = progressionStage?.[0] || 1;

  const doFeedback = (type, topic, detail = null) => {
    onFeedback({ feedback_type: type, topic_or_category: topic, detail });
    setFbSuccess(type);
    setTimeout(() => setFbSuccess(null), 2000);
  };

  return (
    <div className="future-col">
      <div className="col-header">
        <span className="col-label future">WHAT THEY WILL SEE (RECOMMENDATIONS)</span>
      </div>

      <div className="future-body">
        {/* Learning Journey Progression Track */}
        <div className="journey-strip">
          {STAGES.map(([num, name], i) => (
            <React.Fragment key={num}>
              {i > 0 && <span className="journey-arrow">›</span>}
              <span
                className={`journey-step ${
                  num < currentStageNum ? "done" : num === currentStageNum ? "now" : "later"
                }`}
              >
                {num < currentStageNum ? "✓ " : ""}
                {name}
              </span>
            </React.Fragment>
          ))}
        </div>

        {/* Loading state */}
        {loading || !recommendation ? (
          <div className="rec-card" style={{ padding: 24, textAlign: "center" }}>
            <div style={{ fontSize: "0.85rem", color: "var(--text-dim)" }}>
              Loading recommended reels...
            </div>
          </div>
        ) : (
          <>
            {/* Primary #1 Recommendation */}
            <div className="rec-card fade-in">
              <div className="rec-card-header">
                <span className="rec-card-label" style={{ color: "var(--cyan)", fontWeight: 700 }}>
                  #1 Up Next (Primary Recommendation)
                </span>
                <span
                  className={`conf-badge ${
                    recommendation.confidence === "High"
                      ? "high"
                      : recommendation.confidence === "Medium"
                      ? "medium"
                      : "low"
                  }`}
                >
                  {recommendation.confidence} Confidence
                </span>
              </div>

              <div className="rec-card-body">
                {/* Title */}
                <div
                  className="rec-title"
                  style={{
                    fontSize: "1.05rem",
                    fontWeight: 700,
                    color: "#ffffff",
                    marginBottom: 8,
                    lineHeight: 1.3
                  }}
                >
                  {recommendation.recommended_title}
                </div>

                {/* Category & Difficulty */}
                <div className="rec-meta" style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10 }}>
                  <span className="cat-badge" data-cat={recommendation.category}>{recommendation.category}</span>
                  <span className="diff-badge">{recommendation.difficulty}</span>
                </div>

                {/* Quick Feedback Actions */}
                <div
                  className="feedback-section"
                  style={{ borderTop: "1px solid var(--border)", paddingTop: 10, marginTop: 10 }}
                >
                  <div className="feedback-row">
                    <button className="fb-btn" onClick={() => doFeedback("useful", recommendation.interest_detected)}>
                      👍 Useful
                    </button>
                    <button className="fb-btn" onClick={() => doFeedback("not_useful", recommendation.interest_detected)}>
                      👎 Not useful
                    </button>
                    <button className="fb-btn" onClick={() => doFeedback("more_like_this", recommendation.category)}>
                      🔥 More of this
                    </button>
                    <button className="fb-btn" onClick={() => doFeedback("dont_show_topic", recommendation.interest_detected)}>
                      🚫 Block topic
                    </button>
                  </div>
                  {fbSuccess && (
                    <div style={{ marginTop: 6, fontSize: "0.68rem", color: "#4ade80" }}>
                      ✓ Updated recommendations
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Upcoming Queue in Feed (#2, #3, #4) */}
            {recommendation.ranked_alternatives?.length > 0 && (
              <div className="alt-list" style={{ marginTop: 14 }}>
                <div
                  style={{
                    fontSize: "0.68rem",
                    fontFamily: "var(--mono)",
                    color: "var(--text-dim)",
                    textTransform: "uppercase",
                    letterSpacing: "0.6px",
                    marginBottom: 8,
                    fontWeight: 700
                  }}
                >
                  Upcoming Next in Queue
                </div>
                {recommendation.ranked_alternatives.slice(0, 4).map((alt, i) => (
                  <div
                    key={i}
                    className="alt-item"
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                      padding: "10px 12px",
                      background: "var(--surface)",
                      border: "1px solid var(--border)",
                      borderRadius: 10,
                      marginBottom: 8
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span
                        className="alt-rank"
                        style={{
                          color: "var(--cyan)",
                          fontFamily: "var(--mono)",
                          fontSize: "0.72rem",
                          fontWeight: 700
                        }}
                      >
                        #{i + 2} Next in Feed
                      </span>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <span className="cat-badge" data-cat={alt.category} style={{ fontSize: "0.62rem", padding: "1px 6px" }}>
                          {alt.category}
                        </span>
                        <span className="diff-badge" style={{ fontSize: "0.62rem" }}>
                          {alt.difficulty}
                        </span>
                      </div>
                    </div>
                    <div
                      className="alt-title"
                      style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.3 }}
                    >
                      {alt.title}
                    </div>
                    {alt.summary && (
                      <div
                        style={{
                          fontSize: "0.72rem",
                          color: "var(--text-dim)",
                          lineHeight: 1.4,
                          marginTop: 2
                        }}
                      >
                        {alt.summary}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
