import { Bell, Flame, Search, Mail, Menu } from "lucide-react";
import { Badge } from "./ui/badge";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
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

        {/* Search bar - hidden on mobile */}
        <div className="hidden md:flex items-center gap-4 flex-1">
          <div className="relative max-w-md w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search reminders..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2 md:gap-4 ml-auto">
          {/* Streak - smaller on mobile */}
          <div className="flex items-center gap-1.5 md:gap-2 bg-orange-50 px-2 md:px-4 py-1.5 md:py-2 rounded-full">
            <Flame className="w-4 h-4 md:w-5 md:h-5 text-orange-500" />
            <span className="text-orange-700 text-sm md:text-base hidden sm:inline">7 Day Streak</span>
            <span className="text-orange-700 text-sm sm:hidden">7d</span>
          </div>
          
          {/* Mail - hidden on small mobile */}
          <button className="p-2 hover:bg-gray-100 rounded-lg relative hidden sm:block">
            <Mail className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* Notifications */}
          <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
            <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-red-500 text-white rounded-full text-xs">
              3
            </Badge>
          </button>
        </div>
      </div>

      {/* Mobile search bar */}
      <div className="mt-3 md:hidden">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search reminders..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>
    </header>
  );
}