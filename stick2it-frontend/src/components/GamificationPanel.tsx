import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Flame, TrendingUp } from "lucide-react";

export function GamificationPanel() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 rounded-lg bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-white rounded-lg">
              <Flame className="w-6 h-6 text-orange-500" />
            </div>
            <div>
              <div className="text-gray-900">7 Day Streak</div>
              <div className="text-gray-600">Keep it going!</div>
            </div>
          </div>
          <p className="text-gray-600">
            You've completed at least one task every day this week. Amazing!
          </p>
        </div>
        
        <div className="p-4 rounded-lg bg-gradient-to-br from-green-50 to-blue-50 border border-green-200">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-white rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <div className="text-gray-900">32 tasks this week</div>
              <div className="text-gray-600">+8 from last week</div>
            </div>
          </div>
          <p className="text-gray-600">
            You're on a roll! Keep up the momentum.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}