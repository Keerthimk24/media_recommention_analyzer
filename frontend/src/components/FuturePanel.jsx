/**
 * FuturePanel.jsx — Right column: WHAT THEY WILL SEE
 * Clear, distinct queue of what tech reels the student will see next.
 * Accessible markup, semantic hierarchy, and interactive pedagogical feedback loop.
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
    <section className="future-col" aria-label="Upcoming Technology Recommendations">
      <div className="col-header">
        <h2 className="col-label future" style={{ margin: 0, fontSize: "0.7rem" }}>
          WHAT THEY WILL SEE (RECOMMENDATIONS)
        </h2>
      </div>

      <div className="future-body">
        {/* Learning Journey Progression Track */}
        <nav className="journey-strip" aria-label="Pedagogical Learning Progression Stages">
          {STAGES.map(([num, name], i) => {
            const isDone = num < currentStageNum;
            const isNow = num === currentStageNum;
            return (
              <React.Fragment key={num}>
                {i > 0 && <span className="journey-arrow" aria-hidden="true">›</span>}
                <span
                  className={`journey-step ${isDone ? "done" : isNow ? "now" : "later"}`}
                  aria-current={isNow ? "step" : undefined}
                  aria-label={`Stage ${num}: ${name} ${isDone ? "(Completed)" : isNow ? "(Current)" : "(Upcoming)"}`}
                >
                  {isDone ? "✓ " : ""}
                  {name}
                </span>
              </React.Fragment>
            );
          })}
        </nav>

        {/* Loading state */}
        {loading || !recommendation ? (
          <div className="rec-card" style={{ padding: 24, textAlign: "center" }} aria-live="polite">
            <div style={{ fontSize: "0.85rem", color: "var(--text-dim)" }}>
              Loading recommended reels...
            </div>
          </div>
        ) : (
          <>
            {/* Primary #1 Recommendation */}
            <article className="rec-card fade-in" aria-label={`Primary Recommendation: ${recommendation.recommended_title}`}>
              <div className="rec-card-header">
                <span className="rec-card-label" style={{ color: "var(--cyan)", fontWeight: 800 }}>
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
                  aria-label={`Confidence: ${recommendation.confidence}`}
                >
                  {recommendation.confidence} Confidence
                </span>
              </div>

              <div className="rec-card-body">
                {/* Title */}
                <h3
                  className="rec-title"
                  style={{
                    fontSize: "1.08rem",
                    fontWeight: 800,
                    color: "#ffffff",
                    marginBottom: 8,
                    lineHeight: 1.35
                  }}
                >
                  {recommendation.recommended_title}
                </h3>

                {/* Category & Difficulty */}
                <div className="rec-meta" style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10 }}>
                  <span className="cat-badge" data-cat={recommendation.category}>{recommendation.category}</span>
                  <span className="diff-badge">{recommendation.difficulty}</span>
                </div>

                {/* Quick Feedback Actions */}
                <div
                  className="feedback-section"
                  role="group"
                  aria-label="Recommendation Feedback Actions"
                  style={{ borderTop: "1px solid var(--glass-border)", paddingTop: 10, marginTop: 10 }}
                >
                  <div className="feedback-row">
                    <button
                      className="fb-btn"
                      aria-label="Mark recommendation as useful"
                      onClick={() => doFeedback("useful", recommendation.interest_detected)}
                    >
                      👍 Useful
                    </button>
                    <button
                      className="fb-btn"
                      aria-label="Mark recommendation as not useful"
                      onClick={() => doFeedback("not_useful", recommendation.interest_detected)}
                    >
                      👎 Not useful
                    </button>
                    <button
                      className="fb-btn"
                      aria-label="Request more reels like this topic"
                      onClick={() => doFeedback("more_like_this", recommendation.category)}
                    >
                      🔥 More of this
                    </button>
                    <button
                      className="fb-btn"
                      aria-label="Block this topic from feed"
                      onClick={() => doFeedback("dont_show_topic", recommendation.interest_detected)}
                    >
                      🚫 Block topic
                    </button>
                  </div>
                  {fbSuccess && (
                    <div style={{ marginTop: 6, fontSize: "0.7rem", color: "#34d399", fontWeight: 700 }} aria-live="polite">
                      ✓ Preferences updated in real-time
                    </div>
                  )}
                </div>
              </div>
            </article>

            {/* Upcoming Queue in Feed (#2, #3, #4, #5) */}
            {recommendation.ranked_alternatives?.length > 0 && (
              <div className="alt-list" style={{ marginTop: 14 }} aria-label="Upcoming Queue in Feed">
                <h4
                  style={{
                    fontSize: "0.7rem",
                    fontFamily: "var(--mono)",
                    color: "var(--text-dim)",
                    textTransform: "uppercase",
                    letterSpacing: "0.6px",
                    marginBottom: 8,
                    fontWeight: 800
                  }}
                >
                  Upcoming Next in Queue
                </h4>
                {recommendation.ranked_alternatives.slice(0, 4).map((alt, i) => (
                  <article
                    key={i}
                    className="alt-item"
                    aria-label={`Queue #${i + 2}: ${alt.title}`}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span
                        className="alt-rank"
                        style={{
                          color: "var(--cyan)",
                          fontFamily: "var(--mono)",
                          fontSize: "0.74rem",
                          fontWeight: 800
                        }}
                      >
                        #{i + 2} Next in Feed
                      </span>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <span className="cat-badge" data-cat={alt.category} style={{ fontSize: "0.64rem", padding: "2px 7px" }}>
                          {alt.category}
                        </span>
                        <span className="diff-badge" style={{ fontSize: "0.66rem" }}>
                          {alt.difficulty}
                        </span>
                      </div>
                    </div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.3 }}>
                      {alt.title}
                    </div>
                    {alt.summary && (
                      <div style={{ fontSize: "0.72rem", color: "var(--text-dim)", marginTop: 2 }}>
                        {alt.summary}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}
