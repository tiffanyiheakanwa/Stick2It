import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, HeartHandshake } from "lucide-react";
import type { Reminder } from "@/App";

interface BuddyViewProps {
  reminders: Reminder[];
  studentName?: string;
}

export function BuddyView({ reminders, studentName }: BuddyViewProps) {
  const atRisk = reminders.filter(
    (r) => !r.completed && r.status === "pending" && (r.stakeValue ?? 0) > 0
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-gray-900 flex items-center gap-2">
            <HeartHandshake className="w-5 h-5 text-pink-500" />
            Accountability Buddy
          </h2>
          <p className="text-sm text-gray-500">
            You&apos;re keeping{" "}
            <span className="font-medium">
              {studentName || "your friend"}
            </span>{" "}
            on track. These are their current at-risk commitments.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              At-Risk Tasks
            </CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            {atRisk.length} at risk
          </Badge>
        </CardHeader>
        <CardContent className="space-y-3">
          {atRisk.length === 0 ? (
            <p className="text-sm text-gray-500">
              No at-risk commitments right now. Great job—you can relax for a
              bit.
            </p>
          ) : (
            atRisk.map((task) => (
              <div
                key={task.id}
                className="flex items-start justify-between gap-3 rounded-lg border border-red-100 bg-red-50 px-3 py-2"
              >
                <div className="min-w-0">
                  <p className="font-medium text-sm text-gray-900 truncate">
                    {task.title}
                  </p>
                  <p className="text-xs text-gray-600">
                    Stake:{" "}
                    <span className="font-semibold">
                      {task.stakeValue ?? 0} {task.stakeType || "points"}
                    </span>
                    {task.buddyName && (
                      <> · Buddy: {task.buddyName}</>
                    )}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Status: <span className="font-medium">{task.status}</span>
                  </p>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}

