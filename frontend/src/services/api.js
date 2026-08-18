/**
 * frontend/src/services/api.js
 * API client to interact with the FastAPI recommender backend.
 */

const API_BASE = "http://localhost:8000/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchUsers() {
  const res = await fetch(`${API_BASE}/users?limit=50`);
  return res.json();
}

export async function fetchUserProfile(userId) {
  const res = await fetch(`${API_BASE}/users/${userId}`);
  return res.json();
}

export async function fetchUserGraph(userId) {
  const res = await fetch(`${API_BASE}/users/${userId}/graph`);
  return res.json();
}

export async function fetchUserFeed(userId) {
  const res = await fetch(`${API_BASE}/users/${userId}/feed?limit=25`);
  return res.json();
}

export async function recordInteraction(payload) {
  const res = await fetch(`${API_BASE}/interact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function getRecommendation(userId, currentReelId) {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, current_reel_id: currentReelId })
  });
  return res.json();
}

export async function submitFeedback(payload) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function runBenchmarkTraps() {
  const res = await fetch(`${API_BASE}/benchmark/traps`);
  return res.json();
}

export async function fetchTaxonomyStages() {
  const res = await fetch(`${API_BASE}/taxonomy/stages`);
  return res.json();
}

export async function configureSupabase(url, key) {
  const res = await fetch(`${API_BASE}/supabase/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ supabase_url: url, supabase_key: key })
  });
  return res.json();
}

export async function getSupabaseStatus() {
  const res = await fetch(`${API_BASE}/supabase/status`);
  return res.json();
}
