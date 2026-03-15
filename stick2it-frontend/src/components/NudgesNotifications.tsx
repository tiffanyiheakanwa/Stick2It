import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Calendar, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useTasks } from "../context/TaskContext";

/**
 * Combined Nudges Component: 
 * Handles both standard behavioral suggestions and AI-driven Loss Aversion alerts.
 */
export function NudgesNotifications({ externalNudges = [] }: { externalNudges?: any[] }) {
  const { loading, startTask } = useTasks();
  // // Default static nudges for UI consistency
  // const defaultNudges = [
  //   {
  //     id: "d1",
  //     type: "warning",
  //     icon: TrendingDown,
  //     title: "Assignment has been pending for 3 days",
  //     message: "Your Linear Algebra homework is due in 2 days. Break it into smaller steps?",
  //     action: "Break it down",
  //     color: "border-orange-200 bg-orange-50",
  //     iconColor: "text-orange-600",
  //   },
  //   {
  //     id: "d2",
  //     type: "pattern",
  //     icon: Users,
  //     title: "Study Group Check-in",
  //     message: "4 messages in group chat since yesterday. Want a reminder to check in?",
  //     action: "Remind me",
  //     color: "border-blue-200 bg-blue-50",
  //     iconColor: "text-blue-600",
  //   }
  // ];

  // // Combine static defaults with real-time AI nudges from the backend
  // const allNudges = [...externalNudges, ...defaultNudges];
  if (loading) {
    return (
      <div className="space-y-3 p-4 border rounded-xl bg-white shadow-sm">
        <Skeleton className="h-6 w-48 mb-4" /> {/* Title Skeleton */}
        <div className="flex gap-3 items-center">
          <Skeleton className="h-12 w-12 rounded-full" /> {/* Icon Skeleton */}
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </div>
    );
  }

  const getUrgencyStyles = (pFail: number) => {
    if (pFail >= 0.9) return "border-red-600 bg-red-100 animate-pulse border-4"; // Critical
    if (pFail >= 0.75) return "border-red-400 bg-red-50"; // High Risk
    return "border-orange-300 bg-orange-50"; // Warning
  };

  const getUrgencyText = (pFail: number) => {
    if (pFail >= 0.9) return "CRITICAL RISK";
    if (pFail >= 0.75) return "HIGH RISK";
    return "MODERATE RISK";
  };

  return (
    <div className="space-y-3">
      {externalNudges.length === 0 && (
        <p className="text-sm text-gray-500 italic text-center py-4">
          No urgent risks detected. Keep sticking to it!
        </p>
      )}

      {externalNudges.map((nudge) => {
        if (nudge.type === "AI_DYNAMIC_RISK" || nudge.type === "STREAK_PROTECTION") {
          const urgencyClass = getUrgencyStyles(nudge.p_fail || 0.6);
          const urgencyLabel = getUrgencyText(nudge.p_fail || 0.6);

          return (
            <Alert key={nudge.id} className={`transition-all duration-500 ${urgencyClass}`}>
              <Zap className={`h-4 w-4 ${nudge.p_fail > 0.8 ? "text-red-600" : "text-orange-600"}`} />
              <div className="flex-1 ml-2">
                <AlertTitle className="font-black flex justify-between">
                  <span>LOSS AVERSION ALERT!</span>
                  <span className="text-xs">{urgencyLabel} ({Math.round(nudge.p_fail * 100)}%)</span>
                </AlertTitle>
                <AlertDescription>
                  <p className="text-gray-900 mb-2">{nudge.message}</p>
                  <div className="p-2 bg-white/50 rounded border border-black/10">
                    <p className="text-sm font-bold text-red-700">
                      ⚠️ STAKE: Lose {nudge.stakeValue} {nudge.stakeType} & notify {nudge.buddyName}!
                    </p>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button 
                    variant="destructive" 
                    size="sm" 
                    onClick={() => {
                      const rawId = nudge.assignment_id || nudge.id;
                      const cleanId = typeof rawId === 'string' 
                        ? parseInt(rawId.replace(/^\D+/g, ''), 10) 
                        : rawId;
                  
                      if (!isNaN(cleanId)) {
                        startTask(cleanId);
                      }
                    }}
                    className="font-bold">Start Now</Button>
                    <Button variant="ghost" size="sm">Review Plan</Button>
                  </div>
                </AlertDescription>
              </div>
            </Alert>
          );
        }

        // Standard UI for other nudges...
        return <StandardNudge key={nudge.id} nudge={nudge} />;
      })}
    </div>
  );
}

function StandardNudge({ nudge }: { nudge: any }) {
  const Icon = nudge.icon || Calendar;
  
  return (
    <Alert key={nudge.id} className={nudge.color || "border-blue-200 bg-blue-50"}>
      <Icon className={`h-4 w-4 ${nudge.iconColor || "text-blue-600"}`} />
      <AlertDescription>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 ml-2">
            <div className="font-semibold text-gray-900 mb-1">{nudge.title}</div>
            <p className="text-gray-600 text-sm">{nudge.message}</p>
          </div>
          {nudge.action && (
            <Button variant="outline" size="sm" className="whitespace-nowrap">
              {nudge.action}
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}