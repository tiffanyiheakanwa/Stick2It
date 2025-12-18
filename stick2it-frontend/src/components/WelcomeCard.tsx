import { Card, CardContent } from "./ui/card";
import { Sparkles } from "lucide-react";
import type { Reminder } from "../App";

interface WelcomeCardProps {
  reminders: Reminder[];
}

export function WelcomeCard({ reminders }: WelcomeCardProps) {
  const motivationMessages = [
    "I'm here to help you stay on track. Let's tackle your reminders together!",
    "Small steps lead to big accomplishments. What's on your mind today?",
    "You've got this! I'll keep you organized and focused.",
  ];
  
  const today = new Date();
  const dayOfWeek = today.toLocaleDateString('en-US', { weekday: 'long' });
  const todayString = today.toISOString().split('T')[0];
  const todayReminders = reminders.filter(r => r.date === todayString && !r.completed);
  const message = motivationMessages[Math.floor(Math.random() * motivationMessages.length)];
  
  return (
    <Card className="bg-gradient-to-br from-blue-500 to-green-400 border-0 text-white">
      <CardContent className="p-4 md:p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="text-blue-100 mb-1 text-sm md:text-base">Happy {dayOfWeek}!</div>
            <h2 className="text-white mb-2 md:mb-3">You have {todayReminders.length} reminder{todayReminders.length !== 1 ? 's' : ''} today</h2>
            <p className="text-blue-50 flex items-center gap-2 text-sm md:text-base">
              <Sparkles className="w-4 h-4 flex-shrink-0" />
              <span>{message}</span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}