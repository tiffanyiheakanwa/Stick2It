import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Clock } from "lucide-react";

const upcomingReminders = [
  {
    id: 1,
    title: "Submit homework",
    time: "Today, 5:00 PM",
    category: "Academic",
    urgent: true,
  },
  {
    id: 2,
    title: "Call Mom",
    time: "Today, 6:30 PM",
    category: "Personal",
    urgent: false,
  },
  {
    id: 3,
    title: "Group study session",
    time: "Tomorrow, 3:00 PM",
    category: "Academic",
    urgent: false,
  },
  {
    id: 4,
    title: "Doctor's appointment",
    time: "Dec 16, 10:00 AM",
    category: "Personal",
    urgent: false,
  },
  {
    id: 5,
    title: "Project presentation",
    time: "Dec 20, 2:00 PM",
    category: "Academic",
    urgent: false,
  },
];

const categoryColors = {
  Academic: "bg-blue-100 text-blue-700",
  Personal: "bg-green-100 text-green-700",
};

export function CalendarPreview() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Upcoming Reminders
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {upcomingReminders.map((item) => (
          <div
            key={item.id}
            className={`p-3 rounded-lg border ${
              item.urgent
                ? "bg-red-50 border-red-200"
                : "bg-gray-50 border-gray-200"
            }`}
          >
            <div className="flex items-start justify-between mb-1">
              <span className={`text-gray-900 ${item.urgent ? "text-red-700" : ""}`}>
                {item.title}
              </span>
              {item.urgent && (
                <span className="text-red-600">Urgent</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">{item.time}</span>
              <span
                className={`px-2 py-0.5 rounded ${
                  categoryColors[item.category as keyof typeof categoryColors]
                }`}
              >
                {item.category}
              </span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}