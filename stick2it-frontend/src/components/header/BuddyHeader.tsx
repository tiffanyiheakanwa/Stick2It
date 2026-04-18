import { AddBuddyModal } from "../modal/AddBuddyModal.tsx";
import { useState } from "react";
import { Search, Mail, Menu, PlusCircle } from "lucide-react";
import { NotificationMenu } from "./NotificationMenu.tsx";

interface HeaderProps {
  onMenuClick: () => void;
  token:string;
  onNavigate?: (section: string) => void;
}

export function BuddyHeader({ onMenuClick, token, onNavigate }: HeaderProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

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
              placeholder="Search friends..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2 md:gap-4 ml-auto">
          {/* Add friends - smaller on mobile */}
          <button className="flex items-center gap-1.5 md:gap-2 bg-blue-50 px-2 md:px-4 py-1.5 md:py-2 rounded-full" onClick={()=>setIsModalOpen(true)}>
            <PlusCircle className="w-4 h-4 md:w-5 md:h-5 text-blue-500" />
            <span className="text-blue-700 text-sm md:text-base hidden sm:inline">Add Friend</span>
            <span className="text-blue-700 text-sm sm:hidden">Add</span>
          </button>
          
          <AddBuddyModal isOpen={isModalOpen} 
        onOpenChange={setIsModalOpen} 
        token={token} />

          {/* Mail - hidden on small mobile */}
          <button className="p-2 hover:bg-gray-100 rounded-lg relative hidden sm:block">
            <Mail className="w-5 h-5 text-gray-600" />
          </button>
          
           <NotificationMenu onNavigate={onNavigate} />
        </div>
      </div>

      {/* Mobile search bar */}
      <div className="mt-3 md:hidden">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search friends..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>
    </header>
  );
}
