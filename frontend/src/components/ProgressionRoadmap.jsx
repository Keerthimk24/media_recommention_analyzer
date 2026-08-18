/**
 * frontend/src/components/ProgressionRoadmap.jsx
 * Compact inline learning journey strip.
 */

import React from "react";
import { Check, Zap, ChevronRight } from "lucide-react";

const STAGES = [
  [1, "Basics"],
  [2, "DSA"],
  [3, "Backend"],
  [4, "APIs"],
  [5, "HLD"],
  [6, "Cloud"],
  [7, "Architecture"]
];

export default function ProgressionRoadmap({ currentStageNum, currentStageName, targetCategory }) {
  return (
    <div className="glass-panel roadmap-strip">
      <Zap size={14} color="#00e5ff" style={{ flexShrink: 0 }} />
      <span style={{ fontSize: "0.68rem", color: "#64748b", fontFamily: "var(--font-mono)", flexShrink: 0 }}>
        Journey:
      </span>
      {STAGES.map(([num, name], i) => {
        const isCompleted = num < currentStageNum;
        const isCurrent = num === currentStageNum;
        const isFuture = num > currentStageNum;

        return (
          <React.Fragment key={num}>
            {i > 0 && <span className="roadmap-arrow"><ChevronRight size={10} /></span>}
            <div
              className={`roadmap-stage ${isCompleted ? "completed" : ""} ${isCurrent ? "current" : ""} ${isFuture ? "future" : ""}`}
            >
              {isCompleted && <Check size={10} />}
              {isCurrent && <Zap size={10} />}
              <span>{name}</span>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
}
