import { Alert, AlertDescription } from "./ui/alert";
import { AlertCircle, TrendingDown, Lightbulb, Clock, Users, Calendar } from "lucide-react";
import { Button } from "./ui/button";

const nudges = [
  {
    id: 1,
    type: "warning",
    icon: TrendingDown,
    title: "Assignment has been pending for 3 days",
    message: "Your Linear Algebra homework is due in 2 days. Break it into smaller steps?",
    action: "Break it down",
    color: "border-orange-200 bg-orange-50",
    iconColor: "text-orange-600",
  },
  {
    id: 2,
    type: "pattern",
    icon: Users,
    title: "You haven't replied to your study group",
    message: "4 messages in group chat since yesterday. Want a reminder to check in?",
    action: "Remind me",
    color: "border-blue-200 bg-blue-50",
    iconColor: "text-blue-600",
  },
  {
    id: 3,
    type: "suggestion",
    icon: Calendar,
    title: "Lab report due soon",
    message: "You marked this as overdue yesterday. Should I reschedule it or remove it?",
    action: "Reschedule",
    color: "border-purple-200 bg-purple-50",
    iconColor: "text-purple-600",
  },
];

export function NudgesNotifications() {
  return (
    <div className="space-y-3">
      {nudges.map((nudge) => (
        <Alert key={nudge.id} className={nudge.color}>
          <nudge.icon className={`h-4 w-4 ${nudge.iconColor}`} />
          <AlertDescription>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="text-gray-900 mb-1">{nudge.title}</div>
                <p className="text-gray-600">{nudge.message}</p>
              </div>
              <Button variant="outline" size="sm" className="whitespace-nowrap">
                {nudge.action}
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      ))}
    </div>
  );
}