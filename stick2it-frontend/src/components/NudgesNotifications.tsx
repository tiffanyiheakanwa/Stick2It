import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { TrendingDown, Users, Calendar, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Combined Nudges Component: 
 * Handles both standard behavioral suggestions and AI-driven Loss Aversion alerts.
 */
export function NudgesNotifications({ externalNudges = [] }: { externalNudges?: any[] }) {
  
  // Default static nudges for UI consistency
  const defaultNudges = [
    {
      id: "d1",
      type: "warning",
      icon: TrendingDown,
      title: "Assignment has been pending for 3 days",
      message: "Your Linear Algebra homework is due in 2 days. Break it into smaller steps?",
      action: "Break it down",
      color: "border-orange-200 bg-orange-50",
      iconColor: "text-orange-600",
    },
    {
      id: "d2",
      type: "pattern",
      icon: Users,
      title: "Study Group Check-in",
      message: "4 messages in group chat since yesterday. Want a reminder to check in?",
      action: "Remind me",
      color: "border-blue-200 bg-blue-50",
      iconColor: "text-blue-600",
    }
  ];

  // Combine static defaults with real-time AI nudges from the backend
  const allNudges = [...externalNudges, ...defaultNudges];

  return (
    <div className="space-y-3">
      {allNudges.map((nudge) => {
        // Special case for AI-driven Loss Aversion Nudges (High Priority)
        if (nudge.type === "AI_DYNAMIC_RISK" || nudge.type === "STREAK_PROTECTION") {
          return (
            <Alert key={nudge.id} variant="destructive" className="border-2 border-red-500 bg-red-50">
              <Zap className="h-4 w-4 text-red-600" />
              <div className="flex-1 ml-2">
                <AlertTitle className="font-bold text-red-700">Loss Aversion Warning!</AlertTitle>
                <AlertDescription>
                  <p className="text-gray-900 mb-2">{nudge.message}</p>
                  <div className="p-2 bg-white rounded border border-red-200">
                    <p className="text-sm font-bold text-red-700">
                      ⚠️ CONSEQUENCE: You are about to lose {nudge.stakeValue || 10} {nudge.stakeType || 'Points'} 
                      and an alert will be sent to {nudge.buddyName || 'your partner'}!
                    </p>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <Button variant="destructive" size="sm">Start Task Now</Button>
                    <Button variant="outline" size="sm">Dismiss</Button>
                  </div>
                </AlertDescription>
              </div>
            </Alert>
          );
        }

        // Standard UI for low-priority suggestions
        const Icon = nudge.icon || Calendar;
        return (
          <Alert key={nudge.id} className={nudge.color}>
            <Icon className={`h-4 w-4 ${nudge.iconColor}`} />
            <AlertDescription>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 ml-2">
                  <div className="font-semibold text-gray-900 mb-1">{nudge.title}</div>
                  <p className="text-gray-600 text-sm">{nudge.message}</p>
                </div>
                <Button variant="outline" size="sm" className="whitespace-nowrap">
                  {nudge.action}
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        );
      })}
    </div>
  );
}