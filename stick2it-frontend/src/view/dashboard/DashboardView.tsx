import { WelcomeCard } from "../../components/WelcomeCard";
import { QuickReminderCreation } from "../../components/QuickReminderCreation";
// import { ReminderStats } from "../../components/ReminderStats";
// import { TaskChecklist } from "../../components/TaskChecklist";
// import { CalendarPreview } from "../../components/CalendarPreview";
// import { GamificationPanel } from "../../components/GamificationPanel";
// import { AIRecommendation } from "../../components/AIRecommendation";
import { SuccessChart } from "../../components/SuccessChart";
import { NudgesNotifications } from "../../components/NudgesNotifications";
import type { Reminder } from "../../App";
import StakesAtRiskCard from "@/components/StakesAtRiskCard";

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
      <div className="p-0">
        <div className="pl-4 pb-4">
          <h1 className="font-semibold text-xl">Hi, Tiffany</h1>
          <p className="text-blue-600">Let's finish your task today!</p>
        </div>
        <WelcomeCard reminders={reminders} />
      </div>

      <QuickReminderCreation onAddReminder={addReminder} />

      <div className="flex flex-col xl:flex-row gap-5">
        <div className="xl:flex-1 min-w-0">
          <StakesAtRiskCard totalAtRiskPoints={50} activeCommitmentsCount={1} />
        </div>
        <div className="xl:flex-1 min-w-0">
          <NudgesNotifications />
        </div>
      </div>

      <SuccessChart />

      {/* <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
      </div> */}
    </div>
  );
}
