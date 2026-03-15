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
  status: string;          
  stakeType?: string;      
  stakeValue?: number;    
  buddyName?: string;    
  failureProbability?: number; 
  riskCategory?: 'Low' | 'Medium' | 'High' | 'Critical'; 
}

export default function App() {
  const { 
    token, 
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

  useEffect(() => {
    sessionStorage.setItem('lastSection', activeSection);
  }, [activeSection]);

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
        return <DashboardView />;
      case "buddy":
        return <BuddyView />;
      case "reminders":
        return <RemindersView />;
      case "today":
        return <TodayView />;
      case "ai":
        return <AISuggestionsView />;
      default:
        return <DashboardView />;
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
