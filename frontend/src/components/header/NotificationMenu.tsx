import { Bell, UserPlus, FileWarning, Check, X } from "lucide-react";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { useTasks } from "../../context/TaskContext";

interface NotificationMenuProps {
  onNavigate?: (section: string) => void;
}

export function NotificationMenu({ onNavigate }: NotificationMenuProps) {
  const { notifications, handleRespond, displayedBadgeCount, markNotificationsViewed } = useTasks();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button 
          onClick={markNotificationsViewed}
          className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Bell className="w-5 h-5 text-gray-600" />
          {displayedBadgeCount > 0 && (
            <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-red-500 text-white rounded-full text-xs">
              {displayedBadgeCount}
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
                    {notif.type === 'sync_alert_requires_stake' ? (
                      <FileWarning className="w-4 h-4 text-orange-600" />
                    ) : (
                      <UserPlus className="w-4 h-4 text-indigo-600" />
                    )}
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
                    ) : notif.type === 'sync_alert_requires_stake' && notif.status === 'unread' ? (
                      <div className="flex gap-2 mt-3">
                        <Button 
                          size="sm" 
                          className="bg-orange-500 hover:bg-orange-600 h-8 text-xs text-white shadow-sm"
                          onClick={() => {
                            if (onNavigate) onNavigate('reminders');
                          }}
                        >
                          Activate Task
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
  );
}
