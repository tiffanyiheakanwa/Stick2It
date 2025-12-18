import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Checkbox } from "../../components/ui/checkbox";
import { Clock, Sparkles, Edit2, Trash2 } from "lucide-react";
import { Button } from "../../components/ui/button";
import { useState } from "react";
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

interface RemindersViewProps {
  reminders: Reminder[];
  toggleReminder: (id: number) => void;
  deleteReminder: (id: number) => void;
}

export function RemindersView({ reminders, toggleReminder, deleteReminder }: RemindersViewProps) {
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  const filteredReminders = reminders.filter((reminder) => {
    if (filter === "active") return !reminder.completed;
    if (filter === "completed") return reminder.completed;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 className="text-gray-900">All Reminders</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "all"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter("active")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "active"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "completed"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredReminders.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-gray-500">
              No reminders found. {filter === "completed" ? "Complete some tasks to see them here!" : "Create a new reminder to get started!"}
            </CardContent>
          </Card>
        ) : (
          filteredReminders.map((reminder) => (
            <Card key={reminder.id}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={reminder.completed}
                    onCheckedChange={() => toggleReminder(reminder.id)}
                    className="mt-1 flex-shrink-0"
                  />
                  <div className="flex-1 min-w-0">
                    <div className={`flex items-center gap-2 mb-2 ${reminder.completed ? "line-through text-gray-400" : ""}`}>
                      <span className="text-gray-900">{reminder.title}</span>
                      {reminder.aiSuggested && (
                        <Sparkles className="w-3.5 h-3.5 text-purple-500 flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-gray-500 mb-3 text-sm">
                      <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>{reminder.time}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className={priorityColors[reminder.priority as keyof typeof priorityColors]}>
                        {reminder.priority}
                      </Badge>
                      <Badge className={categoryColors[reminder.category as keyof typeof categoryColors]}>
                        {reminder.category}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => alert('Edit functionality - In a full app, this would open an edit dialog')}
                    >
                      <Edit2 className="w-4 h-4 text-gray-600" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this reminder?')) {
                          deleteReminder(reminder.id);
                        }
                      }}
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}