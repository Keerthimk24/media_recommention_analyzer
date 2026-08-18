/**
 * frontend/src/components/ReelFeed.jsx
 * Vertical Reels Feed container with clean nav and reel card.
 */

import React from "react";
import ReelCard from "./ReelCard";
import { ChevronUp, ChevronDown } from "lucide-react";

export default function ReelFeed({ feedReels, currentIndex, onIndexChange, onInteract }) {
  const currentReel = feedReels[currentIndex] || feedReels[0];

  const handlePrev = () => {
    if (currentIndex > 0) onIndexChange(currentIndex - 1);
  };

  const handleNext = () => {
    if (currentIndex < feedReels.length - 1) onIndexChange(currentIndex + 1);
  };

  if (!currentReel) {
    return (
      <div className="feed-column glass-panel" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Loading feed...</p>
      </div>
    );
  }

  return (
    <div className="feed-column">
      <div className="feed-nav">
        <span className="feed-nav-label">
          Reel {currentIndex + 1}/{feedReels.length}
        </span>
        <div className="feed-nav-btns">
          <button className="neu-btn" onClick={handlePrev} disabled={currentIndex === 0}>
            <ChevronUp size={14} />
          </button>
          <button className="neu-btn" onClick={handleNext} disabled={currentIndex === feedReels.length - 1}>
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 0 }}>
        <ReelCard reel={currentReel} onInteract={onInteract} onNextReel={handleNext} isActive={true} />
      </div>
    </div>
  );
}
