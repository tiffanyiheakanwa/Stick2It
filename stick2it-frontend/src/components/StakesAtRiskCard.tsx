import React from 'react';

interface StakesAtRiskProps {
  totalAtRiskPoints: number;
  activeCommitmentsCount: number;
}

const StakesAtRiskCard: React.FC<StakesAtRiskProps> = ({ 
  totalAtRiskPoints, 
  activeCommitmentsCount 
}) => {
  // Leverage Loss Aversion: If there's nothing to lose, don't show the threat.
  if (activeCommitmentsCount === 0) return null;

  return (
    <div className="relative overflow-hidden rounded-xl border border-red-300 bg-red-50 p-5 shadow-md transition-all hover:shadow-lg">
      <div className="flex flex-col gap-2">
        <header className="flex justify-between items-start">
          <h5 className="text-xs font-bold uppercase tracking-wider text-gray-500">
            Current Stakes at Risk
          </h5>
          <span className="flex h-2 w-2">
            <span className="absolute inline-flex h-3 w-3 -mt-0.5 -ml-0.5 animate-ping rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500"></span>
          </span>
        </header>

        <div className="flex items-baseline gap-1">
          <h2 className="text-4xl font-extrabold text-red-600">
            -{totalAtRiskPoints}
          </h2>
          <span className="text-lg font-semibold text-red-600">pts</span>
        </div>

        <p className="mt-2 text-sm leading-relaxed text-gray-700">
          You have <span className="font-bold text-gray-900">{activeCommitmentsCount}</span> active {activeCommitmentsCount === 1 ? 'contract' : 'contracts'} locked. 
          Finish {activeCommitmentsCount === 1 ? 'this task' : 'these tasks'} before the deadline to <span className="font-bold text-red-700">lock in</span> your hard-earned points!
        </p>

        {/* Pulsing Urgency Bar */}
        <div className="mt-4 h-2.5 w-full rounded-full bg-red-200">
          <div 
            className="h-full w-full animate-pulse rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"
            style={{ transition: 'width 0.5s ease-in-out' }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default StakesAtRiskCard;