import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import { Clock, Sparkles } from "lucide-react";
import type { Reminder } from "../App";

const priorityColors = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  Low: "bg-green-100 text-green-700 border-green-200",
};

interface TaskChecklistProps {
  reminders: Reminder[];
  toggleReminder: (id: number) => void;
}

export function TaskChecklist({ reminders, toggleReminder }: TaskChecklistProps) {
  const today = new Date().toISOString().split('T')[0];
  const todayReminders = reminders.filter(r => r.date === today);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Today's Reminders</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {todayReminders.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No reminders for today. You're all caught up!</p>
        ) : (
          todayReminders.map((reminder) => (
            <div
              key={reminder.id}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Checkbox
                checked={reminder.completed}
                onCheckedChange={() => toggleReminder(reminder.id)}
                className="mt-1"
              />
              <div className="flex-1 min-w-0">
                <div className={`flex items-center gap-2 mb-1 ${reminder.completed ? "line-through text-gray-400" : ""}`}>
                  <span className="text-gray-900">{reminder.title}</span>
                  {reminder.aiSuggested && (
                    <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                  )}
                </div>
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{reminder.time}</span>
                  {reminder.aiSuggested && (
                    <span className="text-purple-600">AI suggested time</span>
                  )}
                </div>
              </div>
              <Badge className={priorityColors[reminder.priority as keyof typeof priorityColors]}>
                {reminder.priority}
              </Badge>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}