import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { DashboardHeader } from "./components/DashboardHeader";
import { DashboardView } from "./view/dashboard/DashboardView";
import { RemindersView } from "./view/dashboard/RemindersView";
import { TodayView } from "./view/dashboard/TodayView";
import { UpcomingView } from "./view/dashboard/UpcomingView";
import { AISuggestionsView } from "./view/dashboard/AISuggestionsView";
import { HabitsView } from "./view/dashboard/HabitsView";

export interface Reminder {
  id: number;
  title: string;
  time: string;
  priority: string;
  category: string;
  completed: boolean;
  date: string;
  aiSuggested: boolean;
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
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [reminders, setReminders] = useState<Reminder[]>([
    {
      id: 1,
      title: "Submit final project report",
      time: "Today, 3:00 PM",
      priority: "High",
      category: "Academic",
      completed: false,
      date: "2024-12-15",
      aiSuggested: false,
    },
    {
      id: 2,
      title: "Review Chapter 5 notes",
      time: "Today, 5:00 PM",
      priority: "Medium",
      category: "Study",
      completed: false,
      date: "2024-12-15",
      aiSuggested: true,
    },
    {
      id: 3,
      title: "Team meeting for group project",
      time: "Tomorrow, 10:00 AM",
      priority: "High",
      category: "Academic",
      completed: false,
      date: "2024-12-16",
      aiSuggested: false,
    },
    {
      id: 4,
      title: "Gym workout",
      time: "Tomorrow, 6:00 PM",
      priority: "Low",
      category: "Personal",
      completed: false,
      date: "2024-12-16",
      aiSuggested: false,
    },
    {
      id: 5,
      title: "Practice coding problems",
      time: "Dec 17, 2:00 PM",
      priority: "Medium",
      category: "Study",
      completed: true,
      date: "2024-12-17",
      aiSuggested: false,
    },
    {
      id: 6,
      title: "Buy groceries",
      time: "Dec 18, 4:00 PM",
      priority: "Low",
      category: "Personal",
      completed: false,
      date: "2024-12-18",
      aiSuggested: false,
    },
  ]);

  const [habits, setHabits] = useState<Habit[]>([
    {
      id: 1,
      name: "Morning Exercise",
      streak: 12,
      goal: "Daily",
      completed: [true, true, false, true, true, true, false],
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      id: 2,
      name: "Study Session",
      streak: 7,
      goal: "Daily",
      completed: [true, true, true, true, true, true, true],
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      id: 3,
      name: "Read for 30 mins",
      streak: 5,
      goal: "Daily",
      completed: [true, false, true, true, true, true, false],
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      id: 4,
      name: "Drink 8 glasses of water",
      streak: 15,
      goal: "Daily",
      completed: [true, true, true, true, true, true, true],
      color: "text-cyan-600",
      bgColor: "bg-cyan-50",
    },
  ]);

  const toggleReminder = (id: number) => {
    setReminders(
      reminders.map((reminder) =>
        reminder.id === id
          ? { ...reminder, completed: !reminder.completed }
          : reminder
      )
    );
  };

  const deleteReminder = (id: number) => {
    setReminders(reminders.filter((reminder) => reminder.id !== id));
  };

  const addReminder = (
    title: string,
    time: string,
    priority: string = "Medium",
    category: string = "Personal"
  ) => {
    const newReminder: Reminder = {
      id: Math.max(...reminders.map((r) => r.id), 0) + 1,
      title,
      time,
      priority,
      category,
      completed: false,
      date: new Date().toISOString().split("T")[0],
      aiSuggested: false,
    };
    setReminders([...reminders, newReminder]);
  };

  const completeHabit = (id: number) => {
    setHabits(
      habits.map((habit) => {
        if (habit.id === id) {
          const newCompleted = [...habit.completed];
          newCompleted[6] = true; // Mark today (Sunday) as complete
          return {
            ...habit,
            completed: newCompleted,
            streak: habit.streak + 1,
          };
        }
        return habit;
      })
    );
  };

  const renderContent = () => {
    switch (activeSection) {
      case "dashboard":
        return (
          <DashboardView
            reminders={reminders}
            toggleReminder={toggleReminder}
            addReminder={addReminder}
          />
        );
      case "reminders":
        return (
          <RemindersView
            reminders={reminders}
            toggleReminder={toggleReminder}
            deleteReminder={deleteReminder}
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
      case "habits":
        return <HabitsView habits={habits} completeHabit={completeHabit} />;
      default:
        return (
          <DashboardView
            reminders={reminders}
            toggleReminder={toggleReminder}
            addReminder={addReminder}
          />
        );
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-gradient-to-br from-indigo-600 via-indigo-500 to-purple-600">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="w-full lg:pl-64">
        <div className="min-h-screen bg-white lg:rounded-tl-3xl">
          {activeSection === "dashboard" ? (
            <DashboardHeader onMenuClick={() => setSidebarOpen(true)} />
          ) : (
            <Header onMenuClick={() => setSidebarOpen(true)} />
          )}

          <main className="px-4 md:px-6 lg:px-8 ">{renderContent()}</main>
        </div>
      </div>
    </div>
  );
}
