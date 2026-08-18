/**
 * frontend/src/components/SupabaseModal.jsx
 * Modal for configuring live Supabase Cloud URL and Anon Key.
 */

import React, { useState } from "react";
import { configureSupabase } from "../services/api";
import { Database, CheckCircle, XCircle, X, Link, Key, Shield } from "lucide-react";

export default function SupabaseModal({ isOpen, onClose, currentStatus, onStatusUpdated }) {
  const [url, setUrl] = useState(currentStatus?.supabase_url || "");
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await configureSupabase(url, key);
      setResult(res);
      if (res.connected) {
        onStatusUpdated(res);
      }
    } catch (err) {
      setResult({ connected: false, error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card glass-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Database size={24} color="#10b981" />
            <h2 style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              Supabase Cloud Database Sync
            </h2>
          </div>
          <button className="neu-btn" onClick={onClose} style={{ padding: "6px" }}>
            <X size={16} />
          </button>
        </div>

        <p style={{ fontSize: "0.85rem", color: "#94a3b8", marginBottom: "20px" }}>
          Connect your live Supabase project to persist student interaction streams, evolving latent graph weights, and interactive feedback loops.
        </p>

        {/* Form */}
        <form onSubmit={handleSave}>
          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#cbd5e1", marginBottom: "6px", fontFamily: "var(--font-mono)" }}>
              <Link size={14} style={{ display: "inline", marginRight: "6px" }} />
              Supabase Project URL:
            </label>
            <input
              type="url"
              placeholder="https://your-project.supabase.co"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "#080b14",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                color: "#ffffff",
                fontFamily: "var(--font-mono)",
                fontSize: "0.85rem",
                outline: "none"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", fontSize: "0.8rem", color: "#cbd5e1", marginBottom: "6px", fontFamily: "var(--font-mono)" }}>
              <Key size={14} style={{ display: "inline", marginRight: "6px" }} />
              Supabase Anon / Service Role Key:
            </label>
            <input
              type="password"
              placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              value={key}
              onChange={(e) => setKey(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "#080b14",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                color: "#ffffff",
                fontFamily: "var(--font-mono)",
                fontSize: "0.85rem",
                outline: "none"
              }}
            />
          </div>

          {result && (
            <div
              style={{
                marginBottom: "16px",
                padding: "12px",
                borderRadius: "10px",
                background: result.connected ? "rgba(16, 185, 129, 0.1)" : "rgba(244, 63, 94, 0.1)",
                border: `1px solid ${result.connected ? "rgba(16, 185, 129, 0.3)" : "rgba(244, 63, 94, 0.3)"}`,
                color: result.connected ? "#34d399" : "#fb7185",
                fontSize: "0.82rem",
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              {result.connected ? <CheckCircle size={16} /> : <XCircle size={16} />}
              <span>{result.message || result.error || "Connection tested."}</span>
            </div>
          )}

          <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
            <button type="button" className="neu-btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="neu-btn neu-btn-primary" disabled={loading}>
              {loading ? "Connecting..." : "Connect Supabase"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
