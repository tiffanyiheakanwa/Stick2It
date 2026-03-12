import { useEffect, useState } from "react";
import { Sidebar as LegacySidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { DashboardHeader } from "./components/DashboardHeader";
import { BuddyHeader } from "./components/BuddyHeader";
import { DashboardView } from "./view/dashboard/DashboardView";
import { RemindersView } from "./view/dashboard/RemindersView";
import { TodayView } from "./view/dashboard/TodayView";
import { UpcomingView } from "./view/dashboard/UpcomingView";
import { AISuggestionsView } from "./view/dashboard/AISuggestionsView";
import { AuthLoginView } from "./view/auth/AuthLoginView";
import { AuthSignupView } from "./view/auth/AuthSignupView";
import { BuddyView } from "@/view/dashboard/BuddyView";

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

export interface Habit {
  id: number;
  name: string;
  streak: number;
  goal: string;
  completed: boolean[];
  color: string;
  bgColor: string;
}

export default function App() {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [token, setToken] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [currentStudent, setCurrentStudent] = useState<{
    id: number;
    name: string;
    email: string;
  } | null>(null);

  const API_BASE_URL = "http://localhost:5000/api/v1";

  useEffect(() => {
    if (!isAuthenticated || !token || !currentStudent) return;

    const studentId = currentStudent.id;

    const fetchDashboardData = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/students/${studentId}/stats`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await response.json();
        
        // Map backend data to your frontend Reminder interface
        if (data.commitments) {
          setReminders(data.commitments.map((c: any) => ({
            id: c.id,
            title: c.content_title || "Unnamed Task",
            time: new Date(c.committed_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),            priority: c.stake_value > 20 ? "High" : "Medium", // Derived priority
            category: c.assignment_id ? "Academic" : "Study",
            completed: c.status === "completed",
            date: c.committed_datetime.split('')[0],
            aiSuggested: false,
            stakeType: c.stake_type,
            stakeValue: c.stake_value,
            buddyName: c.buddy_name,
            status: c.status
          })));
        }
      } catch (error) {
        console.error("Failed to fetch data from backend:", error);
      }
    };

    fetchDashboardData();
  }, [API_BASE_URL, isAuthenticated, token, currentStudent]);

  const toggleReminder = (id: number) => {
    setReminders(
      reminders.map((reminder) =>
        reminder.id === id
          ? { ...reminder, completed: !reminder.completed }
          : reminder
      )
    );
  };

  // const deleteReminder = (id: number) => {
  //   setReminders(reminders.filter((reminder) => reminder.id !== id));
  // };

  const addReminder = async(
    title: string,
    time: string,
    priority: string = "Medium",
    category: string = "Personal"
  ) => {
    try {
    // 1. Prepare the payload for the CommitmentSystem
    // Note: In your backend, 'content_id' or 'assignment_id' is required
    const payload = {
      content_id: 1, // You should ideally pass the actual ID from the UI
      committed_datetime: new Date().toISOString(), 
      type: "start_time" 
    };

    if (!token) {
      console.warn("Cannot create commitment without auth token");
      return;
    }

    const response = await fetch(`${API_BASE_URL}/commitments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Failed to save commitment");

    const savedCommitment = await response.json();

    // 2. Update local state with the returned data from the backend
    const newReminder: Reminder = {
      id: savedCommitment.id || Math.max(...reminders.map((r) => r.id), 0) + 1,
      title: title, // Use the title entered in the UI
      time: time,
      priority,
      category,
      completed: false,
      date: new Date().toISOString().split("T")[0],
      aiSuggested: false,
      status: "pending", // Default status from backend
      stakeValue: savedCommitment.stake_value || 10,
      stakeType: savedCommitment.stake_type || "Points",
    };

    setReminders((prev) => [...prev, newReminder]);
  } catch (error) {
    console.error("Error adding reminder:", error);
    // Optional: Add a toast notification here to inform the user
  }
  };

  const renderContent = () => {
    if (!isAuthenticated) {
      if (authMode === "login") {
        return (
          <AuthLoginView
            onLoginSuccess={({ token, student }) => {
              setToken(token);
              setCurrentStudent(student);
              setIsAuthenticated(true);
              setActiveSection("dashboard");
            }}
            onSwitchToSignup={() => setAuthMode("signup")}
          />
        );
      }

      return (
        <AuthSignupView
          onSignupSuccess={({ token, student }) => {
            setToken(token);
            setCurrentStudent(student);
            setIsAuthenticated(true);
            setActiveSection("dashboard");
          }}
          onSwitchToLogin={() => setAuthMode("login")}
        />
      );
    }
    switch (activeSection) {
      case "dashboard":
        return (
          <DashboardView
            reminders={reminders}
            addReminder={addReminder}
            token={token || ""}
            studentId={currentStudent?.id || 1}
            studentName={currentStudent?.name || ""}
          />
        );
      case "reminders":
        return (
          <RemindersView
            token={token || ""}
            studentId={currentStudent?.id || 1}
          />
        );
      case "today":
        return (
          <TodayView reminders={reminders} toggleReminder={toggleReminder} />
        );
      case "upcoming":
        return <UpcomingView reminders={reminders} />;
      case "ai":
        return <AISuggestionsView addReminder={addReminder} />;
      case "buddy":
        return (
          <BuddyView
            reminders={reminders}
            studentName={currentStudent?.name}
          />
        );
      default:
        return (
          <DashboardView
            reminders={reminders}
            addReminder={addReminder}
            token={token || ""}
            studentId={currentStudent?.id || 1}
            studentName={currentStudent?.name || ""}
          />
        );
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
          onLogout={() => {
            setIsAuthenticated(false);
            setAuthMode("login");
            setSidebarOpen(false);
            setToken(null);
            setCurrentStudent(null);
            setReminders([]);
          }}
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
