import { useEffect, useState } from "react";
import { Sidebar as LegacySidebar } from "./components/Sidebar";
import { Header } from "./components/header/Header.tsx";
import { DashboardHeader } from "./components/header/DashboardHeader.tsx";
import { BuddyHeader } from "./components/header/BuddyHeader.tsx";
import { DashboardView } from "./view/dashboard/DashboardView";
import { RemindersView } from "./view/dashboard/RemindersView";
import { TodayView } from "./view/dashboard/TodayView";
import { AISuggestionsView } from "./view/dashboard/AISuggestionsView";
import { AuthLoginView } from "./view/auth/AuthLoginView";
import { AuthSignupView } from "./view/auth/AuthSignupView";
import { BuddyView } from "@/view/dashboard/BuddyView";
import { useTasks } from './context/TaskContext.tsx';

export interface Reminder {
  id: number;
  title: string;
  time: string;
  priority: string;
  category: string;
  completed: boolean;
  date: string;
  aiSuggested: boolean;
  // New fields to match the Commitment class
  stakeType?: string;      // From stake_type
  stakeValue?: number;     // From stake_value
  buddyName?: string;      // From buddy_name
  status: string;          // To track 'pending', 'completed', or 'broken'
}

export default function App() {
  const { 
    token, 
    studentId, 
    isAuthenticated, 
    currentStudent, 
    login, 
    logout,
    loading
  } = useTasks();

  const [activeSection, setActiveSection] = useState(() => {
    return sessionStorage.getItem('lastSection') || "dashboard";
  });
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  

  const API_BASE_URL = "http://localhost:5000/api/v1";

  useEffect(() => {
    sessionStorage.setItem('lastSection', activeSection);
  }, [activeSection]);

  // 1. Define toggleReminder at the top level so renderContent can see it
  const toggleReminder = (id: number) => {
    setReminders(prev =>
      prev.map((r) => r.id === id ? { ...r, completed: !r.completed } : r)
    );
  };

  // 2. Define addReminder at the top level
  const addReminder = async (title: string, time: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/commitments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          committed_datetime: new Date().toISOString(),
          stake_value: 10
        }),
      });

      if (!response.ok) throw new Error("Failed to save");
      const saved = await response.json();

      setReminders(prev => [...prev, {
        id: saved.id,
        title,
        time,
        priority: "Medium",
        category: "Personal",
        completed: false,
        date: new Date().toISOString().split("T")[0],
        aiSuggested: false,
        status: "pending"
      }]);
    } catch (error) {
      console.error("Error adding reminder:", error);
    }
  };

  // 3. Keep useEffect ONLY for fetching the initial list
  useEffect(() => {
    if (!isAuthenticated || !token || !studentId) return;

    const fetchDashboardData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/students/${studentId}/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (data.commitments) {
          setReminders(data.commitments.map((c: any) => ({
            id: c.id,
            title: c.custom_title || "Unnamed Task",
            time: new Date(c.committed_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            priority: "Medium",
            category: "Study",
            completed: c.status === "completed",
            date: c.committed_datetime.split('T')[0],
            aiSuggested: false,
            status: c.status
          })));
        }
      } catch (error) { console.error(error); }
    };

    fetchDashboardData();
  }, [isAuthenticated, token, studentId]);

  if (loading) return <div className="h-screen w-screen flex items-center justify-center bg-indigo-600 text-white">Loading...</div>;

  const renderContent = () => {
    if (!isAuthenticated) {
      return authMode === "login" ? (
        <AuthLoginView
          onLoginSuccess={({ token, student }) => {
            login(token, student); 
            setActiveSection("dashboard");
          }}
          onSwitchToSignup={() => setAuthMode("signup")}
        />
      ) : (
        <AuthSignupView
          onSignupSuccess={({ token, student }) => {
            login(token, student);
            setActiveSection("dashboard");
          }}
          onSwitchToLogin={() => setAuthMode("login")}
        />
      );
    }

    switch (activeSection) {
      case "dashboard":
        return <DashboardView addReminder={addReminder} />;
      case "buddy":
        return <BuddyView />;
      case "reminders":
        return <RemindersView />;
      case "today":
        return <TodayView reminders={reminders} toggleReminder={toggleReminder} />;
      case "ai":
        return <AISuggestionsView addReminder={addReminder} />;
      default:
        return <DashboardView addReminder={addReminder} />;
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-gradient-to-br from-indigo-600 via-indigo-500 to-purple-600">
      {isAuthenticated && (
        <LegacySidebar
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          currentStudent={currentStudent}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onLogout={logout}
        />
      )}

      {isAuthenticated ? (
        <div className="w-full lg:pl-64">
          <div className="min-h-screen bg-white lg:rounded-tl-3xl">
            {activeSection === "dashboard" ? (
              <DashboardHeader onMenuClick={() => setSidebarOpen(true)} token={token || ""} />
            ) : activeSection === "buddy" ? (
              <BuddyHeader onMenuClick={() => setSidebarOpen(true)} token={token || ""}/>
            ) : (
              <Header onMenuClick={() => setSidebarOpen(true)} token={token || ""}/>
            )}

            <main className="px-4 md:px-6 lg:px-8 ">{renderContent()}</main>
          </div>
        </div>
      ) : (
        <main className="w-full">{renderContent()}</main>
      )}
    </div>
  );
}
