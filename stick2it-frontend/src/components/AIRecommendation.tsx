import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Sparkles, ArrowRight, Clock, Brain, TrendingUp } from "lucide-react";
import { Button } from "./ui/button";

const recommendations = [
  {
    id: 1,
    title: "Perfect time to work on your assignment",
    description: "Based on your habits, you're most productive between 4-6 PM. Want me to schedule a focus block?",
    action: "Schedule now",
    icon: Clock,
  },
  {
    id: 2,
    title: "Break down: CS Project Presentation",
    description: "This is a big task due in 7 days. I can help you split it into smaller, manageable reminders.",
    action: "Break it down",
    icon: Brain,
  },
  {
    id: 3,
    title: "You usually call home on Fridays",
    description: "It's been 2 weeks since you last called. Want to set a reminder for this Friday at 6 PM?",
    action: "Set reminder",
    icon: Sparkles,
  },
  {
    id: 4,
    title: "Grocery reminder pattern detected",
    description: "You typically shop on Saturdays. Should I create a recurring reminder?",
    action: "Make it recurring",
    icon: TrendingUp,
  },
];

export function AIRecommendation() {
  return (
    <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          AI Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recommendations.map((rec) => (
          <div key={rec.id} className="bg-white p-4 rounded-lg border border-purple-100">
            <div className="flex items-start gap-3 mb-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <rec.icon className="w-4 h-4 text-purple-600" />
              </div>
              <div className="flex-1">
                <div className="text-gray-900 mb-1">{rec.title}</div>
                <p className="text-gray-600 mb-3">{rec.description}</p>
                <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                  {rec.action}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}