import { AddBuddyModal } from "./modal/AddBuddyModal";
import { useState, useEffect } from "react";
import { Bell, Search, Mail, Menu, UserPlus, Check, X, PlusCircle } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";

interface HeaderProps {
  onMenuClick: () => void;
  token:string;
}

export function BuddyHeader({ onMenuClick, token }: HeaderProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const unreadCount = notifications.filter(n => n.status === 'unread').length;

  const fetchNotifications = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/v1/notifications", {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success) setNotifications(data.notifications);
    } catch (err) {
      console.error("Failed to fetch notifications");
    }
  };

  useEffect(() => {
    if (token) fetchNotifications();
  }, [token]);

  const handleRespond = async (id: number, action: 'accept' | 'refuse') => {
    try {
      const response = await fetch(`http://localhost:5000/api/v1/notifications/${id}/respond`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`, 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ action })
      });
      if (response.ok) fetchNotifications();
    } catch (err) {
      console.error("Error responding to request");
    }
  };

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
          
           {/* Notifications Popover */}
           <Popover>
            <PopoverTrigger asChild>
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell className="w-5 h-5 text-gray-600" />
                {unreadCount > 0 && (
                  <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-red-500 text-white rounded-full text-xs">
                    {unreadCount}
                  </Badge>
                )}
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0" align="end">
              <div className="p-4 border-b font-semibold">Notifications</div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-gray-400 text-sm">No new notifications</div>
                ) : (
                  notifications.map((notif) => (
                    <div key={notif.id} className="p-4 border-b last:border-0 hover:bg-gray-50 transition-colors">
                      <div className="flex gap-3">
                        <div className="bg-indigo-100 p-2 rounded-full h-fit">
                          <UserPlus className="w-4 h-4 text-indigo-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-gray-800">{notif.message}</p>
                          {notif.type === 'buddy_request' && notif.status === 'unread' ? (
                            <div className="flex gap-2 mt-3">
                              <Button 
                                size="sm" 
                                className="bg-indigo-600 h-8 text-xs"
                                onClick={() => handleRespond(notif.id, 'accept')}
                              >
                                <Check className="w-3 h-3 mr-1" /> Accept
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                className="h-8 text-xs"
                                onClick={() => handleRespond(notif.id, 'refuse')}
                              >
                                <X className="w-3 h-3 mr-1" /> Refuse
                              </Button>
                            </div>
                          ) : (
                            <span className="text-xs text-gray-400 capitalize mt-1 block">
                              {notif.status}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </PopoverContent>
          </Popover>
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