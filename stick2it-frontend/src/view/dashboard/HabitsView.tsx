import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Flame, TrendingUp, Target, Award, Calendar, Check } from "lucide-react";
import { Button } from "../../components/ui/button";
import type { Habit } from "../../App";

const achievements = [
  { icon: Flame, title: "7 Day Streak", description: "Completed tasks for 7 days straight", color: "text-orange-600", bgColor: "bg-orange-50" },
  { icon: Target, title: "100 Tasks", description: "Completed 100 tasks total", color: "text-blue-600", bgColor: "bg-blue-50" },
  { icon: Award, title: "Early Bird", description: "Completed morning tasks consistently", color: "text-yellow-600", bgColor: "bg-yellow-50" },
  { icon: TrendingUp, title: "Productivity Pro", description: "Maintained 90% completion rate", color: "text-green-600", bgColor: "bg-green-50" },
];

const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

interface HabitsViewProps {
  habits: Habit[];
  completeHabit: (id: number) => void;
}

export function HabitsView({ habits, completeHabit }: HabitsViewProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900 mb-2">Habits & Streaks</h2>
        <p className="text-gray-600 text-sm md:text-base">Build consistency and track your progress</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Current Streaks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {habits.map((habit) => (
              <div key={habit.id} className={`p-3 md:p-4 rounded-lg ${habit.bgColor}`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div>
                    <div className={`text-gray-900 mb-1 text-sm md:text-base`}>{habit.name}</div>
                    <div className="flex items-center gap-2">
                      <Flame className={`w-4 h-4 ${habit.color}`} />
                      <span className={`${habit.color} text-sm`}>{habit.streak} day streak</span>
                    </div>
                  </div>
                  <Button 
                    onClick={() => {
                      completeHabit(habit.id);
                      alert(`Great job! ${habit.name} marked as complete for today!`);
                    }}
                    disabled={habit.completed[6]}
                    className={`w-full sm:w-auto text-sm md:text-base ${
                      habit.completed[6] 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : 'bg-indigo-600 hover:bg-indigo-700'
                    } text-white`}
                  >
                    <Check className="w-4 h-4 mr-2" />
                    {habit.completed[6] ? 'Completed!' : 'Mark Complete'}
                  </Button>
                </div>
                <div className="flex items-center gap-1 md:gap-2 overflow-x-auto pb-1">
                  {weekDays.map((day, idx) => (
                    <div key={idx} className="flex-1 min-w-[40px] md:min-w-0 text-center">
                      <div className="text-gray-500 mb-1 text-xs md:text-sm">{day}</div>
                      <div
                        className={`w-full h-8 md:h-10 rounded ${
                          habit.completed[idx]
                            ? "bg-indigo-600"
                            : "bg-gray-200"
                        }`}
                      ></div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Achievements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              {achievements.map((achievement, idx) => (
                <div key={idx} className={`p-3 md:p-4 rounded-lg ${achievement.bgColor} border-2 border-transparent hover:border-indigo-300 transition-colors cursor-pointer`}>
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-white rounded-lg flex-shrink-0">
                      <achievement.icon className={`w-5 h-5 md:w-6 md:h-6 ${achievement.color}`} />
                    </div>
                    <div className="min-w-0">
                      <div className="text-gray-900 mb-1 text-sm md:text-base">{achievement.title}</div>
                      <div className="text-gray-600 text-xs md:text-sm">{achievement.description}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Weekly Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600 text-sm md:text-base">Completion Rate</span>
                    <span className="text-gray-900">89%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 md:h-3">
                    <div className="bg-green-600 h-2 md:h-3 rounded-full" style={{ width: "89%" }}></div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 md:gap-4 pt-4">
                  <div className="text-center p-3 md:p-4 bg-blue-50 rounded-lg">
                    <div className="text-gray-900 mb-1">32</div>
                    <div className="text-gray-600 text-xs md:text-sm">Tasks this week</div>
                  </div>
                  <div className="text-center p-3 md:p-4 bg-green-50 rounded-lg">
                    <div className="text-gray-900 mb-1">+8</div>
                    <div className="text-gray-600 text-xs md:text-sm">vs last week</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Motivation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-3 md:p-4 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Flame className="w-5 h-5 md:w-6 md:h-6" />
                  <span className="text-white text-sm md:text-base">Keep it going!</span>
                </div>
                <p className="text-white/90 text-xs md:text-sm">
                  You're on a 7-day streak. Just 3 more days to reach your personal best!
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-gray-600 text-sm">
                  <Calendar className="w-4 h-4 flex-shrink-0" />
                  <span>Current streak: 7 days</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600 text-sm">
                  <Target className="w-4 h-4 flex-shrink-0" />
                  <span>Personal best: 10 days</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}