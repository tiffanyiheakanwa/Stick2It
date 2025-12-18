import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const courseData = [
  { name: "Computer Science", progress: 85, color: "#3b82f6" },
  { name: "Mathematics", progress: 70, color: "#10b981" },
  { name: "Physics", progress: 92, color: "#8b5cf6" },
];

const weeklyData = [
  { name: "Completed", value: 68 },
  { name: "Remaining", value: 32 },
];

const COLORS = ["#10b981", "#e5e7eb"];

export function ProgressOverview() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Progress Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-8">
          <div className="w-32 h-32">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={weeklyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={35}
                  outerRadius={55}
                  dataKey="value"
                  startAngle={90}
                  endAngle={-270}
                >
                  {weeklyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center -mt-20">
              <div className="text-gray-900">68%</div>
              <div className="text-gray-500">Weekly</div>
            </div>
          </div>
          
          <div className="flex-1">
            <div className="text-gray-900 mb-2">This Week's Progress</div>
            <p className="text-gray-500 mb-4">
              You've completed 17 out of 25 tasks this week. Great work!
            </p>
            <div className="flex gap-4">
              <div>
                <div className="text-gray-900">17</div>
                <div className="text-gray-500">Completed</div>
              </div>
              <div>
                <div className="text-gray-900">8</div>
                <div className="text-gray-500">Remaining</div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="space-y-4 pt-4 border-t border-gray-200">
          <div className="text-gray-900">Course Progress</div>
          {courseData.map((course) => (
            <div key={course.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">{course.name}</span>
                <span className="text-gray-900">{course.progress}%</span>
              </div>
              <Progress value={course.progress} className="h-2" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
