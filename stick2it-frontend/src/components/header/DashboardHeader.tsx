
import { Flame, Menu } from "lucide-react";
import { NotificationMenu } from "./NotificationMenu.tsx";
import { useTasks } from "../../context/TaskContext.tsx";

interface HeaderProps {
  onMenuClick: () => void;
  token:string;
  onNavigate?: (section: string) => void;
}

export function DashboardHeader({ onMenuClick, onNavigate }: HeaderProps) {
  const { streak } = useTasks();

  return (
    <header className="bg-white px-4 md:px-8 py-4">
      <div className="flex items-center justify-between gap-4">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
        >
          <Menu className="w-6 h-6 text-gray-600" />
        </button>

        <div className="flex items-center gap-2 md:gap-4">
          {/* Streak - smaller on mobile */}
          <div className="flex items-center gap-1.5 md:gap-2 bg-orange-50 px-2 md:px-4 py-1.5 md:py-2 rounded-full">
            <Flame className="w-4 h-4 md:w-5 md:h-5 text-orange-500" />
            <span className="text-orange-700 text-sm md:text-base hidden sm:inline">{streak} Day Streak</span>
            <span className="text-orange-700 text-sm sm:hidden">{streak}d</span>
          </div>
          
        </div>
                  <NotificationMenu onNavigate={onNavigate} />
      </div>

      
    </header>
  );
}
