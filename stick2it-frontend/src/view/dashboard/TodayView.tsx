import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Checkbox } from "../../components/ui/checkbox";
import { Clock, CheckCircle2, AlertCircle, Sparkles } from "lucide-react";
import type { Reminder } from "../../App";

const priorityColors = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  Low: "bg-green-100 text-green-700 border-green-200",
};

interface TodayViewProps {
  reminders: Reminder[];
  toggleReminder: (id: number) => void;
}

export function TodayView({ reminders, toggleReminder }: TodayViewProps) {
  const today = new Date().toISOString().split('T')[0];
  const todayReminders = reminders.filter(r => r.date === today);
  
  const completedCount = todayReminders.filter(t => t.completed).length;
  const totalCount = todayReminders.length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900 mb-2">Today's Tasks</h2>
        <p className="text-gray-600 text-sm md:text-base">
          {completedCount} of {totalCount} tasks completed
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        <Card>
          <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 md:p-3 bg-green-100 rounded-lg">
                <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 text-green-600" />
              </div>
              <div>
                <div className="text-gray-900">{completedCount}</div>
                <div className="text-gray-500 text-sm">Completed</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 md:p-3 bg-blue-100 rounded-lg">
                <Clock className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
              </div>
              <div>
                <div className="text-gray-900">{totalCount - completedCount}</div>
                <div className="text-gray-500 text-sm">Pending</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="sm:col-span-2 lg:col-span-1">
          <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 md:p-3 bg-red-100 rounded-lg">
                <AlertCircle className="w-5 h-5 md:w-6 md:h-6 text-red-600" />
              </div>
              <div>
                <div className="text-gray-900">
                  {todayReminders.filter(t => !t.completed && t.priority === "High").length}
                </div>
                <div className="text-gray-500 text-sm">High Priority</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Task List</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {todayReminders.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No tasks for today. Enjoy your free time!</p>
          ) : (
            todayReminders.map((task) => (
              <div
                key={task.id}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Checkbox
                  checked={task.completed}
                  onCheckedChange={() => toggleReminder(task.id)}
                  className="mt-1 flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className={`flex flex-wrap items-center gap-2 mb-1 ${task.completed ? "line-through text-gray-400" : ""}`}>
                    <span className="text-gray-900">{task.title}</span>
                    {task.aiSuggested && (
                      <Sparkles className="w-3.5 h-3.5 text-purple-500 flex-shrink-0" />
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-gray-500 text-sm">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{task.time}</span>
                    </div>
                    {task.aiSuggested && (
                      <span className="text-purple-600">AI suggested time</span>
                    )}
                  </div>
                </div>
                <Badge className={`${priorityColors[task.priority as keyof typeof priorityColors]} flex-shrink-0`}>
                  {task.priority}
                </Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}