import { useEffect, useState } from "react";

const TIPS = [
  "Analyzing your procrastination patterns…",
  "Calculating your risk profile…",
  "Loading your commitments…",
  "Syncing your accountability data…",
  "Getting your nudges ready…",
];

export function AppLoader() {
  const [tipIndex, setTipIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setTipIndex((i) => (i + 1) % TIPS.length);
        setFade(true);
      }, 300);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #4f46e5 0%, #6d28d9 50%, #7c3aed 100%)",
        zIndex: 9999,
        gap: 0,
      }}
    >
      {/* Ambient glow blobs */}
      <div style={{
        position: "absolute", top: "15%", left: "20%",
        width: 300, height: 300, borderRadius: "50%",
        background: "rgba(167,139,250,0.18)",
        filter: "blur(60px)", pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: "20%", right: "15%",
        width: 260, height: 260, borderRadius: "50%",
        background: "rgba(99,102,241,0.22)",
        filter: "blur(50px)", pointerEvents: "none",
      }} />

      {/* Animated concentric rings */}
      <div style={{ position: "relative", width: 140, height: 140, marginBottom: 36 }}>
        {/* Outermost ring */}
        <div style={{
          position: "absolute", inset: 0,
          borderRadius: "50%",
          border: "2px solid rgba(255,255,255,0.12)",
          animation: "s2i-ring-ping 2.4s cubic-bezier(0,0,0.2,1) infinite",
        }} />
        {/* Middle ring */}
        <div style={{
          position: "absolute", inset: 16,
          borderRadius: "50%",
          border: "2px solid rgba(255,255,255,0.18)",
          animation: "s2i-ring-ping 2.4s cubic-bezier(0,0,0.2,1) 0.4s infinite",
        }} />
        {/* Inner ring (static border + spin arc) */}
        <div style={{
          position: "absolute", inset: 32,
          borderRadius: "50%",
          border: "3px solid rgba(255,255,255,0.15)",
          borderTopColor: "rgba(255,255,255,0.85)",
          borderRightColor: "rgba(255,255,255,0.55)",
          animation: "s2i-spin 1s linear infinite",
        }} />
        {/* Icon center circle */}
        <div style={{
          position: "absolute", inset: 44,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.12)",
          backdropFilter: "blur(8px)",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 0 24px rgba(167,139,250,0.4)",
        }}>
          {/* Stick2It brand "S" mark */}
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path
              d="M20 8C20 8 17.5 6 14 6C9.58 6 6 9.58 6 14C6 18.42 9.58 22 14 22C18.42 22 22 18.42 22 14"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              fill="none"
            />
            <circle cx="14" cy="14" r="2.5" fill="white" />
            <path d="M18 10L22 6M22 6H18M22 6V10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>

      {/* Brand name */}
      <div style={{
        color: "white",
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: "-0.5px",
        marginBottom: 6,
        textShadow: "0 2px 12px rgba(0,0,0,0.2)",
      }}>
        Stick<span style={{ color: "rgba(196,181,253,1)" }}>2</span>It
      </div>

      <div style={{
        color: "rgba(255,255,255,0.6)",
        fontSize: 13,
        fontWeight: 500,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        marginBottom: 32,
      }}>
        Accountability Platform
      </div>

      {/* Tip text */}
      <div style={{
        color: "rgba(255,255,255,0.75)",
        fontSize: 14,
        maxWidth: 280,
        textAlign: "center",
        height: 20,
        transition: "opacity 0.3s ease",
        opacity: fade ? 1 : 0,
        marginBottom: 28,
      }}>
        {TIPS[tipIndex]}
      </div>

      {/* Pulsing dots */}
      <div style={{ display: "flex", gap: 8 }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.9)",
              animation: `s2i-bounce 1.2s ease-in-out ${i * 0.18}s infinite`,
            }}
          />
        ))}
      </div>

      {/* Keyframe styles injected inline */}
      <style>{`
        @keyframes s2i-spin {
          to { transform: rotate(360deg); }
        }
        @keyframes s2i-ring-ping {
          0%   { transform: scale(1);   opacity: 0.6; }
          60%  { transform: scale(1.15); opacity: 0.2; }
          100% { transform: scale(1.25); opacity: 0; }
        }
        @keyframes s2i-bounce {
          0%, 80%, 100% { transform: translateY(0);   opacity: 0.5; }
          40%            { transform: translateY(-8px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
