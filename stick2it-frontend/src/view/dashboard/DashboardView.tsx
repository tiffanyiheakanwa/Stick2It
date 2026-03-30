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
import StakesAtRiskCard from "@/components/StakesAtRiskCard";
import { StressMeter } from "../../components/ProgressOverview";
import { useState, useEffect } from "react";
import { useTasks } from "../../context/TaskContext"; 
import toast from 'react-hot-toast';


export function DashboardView() {
  const { commitments, token, studentId, currentStudent, nudges, refreshData, addReminder, stressScore } = useTasks();
  const [quickInput, setQuickInput] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [localCommitments, setLocalCommitments] = useState<any[]>([]);

  const handleOpenModal = () => {
    if (quickInput.trim()) {
      setIsModalOpen(true);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      if (!token || !studentId) return;
      try {
        const response = await fetch(`http://localhost:8000/api/v1/students/${studentId}/stats`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.success && data.commitments) {
          setLocalCommitments(data.commitments);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      }
    };
    
    loadData();
  }, [token, studentId]);

  useEffect(() => {
    // Create WebSocket connection
    if (!studentId) return;
    const socket = new WebSocket(`ws://localhost:8000/ws/${studentId}`);

    socket.onopen = () => {
      console.log("Connected to Stick2It Real-time Sync");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "COMMITMENT_UPDATED") {
        console.log(`Buddy marked task as ${data.status}!`);
        refreshData(); 
        loadData(); 

        if (data.status === "completed") {
          toast.success((_t) => (
                  <span>
                      <b>Task Verified!</b> <br />
                      Buddy confirmed you finished your task. +{data.points_gained || 10} points!
                  </span>
              ),
              { duration: 5000, icon: '✅' }
          );
        } else if (data.status === "failed") {
          toast.error(
              "Buddy marked the task as failed. Stake deducted.",
              { duration: 6000, icon: '⚠️' }
          );
        }
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    return () => socket.close();
  }, [studentId, refreshData]);

  // Helper to re-run the specific stats fetch
  const loadData = async () => {
    if (!token || !studentId) return;
    try {
      const response = await fetch(`http://localhost:8000/api/v1/students/${studentId}/stats`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success && data.commitments) {
        setLocalCommitments(data.commitments);
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-0">
        <div className="pl-4 pb-4">
          <h1 className="font-semibold text-xl">Hi, {currentStudent?.name || "Student"}</h1>
          <p className="text-blue-600">Let's finish your task today!</p>
        </div>
        <WelcomeCard reminders={commitments} />
      </div>

      <QuickReminderCreation onAddReminder={addReminder} value={quickInput} onChange={setQuickInput} onOpenModal={handleOpenModal}/>
      
      <CreateCommitmentModal 
        isOpen={isModalOpen} 
        onOpenChange={(open) => {
          setIsModalOpen(open);
          if (!open) {
            refreshData(); // Refresh global tasks when modal closes
            loadData(); // Refresh local stats for StakesAtRiskCard
          }
        }} 
        initialTitle={quickInput} 
        token={token || ""}

      />

      <div className="flex flex-col xl:flex-row gap-5">
        <div className="xl:flex-1 min-w-0">
          <StakesAtRiskCard commitments={localCommitments} />
          <NudgesNotifications externalNudges={nudges}/>
        </div>
        <div className="xl:block min-w-0 ">
        </div>
        <div className="xl:flex-1 min-w-0">
          <StressMeter pFail={stressScore} />
        </div>
      </div>
      <div className="pb-6">
        <SuccessChart/>
      </div>

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
