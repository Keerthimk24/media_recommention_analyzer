/**
 * TrapTester.jsx — Trap Benchmark Lab
 */
import React, { useState, useEffect } from "react";
import { runBenchmarkTraps } from "../services/api";

export default function TrapTester({ onSelectTrapUser }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    try { const res = await runBenchmarkTraps(); setResults(res); }
    catch (err) { console.error("Benchmark failed:", err); }
    finally { setLoading(false); }
  };

  useEffect(() => { handleRun(); }, []);

  return (
    <div className="trap-view">
      <div className="trap-header">
        <h2>
          Trap Benchmark Lab
          {results && (
            <span className={`trap-badge ${results.passed === results.total ? "pass" : ""}`}>
              {results.passed}/{results.total} PASSED
            </span>
          )}
        </h2>
        <button className="trap-run-btn" onClick={handleRun} disabled={loading}>
          {loading ? "Running..." : "▸ Run All"}
        </button>
      </div>

      {results?.results && (
        <div className="trap-grid">
          {Object.entries(results.results).map(([key, trap]) => (
            <div key={key} className={`trap-card ${trap.passed ? "passed" : ""}`}>
              <div className="trap-card-head">
                <span className="trap-name">{key}</span>
                <span style={{ color: trap.passed ? "#4ade80" : "#fb7185" }}>
                  {trap.passed ? "✓" : "✗"}
                </span>
              </div>

              <div className="trap-detail">
                <div><strong>Ground Truth:</strong> {trap.ground_truth}</div>
                <div><strong>Inferred:</strong> <span style={{ color: "#38bdf8" }}>{trap.inferred_interest}</span></div>
                <div><strong>Recommended:</strong> <span style={{ color: "#a855f7" }}>{trap.recommended_title} [{trap.category}]</span></div>
              </div>

              <div>
                <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", fontFamily: "var(--mono)", marginBottom: 3 }}>SPEC OUTPUT:</div>
                <pre className="trap-output">{trap.exact_formatted_output}</pre>
              </div>

              <button className="trap-inspect-btn" onClick={() => onSelectTrapUser(key)}>
                Inspect in Feed →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
