/**
 * SectionLoader — compact centered loader used inside any view/section
 * while data is fetching. Replaces per-view skeleton screens.
 */
export function SectionLoader({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 320,
        gap: 20,
        padding: "48px 24px",
      }}
    >
      {/* Triple-ring spinner */}
      <div style={{ position: "relative", width: 72, height: 72 }}>
        {/* Outer slow ring */}
        <div style={{
          position: "absolute", inset: 0,
          borderRadius: "50%",
          border: "2.5px solid transparent",
          borderTopColor: "#6d28d9",
          borderRightColor: "#6d28d9",
          opacity: 0.25,
          animation: "sl-spin-cw 2s linear infinite",
        }} />
        {/* Middle medium ring CCW */}
        <div style={{
          position: "absolute", inset: 8,
          borderRadius: "50%",
          border: "2.5px solid transparent",
          borderTopColor: "#4f46e5",
          borderLeftColor: "#4f46e5",
          opacity: 0.45,
          animation: "sl-spin-ccw 1.4s linear infinite",
        }} />
        {/* Inner fast ring */}
        <div style={{
          position: "absolute", inset: 18,
          borderRadius: "50%",
          border: "3px solid transparent",
          borderTopColor: "#7c3aed",
          borderRightColor: "rgba(124,58,237,0.4)",
          animation: "sl-spin-cw 0.85s linear infinite",
        }} />
        {/* Center dot */}
        <div style={{
          position: "absolute",
          top: "50%", left: "50%",
          transform: "translate(-50%,-50%)",
          width: 10, height: 10,
          borderRadius: "50%",
          background: "linear-gradient(135deg,#6d28d9,#4f46e5)",
          boxShadow: "0 0 10px rgba(109,40,217,0.5)",
          animation: "sl-pulse 1.4s ease-in-out infinite",
        }} />
      </div>

      {/* Label */}
      <p style={{
        margin: 0,
        color: "#6b7280",
        fontSize: 13.5,
        fontWeight: 500,
        letterSpacing: "0.03em",
      }}>
        {label}
      </p>

      {/* Track bar */}
      <div style={{
        width: 120,
        height: 3,
        borderRadius: 9999,
        background: "#e5e7eb",
        overflow: "hidden",
        position: "relative",
      }}>
        <div style={{
          position: "absolute",
          height: "100%",
          width: "40%",
          borderRadius: 9999,
          background: "linear-gradient(90deg,#6d28d9,#4f46e5)",
          animation: "sl-track 1.4s ease-in-out infinite",
        }} />
      </div>

      <style>{`
        @keyframes sl-spin-cw  { to { transform: rotate(360deg);  } }
        @keyframes sl-spin-ccw { to { transform: rotate(-360deg); } }
        @keyframes sl-pulse {
          0%,100% { opacity:0.6; transform:translate(-50%,-50%) scale(1);   }
          50%      { opacity:1;   transform:translate(-50%,-50%) scale(1.3); }
        }
        @keyframes sl-track {
          0%   { left:-40%; }
          60%  { left:100%; }
          100% { left:100%; }
        }
      `}</style>
    </div>
  );
}
