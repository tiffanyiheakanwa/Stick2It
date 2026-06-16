import { useEffect, useState } from "react";
import { Sidebar as LegacySidebar } from "./components/Sidebar";
import { Header } from "./components/header/Header.tsx";
import { DashboardHeader } from "./components/header/DashboardHeader.tsx";
import { BuddyHeader } from "./components/header/BuddyHeader.tsx";
import { DashboardView } from "./view/dashboard/DashboardView";
import { RemindersView } from "./view/dashboard/RemindersView";
// import { TodayView } from "./view/dashboard/TodayView";
import { AISuggestionsView } from "./view/dashboard/AISuggestionsView";
import { AuthLoginView } from "./view/auth/AuthLoginView";
import { AuthSignupView } from "./view/auth/AuthSignupView";
import { OAuthCallbackView } from "./view/auth/OAuthCallbackView";
import { BuddyView } from "@/view/dashboard/BuddyView";
import { SettingsView } from "./view/dashboard/SettingsView";
import { useTasks } from './context/TaskContext.tsx';
import { Toaster } from "react-hot-toast";

import { VerifyView } from "./view/dashboard/VerifyView";

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

  const [isOAuthCallback] = useState(() => window.location.search.includes('token='));
  const [isVerifyRoute] = useState(() => window.location.pathname.startsWith('/verify/'));

  const [activeSection, setActiveSection] = useState(() => {
    return sessionStorage.getItem('lastSection') || "dashboard";
  });
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    sessionStorage.setItem('lastSection', activeSection);
  }, [activeSection]);

  if (loading) {
    return (
      <div className="text-center ">
    <div role="status">
        <svg aria-hidden="true" className="inline w-10 h-10 text-neutral-tertiary animate-spin fill-purple" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
            <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
        </svg>
        <span className="sr-only">Loading...</span>
    </div>
</div>
    );
  }

  if (isOAuthCallback) {
    return <OAuthCallbackView />;
  }

  if (isVerifyRoute) {
    return <VerifyView />;
  }

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
        return <DashboardView onNavigate={(section) => setActiveSection(section)} />;
      case "buddy":
        return <BuddyView />;
      case "reminders":
        return <RemindersView />;
      // case "today":
      //   return <TodayView />;
      case "ai":
        return <AISuggestionsView />;
      case "settings":
        return <SettingsView />;
      default:
        return <DashboardView onNavigate={(section) => setActiveSection(section)} />;
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-gradient-to-br from-indigo-600 via-indigo-500 to-purple-600">
      <Toaster 
        position="top-right" 
        toastOptions={{
          duration: 5000,
          style: {
            background: '#333',
            color: '#fff',
          },
        }} 
      />
      
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
              <DashboardHeader onMenuClick={() => setSidebarOpen(true)} token={token || ""} onNavigate={(sec) => setActiveSection(sec)} />
            ) : activeSection === "buddy" ? (
              <BuddyHeader onMenuClick={() => setSidebarOpen(true)} token={token || ""} onNavigate={(sec) => setActiveSection(sec)} />
            ) : (
              <Header onMenuClick={() => setSidebarOpen(true)} token={token || ""} onNavigate={(sec) => setActiveSection(sec)} />
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
