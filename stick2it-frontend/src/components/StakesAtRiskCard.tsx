import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Commitment {
  id: number;
  status: string;
  stake_value: number;
}

interface StakesAtRiskProps {
  commitments: Commitment[];
  loading: boolean;
}

export function StakesAtRiskCard({ commitments, loading }: StakesAtRiskProps) {
// Derive dynamic values from the commitments array
const activeCommitments = commitments.filter(c => c.status === "pending");
const activeCommitmentsCount = activeCommitments.length;
const totalAtRiskPoints = activeCommitments.reduce((sum, c) => sum + (c.stake_value || 0), 0);

return (
  <Card className="relative overflow-hidden rounded-xl border border-red-300 bg-red-50 p-5 shadow-md transition-all hover:shadow-lg">
    <div className="flex flex-col gap-2">
      <CardHeader className="flex justify-between items-start">
        <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500">
          Current Stakes at Risk
        </CardTitle>
        {!loading && (
            <span className="flex h-2 w-2">
              <span className="absolute inline-flex h-3 w-3 -mt-0.5 -ml-0.5 animate-ping rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500"></span>
            </span>
          )}
      </CardHeader>

      <CardContent>
        <div className="flex items-baseline gap-1">
          {loading ? (
            // Big skeleton for the main point display
            <Skeleton className="h-10 w-24 bg-red-200/50" />
          ) : (
            <h2 className="text-4xl font-extrabold text-red-600">
              -{totalAtRiskPoints}
            </h2>
          )}
          {!loading && <span className="text-lg font-semibold text-red-600">pts</span>}
        </div>

        <div className="mt-2 text-sm leading-relaxed text-gray-700">
          {loading ? (
            // Multi-line skeleton for the descriptive text
            <div className="space-y-2">
              <Skeleton className="h-4 w-full bg-red-200/30" />
              <Skeleton className="h-4 w-3/4 bg-red-200/30" />
            </div>
          ) : (
            <p>
              You have <span className="font-bold text-gray-900">{activeCommitmentsCount}</span> active {activeCommitmentsCount === 1 ? 'contract' : 'contracts'} locked. 
              Finish {activeCommitmentsCount === 1 ? 'this task' : 'these tasks'} before the deadline to <span className="font-bold text-red-700">lock in</span> your hard-earned points!
            </p>
          )}
        </div>
      </CardContent>
    </div>
  </Card>
  );
};

export default StakesAtRiskCard;
