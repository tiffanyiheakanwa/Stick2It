import { WelcomeCard } from "../../components/WelcomeCard";
import { QuickReminderCreation } from "../../components/QuickReminderCreation";
import { ReminderStats } from "../../components/ReminderStats";
import { TaskChecklist } from "../../components/TaskChecklist";
import { CalendarPreview } from "../../components/CalendarPreview";
import { GamificationPanel } from "../../components/GamificationPanel";
import { AIRecommendation } from "../../components/AIRecommendation";
import { NudgesNotifications } from "../../components/NudgesNotifications";
import type { Reminder } from "../../App";

interface DashboardViewProps {
  reminders: Reminder[];
  toggleReminder: (id: number) => void;
  addReminder: (title: string, time: string) => void;
}

export function DashboardView({
  reminders,
  toggleReminder,
  addReminder,
}: DashboardViewProps) {
  return (
    <div className="space-y-6">
      <WelcomeCard reminders={reminders} />

      <QuickReminderCreation onAddReminder={addReminder} />

      <NudgesNotifications />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <TaskChecklist
            reminders={reminders}
            toggleReminder={toggleReminder}
          />
          <AIRecommendation />
        </div>

        <div className="space-y-6">
          <ReminderStats reminders={reminders} />
          <GamificationPanel />
          <CalendarPreview />
        </div>
      </div>
    </div>
  );
}
