/**
 * InterestGraphView.jsx — Full-screen Latent Interest Graph Explorer
 * Displays the exact interest graph for the selected student/person with physics,
 * domain rollups, and inferred top topics.
 */
import React, { useRef, useEffect, useState } from "react";

export default function InterestGraphView({
  graphData,
  currentUser,
  selectedUserId,
  users = [],
  onSelectUser,
  onRefresh
}) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const [zoom, setZoom] = useState(1.0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !graphData?.nodes?.length) return;

    const ctx = canvas.getContext("2d");
    const container = canvas.parentElement;
    let width = (canvas.width = container.clientWidth);
    let height = (canvas.height = container.clientHeight);

    const nodes = graphData.nodes.map((n, i) => {
      const isUser = n.id === "USER";
      const isDomain = n.type === "domain";
      const angle = (i / graphData.nodes.length) * Math.PI * 2;
      const radius = isUser ? 0 : isDomain ? 160 : 280;
      return {
        ...n,
        x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 20,
        y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 20,
        r: n.size || 14
      };
    });

    const links = graphData.links || [];
    let tick = 0;

    const render = () => {
      tick += 0.02;
      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(width / 2, height / 2);
      ctx.scale(zoom, zoom);
      ctx.translate(-width / 2, -height / 2);

      // Links
      links.forEach((l) => {
        const src = nodes.find((n) => n.id === l.source);
        const tgt = nodes.find((n) => n.id === l.target);
        if (src && tgt) {
          ctx.beginPath();
          ctx.moveTo(src.x, src.y);
          ctx.lineTo(tgt.x, tgt.y);
          ctx.strokeStyle =
            l.type === "rollup" ? "rgba(168,85,247,0.22)" : "rgba(0,212,255,0.18)";
          ctx.lineWidth = Math.max(0.6, (l.weight || 0.5) * 2.5);
          ctx.stroke();

          // Flow particle
          const p = (tick * 0.4 + (l.weight || 0)) % 1;
          ctx.beginPath();
          ctx.arc(src.x + (tgt.x - src.x) * p, src.y + (tgt.y - src.y) * p, 2, 0, Math.PI * 2);
          ctx.fillStyle = l.type === "rollup" ? "#a855f7" : "#00d4ff";
          ctx.fill();
        }
      });

      // Nodes
      nodes.forEach((n) => {
        const pulse = Math.sin(tick * 2 + n.r) * 2;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r + pulse + 3, 0, Math.PI * 2);
        ctx.fillStyle = n.color ? `${n.color}15` : "rgba(0,212,255,0.08)";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.color || "#38bdf8";
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = "rgba(255,255,255,0.4)";
        ctx.stroke();

        ctx.fillStyle = "#e2e8f0";
        ctx.font = `500 ${n.type === "user" ? "12px" : "10px"} Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText(n.label, n.x, n.y + n.r + 14);

        if (n.score !== undefined) {
          ctx.fillStyle = "#64748b";
          ctx.font = "9px 'JetBrains Mono', monospace";
          ctx.fillText(`+${n.score}`, n.x, n.y + n.r + 24);
        }
      });

      ctx.restore();
      animRef.current = requestAnimationFrame(render);
    };

    render();
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [graphData, zoom]);

  return (
    <div className="graph-view">
      {/* Top Toolbar with active user indicator and switcher */}
      <div className="graph-toolbar">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span className="graph-toolbar-title" style={{ fontSize: "0.85rem", fontWeight: 600, color: "#ffffff" }}>
            Latent Interest Graph:{" "}
            <span style={{ color: "var(--cyan)" }}>
              {selectedUserId} {currentUser?.persona ? `(${currentUser.persona})` : ""}
            </span>
          </span>
          {onSelectUser && users.length > 0 && (
            <select
              className="user-select"
              value={selectedUserId}
              onChange={(e) => onSelectUser(e.target.value)}
              style={{ fontSize: "0.72rem" }}
            >
              <optgroup label="Trap Benchmark Users">
                <option value="TRAP_JAVA_BACKEND">TRAP: Java Meme to Backend</option>
                <option value="TRAP_MULTILINGUAL">TRAP: Telugu + AI/ML</option>
                <option value="TRAP_ENTERTAINMENT_HEAVY">TRAP: Entertainment to DSA</option>
              </optgroup>
              <optgroup label="Synthetic Personas">
                {users
                  .filter((u) => !u.user_id.startsWith("TRAP_"))
                  .slice(0, 15)
                  .map((u) => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.user_id} — {u.persona} ({u.skill_level})
                    </option>
                  ))}
              </optgroup>
            </select>
          )}
        </div>

        <div className="graph-toolbar-btns">
          <button onClick={() => setZoom((z) => Math.min(1.6, z + 0.1))} title="Zoom In">
            ＋ Zoom In
          </button>
          <button onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))} title="Zoom Out">
            － Zoom Out
          </button>
          <button onClick={onRefresh} title="Recalculate Physics">
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="graph-legend">
        <div>
          <span className="legend-dot" style={{ background: "#38bdf8" }} />
          Student Hub ({selectedUserId})
        </div>
        <div>
          <span className="legend-dot" style={{ background: "#a855f7" }} />
          Latent Domain Rollups
        </div>
        <div>
          <span className="legend-dot" style={{ background: "#22c55e" }} />
          Tech Entities & Tools
        </div>
      </div>

      {/* Main Canvas */}
      <div className="graph-canvas-wrap">
        <canvas ref={canvasRef} />
      </div>

      {/* Inferred Top Latent Interests Footer */}
      {graphData?.top_interests && (
        <div style={{ padding: "8px 16px 12px", display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontFamily: "var(--mono)", fontWeight: 600 }}>
            Inferred Latent Interests for {selectedUserId}:
          </span>
          {graphData.top_interests.map(([topic, score, trend], i) => (
            <span
              key={i}
              style={{
                fontSize: "0.7rem",
                padding: "3px 8px",
                borderRadius: 6,
                background: "rgba(0,212,255,0.08)",
                border: "1px solid rgba(0,212,255,0.2)",
                color: "#7dd3fc",
                fontFamily: "var(--mono)"
              }}
            >
              {topic}: +{score} ({trend})
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
