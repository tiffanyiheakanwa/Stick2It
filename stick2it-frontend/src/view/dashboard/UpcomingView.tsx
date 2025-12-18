import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Calendar, Clock, AlertCircle } from "lucide-react";
import type { Reminder } from "../../App";

const priorityColors = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  Low: "bg-green-100 text-green-700 border-green-200",
};

const categoryColors = {
  Academic: "bg-blue-100 text-blue-700 border-blue-200",
  Study: "bg-purple-100 text-purple-700 border-purple-200",
  Personal: "bg-green-100 text-green-700 border-green-200",
  Work: "bg-orange-100 text-orange-700 border-orange-200",
};

interface UpcomingViewProps {
  reminders: Reminder[];
}

export function UpcomingView({ reminders }: UpcomingViewProps) {
  // Group reminders by date
  const groupedReminders = reminders.reduce((acc, reminder) => {
    const date = reminder.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(reminder);
    return acc;
  }, {} as Record<string, Reminder[]>);

  // Convert to array and sort by date
  const upcomingDays = Object.entries(groupedReminders)
    .map(([date, items]) => ({
      date: new Date(date).toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" }),
      items: items.filter(item => !item.completed),
      rawDate: date,
    }))
    .filter(day => day.items.length > 0)
    .sort((a, b) => a.rawDate.localeCompare(b.rawDate));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-gray-900 mb-2">Upcoming Reminders</h2>
          <p className="text-gray-600 text-sm md:text-base">Stay ahead of your schedule</p>
        </div>
        <select className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm md:text-base">
          <option>Next 7 days</option>
          <option>Next 14 days</option>
          <option>Next 30 days</option>
        </select>
      </div>

      <div className="space-y-6">
        {upcomingDays.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-gray-500">
              No upcoming reminders. You're all clear!
            </CardContent>
          </Card>
        ) : (
          upcomingDays.map((day, idx) => (
            <Card key={idx}>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-indigo-600" />
                    <CardTitle>{day.date}</CardTitle>
                  </div>
                  <Badge className="ml-auto w-fit">{day.items.length} reminder{day.items.length !== 1 ? 's' : ''}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {day.items.map((item) => (
                  <div
                    key={item.id}
                    className={`p-4 rounded-lg border ${
                      item.priority === "High"
                        ? "bg-red-50 border-red-200"
                        : "bg-gray-50 border-gray-200"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
                      <div className="flex-1">
                        <div className={`text-gray-900 mb-1 ${item.priority === "High" ? "text-red-700" : ""}`}>
                          {item.title}
                        </div>
                        <div className="flex items-center gap-2 text-gray-500 text-sm">
                          <Clock className="w-4 h-4 flex-shrink-0" />
                          {item.time}
                        </div>
                      </div>
                      {item.priority === "High" && (
                        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className={priorityColors[item.priority as keyof typeof priorityColors]}>
                        {item.priority}
                      </Badge>
                      <Badge className={categoryColors[item.category as keyof typeof categoryColors]}>
                        {item.category}
                      </Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}