import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { CheckCircle2, Clock, AlertCircle, TrendingUp } from "lucide-react";
import type { Reminder } from "../App";

interface ReminderStatsProps {
  reminders: Reminder[];
}

export function ReminderStats({ reminders }: ReminderStatsProps) {
  const today = new Date().toISOString().split("T")[0];
  const completedToday = reminders.filter(
    (r) => r.date === today && r.completed
  ).length;
  const pendingToday = reminders.filter(
    (r) => r.date === today && !r.completed
  ).length;
  const overdue = reminders.filter(
    (r) => r.date < today && !r.completed
  ).length;
  const completedThisWeek = reminders.filter((r) => r.completed).length;

  const stats = [
    {
      icon: CheckCircle2,
      label: "Completed Today",
      value: completedToday.toString(),
      subtext: "Great progress!",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      icon: Clock,
      label: "Pending",
      value: pendingToday.toString(),
      subtext: "Due today",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      icon: AlertCircle,
      label: "Overdue",
      value: overdue.toString(),
      subtext: overdue > 0 ? "Needs attention" : "All clear!",
      color: "text-red-600",
      bgColor: "bg-red-50",
    },
    {
      icon: TrendingUp,
      label: "Total",
      value: reminders.length.toString(),
      subtext: `${completedThisWeek} completed`,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reminder Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => (
            <div key={stat.label} className={`p-4 rounded-lg ${stat.bgColor}`}>
              <div className="flex items-start justify-between mb-2">
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div className="text-gray-900 mb-1">{stat.value}</div>
              <div className="text-gray-600 mb-1 text-sm">{stat.label}</div>
              <div className="text-gray-500 text-xs">{stat.subtext}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
