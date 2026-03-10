import { Bell, Flame, Menu } from "lucide-react";
import { Badge } from "./ui/badge";

interface HeaderProps {
  onMenuClick: () => void;
}

export function DashboardHeader({ onMenuClick }: HeaderProps) {
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
            <span className="text-orange-700 text-sm md:text-base hidden sm:inline">7 Day Streak</span>
            <span className="text-orange-700 text-sm sm:hidden">7d</span>
          </div>
          
        </div>
          {/* Notifications */}
          <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors ml-auto">
            <Bell className="w-5 h-5 text-gray-600" />
            <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-red-500 text-white rounded-full text-xs">
              3
            </Badge>
          </button>
      </div>

      
    </header>
  );
}