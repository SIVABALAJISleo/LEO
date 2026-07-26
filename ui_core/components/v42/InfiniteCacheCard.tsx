import React, { useEffect, useState } from "react";
import {
  InfiniteCacheEngine,
  InfiniteCacheMetrics,
} from "../../src/v40/engines/infiniteCacheEngine";

const cacheEngine = new InfiniteCacheEngine();

export const InfiniteCacheCard: React.FC = () => {
  const [metrics, setMetrics] = useState<InfiniteCacheMetrics>(cacheEngine.metrics);

  useEffect(() => {
    const interval = setInterval(async () => {
      const data = await cacheEngine.fetchTelemetry();

      // Simulate live traffic for demo
      setMetrics((prev) => {
        const hits = prev.tiers.map((t) => t.hitCount + Math.floor(Math.random() * 5));
        const total = prev.totalRequests + 25;
        const newHitRate = hits.reduce((a, b) => a + b, 0) / total;

        return {
          ...data,
          totalRequests: total,
          overallHitRate: newHitRate,
          estimatedTFlopsSaved: prev.estimatedTFlopsSaved + 35,
          tiers: prev.tiers.map((t, i) => ({ ...t, hitCount: hits[i], hitRate: hits[i] / total })),
        };
      });
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        background: "rgba(20, 25, 30, 0.65)",
        backdropFilter: "blur(16px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "20px",
        padding: "24px",
        color: "#fff",
        fontFamily: '"Inter", sans-serif',
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
        transition: "transform 0.3s ease",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Decorative Glow */}
      <div
        style={{
          position: "absolute",
          top: "-50px",
          left: "-50px",
          width: "150px",
          height: "150px",
          background: "radial-gradient(circle, rgba(0, 210, 255, 0.2) 0%, transparent 70%)",
          filter: "blur(20px)",
          zIndex: 0,
        }}
      ></div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 1,
        }}
      >
        <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 600, letterSpacing: "0.5px" }}>
          Infinite Cache Layer
        </h2>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "0.8rem", color: "#aaa", textTransform: "uppercase" }}>
            Hit Rate
          </span>
          <span style={{ fontSize: "1.2rem", fontWeight: 700, color: "#00d2ff" }}>
            {(metrics.overallHitRate * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px", zIndex: 1 }}>
        {metrics.tiers.map((tier, idx) => {
          const colors = ["#00d2ff", "#3a7bd5", "#8a2387", "#e94057", "#f27121"];
          const barWidth = `${Math.min(100, Math.max(2, tier.hitRate * 100 * 2))}%`; // Scaled for demo

          return (
            <div key={idx} style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <div
                style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}
              >
                <span style={{ color: "#ccc" }}>{tier.tierName}</span>
                <span style={{ fontWeight: 600, color: colors[idx] }}>
                  {tier.hitCount.toLocaleString()} hits
                </span>
              </div>
              <div
                style={{
                  width: "100%",
                  height: "8px",
                  background: "rgba(255,255,255,0.05)",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: barWidth,
                    background: colors[idx],
                    transition: "width 0.5s ease-out",
                    borderRadius: "4px",
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div
        style={{
          background: "rgba(0,0,0,0.3)",
          padding: "16px",
          borderRadius: "12px",
          border: "1px solid rgba(0, 210, 255, 0.2)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 1,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
          <span style={{ fontSize: "0.8rem", color: "#888", textTransform: "uppercase" }}>
            Compute Avoided
          </span>
          <span style={{ fontSize: "1.5rem", fontWeight: 700, color: "#00ff88" }}>
            {metrics.estimatedTFlopsSaved.toLocaleString()}{" "}
            <span style={{ fontSize: "0.9rem", color: "#aaa", fontWeight: 400 }}>TFLOPs</span>
          </span>
        </div>

        {metrics.offlineFallbackActive && (
          <span
            style={{
              fontSize: "0.75rem",
              background: "rgba(255, 170, 0, 0.1)",
              color: "#ffaa00",
              padding: "4px 8px",
              borderRadius: "4px",
              border: "1px solid rgba(255, 170, 0, 0.3)",
            }}
          >
            Offline Fallback Active
          </span>
        )}
      </div>
    </div>
  );
};
