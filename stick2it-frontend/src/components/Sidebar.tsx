import {
  LayoutDashboard,
  CheckSquare,
  Calendar,
  TrendingUp,
  Award,
  Sparkles,
  LogOut,
  X,
} from "lucide-react";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", id: "dashboard" },
  { icon: CheckSquare, label: "My Reminders", id: "reminders" },
  { icon: Calendar, label: "Today", id: "today" },
  // { icon: TrendingUp, label: "Upcoming", id: "upcoming" },
  { icon: Sparkles, label: "AI Suggestions", id: "ai" },
  // { icon: Award, label: "Habits", id: "habits" },
];

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({
  activeSection,
  onSectionChange,
  isOpen,
  onClose,
}: SidebarProps) {
  const handleSectionChange = (section: string) => {
    onSectionChange(section);
    onClose(); // Close sidebar on mobile after selection
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`w-64 bg-white h-screen fixed left-0 top-0 flex flex-col text-gray-500 z-50 border-r-2 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Close button for mobile */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-indigo-300 rounded-lg lg:hidden"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-600" />
            </div>
            <span className="text-indigo-600">RemindAI</span>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleSectionChange(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  activeSection === item.id
                    ? "bg-white text-indigo-600"
                    : "text-gray-700 hover:bg-indigo-200"
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-6 bg-indigo-500 rounded-xl m-4">
          <div className="flex items-center gap-3 px-2 mb-4">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-indigo-600">
              AS
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-white truncate">Alex Smith</div>
              <div className="text-indigo-200">Student</div>
            </div>
          </div>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-white hover:bg-indigo-500 rounded-lg transition-colors">
            <LogOut className="w-5 h-5" />
            <span>Log Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
