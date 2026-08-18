/**
 * frontend/src/App.jsx
 * Clean 3-column dashboard: HISTORY | PRESENT | FUTURE
 */

import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import HistoryPanel from "./components/HistoryPanel";
import PresentPanel from "./components/PresentPanel";
import FuturePanel from "./components/FuturePanel";
import InterestGraphView from "./components/InterestGraphView";
import TrapTester from "./components/TrapTester";
import SupabaseModal from "./components/SupabaseModal";

import {
  fetchUsers,
  fetchUserProfile,
  fetchUserFeed,
  fetchUserGraph,
  getRecommendation,
  recordInteraction,
  submitFeedback,
  getSupabaseStatus
} from "./services/api";

export default function App() {
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState("U000001");
  const [currentUserProfile, setCurrentUserProfile] = useState(null);
  const [feedReels, setFeedReels] = useState([]);
  const [currentReelIndex, setCurrentReelIndex] = useState(0);
  const [recommendation, setRecommendation] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [recLoading, setRecLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("feed");
  const [isSupabaseModalOpen, setIsSupabaseModalOpen] = useState(false);
  const [supabaseStatus, setSupabaseStatus] = useState(null);

  useEffect(() => {
    async function init() {
      try {
        const usersRes = await fetchUsers();
        if (usersRes?.users) setUsers(usersRes.users);
        const statusRes = await getSupabaseStatus();
        setSupabaseStatus(statusRes);
      } catch (err) { console.error("Init failed:", err); }
    }
    init();
  }, []);

  useEffect(() => {
    if (!selectedUserId) return;
    async function loadUserData() {
      try {
        setRecLoading(true);
        const profile = await fetchUserProfile(selectedUserId);
        setCurrentUserProfile(profile);

        const feedRes = await fetchUserFeed(selectedUserId);
        const combined = [...(feedRes.history_reels || []), ...(feedRes.feed_reels || [])];
        setFeedReels(combined);
        setCurrentReelIndex(0);

        const graphRes = await fetchUserGraph(selectedUserId);
        setGraphData(graphRes);

        if (combined.length > 0) {
          const recRes = await getRecommendation(selectedUserId, combined[0].reel_id);
          setRecommendation(recRes);
        }
      } catch (err) { console.error("Error loading user data:", err); }
      finally { setRecLoading(false); }
    }
    loadUserData();
  }, [selectedUserId]);

  const handleReelSelect = async (index) => {
    setCurrentReelIndex(index);
    const targetReel = feedReels[index];
    if (targetReel) {
      try {
        setRecLoading(true);
        const recRes = await getRecommendation(selectedUserId, targetReel.reel_id);
        setRecommendation(recRes);
      } catch (err) { console.error("Rec error:", err); }
      finally { setRecLoading(false); }
    }
  };

  const handleInteract = async (payload) => {
    try {
      await recordInteraction({ user_id: selectedUserId, ...payload });
      const updatedGraph = await fetchUserGraph(selectedUserId);
      setGraphData(updatedGraph);
      const currentReel = feedReels[currentReelIndex];
      if (currentReel) {
        const updatedRec = await getRecommendation(selectedUserId, currentReel.reel_id);
        setRecommendation(updatedRec);
      }
      const updatedProfile = await fetchUserProfile(selectedUserId);
      setCurrentUserProfile(updatedProfile);
    } catch (err) { console.error("Interaction failed:", err); }
  };

  const handleFeedback = async (payload) => {
    try {
      await submitFeedback({ user_id: selectedUserId, ...payload });
      const updatedGraph = await fetchUserGraph(selectedUserId);
      setGraphData(updatedGraph);
      const currentReel = feedReels[currentReelIndex];
      if (currentReel) {
        const updatedRec = await getRecommendation(selectedUserId, currentReel.reel_id);
        setRecommendation(updatedRec);
      }
    } catch (err) { console.error("Feedback failed:", err); }
  };

  const currentReel = feedReels[currentReelIndex] || null;
  const historyReels = feedReels.map((r, i) => ({ ...r, _index: i }));
  const progressionStage = currentUserProfile?.progression_stage || [1, "Basics"];

  return (
    <div className="app" role="application" aria-label="AI Reels Interest Inference & Recommendation System">
      <Header
        users={users}
        selectedUserId={selectedUserId}
        currentUser={currentUserProfile?.user}
        onSelectUser={(uid) => setSelectedUserId(uid)}
        confidence={graphData?.confidence || currentUserProfile?.confidence}
        supabaseStatus={supabaseStatus}
        onOpenSupabaseModal={() => setIsSupabaseModalOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="app-main" id="main-content">
        {activeTab === "feed" && (
          <section className="main-content" aria-label="Reel Timeline, Viewer, and Recommendations" role="tabpanel" id="tabpanel-feed">
            <HistoryPanel
              reels={historyReels}
              activeIndex={currentReelIndex}
              onSelect={handleReelSelect}
            />
            <PresentPanel
              reel={currentReel}
              onInteract={handleInteract}
              recommendation={recommendation}
              loading={recLoading}
            />
            <FuturePanel
              recommendation={recommendation}
              onFeedback={handleFeedback}
              loading={recLoading}
              progressionStage={progressionStage}
            />
          </section>
        )}

        {activeTab === "graph" && (
          <section className="graph-tab-wrap" aria-label="Interactive Latent Interest Graph" role="tabpanel" id="tabpanel-graph">
            <InterestGraphView
              graphData={graphData}
              selectedUserId={selectedUserId}
              currentUser={currentUserProfile?.user}
              users={users}
              onSelectUser={(uid) => setSelectedUserId(uid)}
              onRefresh={async () => {
                const g = await fetchUserGraph(selectedUserId);
                setGraphData(g);
              }}
            />
          </section>
        )}

        {activeTab === "traps" && (
          <section className="traps-tab-wrap" aria-label="Anti-Trap Adversarial Evaluation Benchmark" role="tabpanel" id="tabpanel-traps">
            <TrapTester onSelectTrapUser={(id) => { setSelectedUserId(id); setActiveTab("feed"); }} />
          </section>
        )}
      </main>

      <SupabaseModal
        isOpen={isSupabaseModalOpen}
        onClose={() => setIsSupabaseModalOpen(false)}
        currentStatus={supabaseStatus}
        onStatusUpdated={(s) => setSupabaseStatus(s)}
      />
    </div>
  );
}
