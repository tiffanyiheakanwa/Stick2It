// components/dashboard/DashboardSkeleton.tsx
import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="pl-4 pb-4 space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>

      {/* Welcome Card Skeleton */}
      <Skeleton className="h-40 w-full rounded-xl" />

      {/* Quick Input Skeleton */}
      <Skeleton className="h-12 w-full rounded-lg" />

      {/* Grid for Stakes and Nudges */}
      <div className="flex flex-col xl:flex-row gap-5">
        <div className="xl:flex-1">
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
        <div className="xl:flex-1">
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      </div>

      {/* Success Chart Skeleton */}
      <Skeleton className="h-80 w-full rounded-xl" />
    </div>
  );
}