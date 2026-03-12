import { WelcomeCard } from "../../components/WelcomeCard";
import { QuickReminderCreation } from "../../components/QuickReminderCreation";
import { CreateCommitmentModal } from "../../components/modal/CreateCommitmentModal";
// import { ReminderStats } from "../../components/ReminderStats";
// import { TaskChecklist } from "../../components/TaskChecklist";
// import { CalendarPreview } from "../../components/CalendarPreview";
// import { GamificationPanel } from "../../components/GamificationPanel";
// import { AIRecommendation } from "../../components/AIRecommendation";
import { SuccessChart } from "../../components/SuccessChart";
import { NudgesNotifications } from "../../components/NudgesNotifications";
import type { Reminder } from "../../App";
import StakesAtRiskCard from "@/components/StakesAtRiskCard";
import { useState, useEffect } from "react";

interface DashboardViewProps {
  reminders: Reminder[];
  addReminder: (title: string, time: string) => void;
  token: string;
  studentId : number;
  studentName: string;
}

export function DashboardView({
  reminders,
  addReminder,
  token,
  studentId,
  studentName,
}: DashboardViewProps) {

  const [quickInput, setQuickInput] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [commitments, setCommitments] = useState<any[]>([]);

  const handleOpenModal = () => {
    if (quickInput.trim()) {
      setIsModalOpen(true);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/v1/students/${studentId}/stats`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.success && data.commitments) {
          console.log("Backend returned commitments:", data.commitments);
          setCommitments(data.commitments); // Ensure this state is passed to the card
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      }
    };
    
    if (token && studentId) {
      loadData();
    }
  }, [token, studentId]);

  return (
    <div className="space-y-6">
      <div className="p-0">
        <div className="pl-4 pb-4">
          <h1 className="font-semibold text-xl">Hi, {studentName}</h1>
          <p className="text-blue-600">Let's finish your task today!</p>
        </div>
        <WelcomeCard reminders={reminders} />
      </div>

      <QuickReminderCreation onAddReminder={addReminder} value={quickInput} onChange={setQuickInput} onOpenModal={handleOpenModal}/>
      
      <CreateCommitmentModal 
        isOpen={isModalOpen} 
        onOpenChange={setIsModalOpen} 
        initialTitle={quickInput} 
        token={token}
      />

      <div className="flex flex-col xl:flex-row gap-5">
        <div className="xl:flex-1 min-w-0">
          <StakesAtRiskCard commitments={commitments} />
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
