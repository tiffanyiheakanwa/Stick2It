import { Card, CardContent } from "./ui/card";
import { Plus, Clock, Calendar, Zap, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { useState } from "react";

const quickActions = [
  { icon: Clock, label: "In 1 hour", color: "text-blue-600", bgColor: "bg-blue-50", time: "In 1 hour" },
  { icon: Calendar, label: "Tomorrow", color: "text-green-600", bgColor: "bg-green-50", time: "Tomorrow, 9:00 AM" },
  { icon: Zap, label: "This evening", color: "text-purple-600", bgColor: "bg-purple-50", time: "Today, 6:00 PM" },
];

interface QuickReminderCreationProps {
  onAddReminder: (title: string, time: string) => Promise<void>;
  value: string;
  onChange: (value: string) => void;
  onOpenModal: () => void;
}

export function QuickReminderCreation({ onAddReminder, value, onChange, onOpenModal }: QuickReminderCreationProps) {
  const [isSaving, setIsSaving] = useState(false);

  // Unified Save Logic
  const processAdd = async (time: string = "Later today") => {
    // 1. Validation: Prevent empty tasks
    if (!value.trim()) return;

    setIsSaving(true);
    try {
      await onAddReminder(value, time);
      // 2. The parent should handle clearing the 'value' prop, 
      // but we ensure validation passes first.
    } catch (err) {
      console.error("Failed to add", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-4 md:p-6">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-4">
          <input
            type="text"
            placeholder="What are you commiting to?"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && processAdd()}
            disabled={isSaving}
            className="flex-1 px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <Button 
            onClick={onOpenModal}
            disabled={isSaving || !value.trim()} // Validation: Disable if empty
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 w-full sm:w-auto"
          >
            {isSaving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5 mr-2" />}
            {isSaving ? "Saving..." : "Add"}
          </Button>
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-gray-500 text-sm">Quick set:</span>
          {quickActions.map((action) => (
            <button
              key={action.label}
              disabled={isSaving || !value.trim()}
              onClick={() => processAdd(action.time)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${action.bgColor} hover:opacity-80 transition-opacity text-sm`}
            >
              <action.icon className={`w-4 h-4 ${action.color}`} />
              <span className={action.color}>{action.label}</span>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}