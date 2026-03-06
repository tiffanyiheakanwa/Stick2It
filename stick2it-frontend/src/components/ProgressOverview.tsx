interface StressMeterProps {
  pFail: number; // 0.0 – 1.0
}

export const StressMeter = ({ pFail }: StressMeterProps) => {
  const percentage = Math.round(pFail * 100);

  // Convert value to rotation (-90deg to 90deg)
  const rotation = -90 + pFail * 180;

  const getLabel = () => {
    if (pFail < 0.4) return "Low Risk";
    if (pFail < 0.75) return "Moderate Risk";
    return "High Risk";
  };

  return (
    <div className="p-6 border rounded-lg bg-card shadow-sm flex flex-col items-center">
      <h3 className="text-sm font-semibold text-muted-foreground mb-4">
        AI Risk Assessment (P-Fail)
      </h3>

      <div className="relative w-80 h-32">
        {/* Gauge background */}
        <svg viewBox="0 0 200 100" className="w-full h-full">
          {/* Green */}
          <path
            d="M10 100 A90 90 0 0 1 70 20"
            stroke="#22c55e"
            strokeWidth="30"
            fill="none"
          />

          {/* Yellow */}
          <path
            d="M70 20 A90 90 0 0 1 130 20"
            stroke="#eab308"
            strokeWidth="30"
            fill="none"
          />

          {/* Red */}
          <path
            d="M130 20 A90 90 0 0 1 190 100"
            stroke="#ef4444"
            strokeWidth="30"
            fill="none"
          />
        </svg>

        {/* Needle */}
        <div
          className="absolute bottom-0 left-1/2 origin-bottom transition-transform duration-500"
          style={{ transform: `rotate(${rotation}deg)` }}
        >
          <div className="w-1 h-20 bg-black rounded"></div>
        </div>

        {/* Center pivot */}
        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-black rounded-full"></div>
      </div>

      <div className="mt-4 text-center">
        <p className="font-bold text-lg">{percentage}%</p>
        <p className="text-sm text-muted-foreground">{getLabel()}</p>
      </div>
    </div>
  );
};
