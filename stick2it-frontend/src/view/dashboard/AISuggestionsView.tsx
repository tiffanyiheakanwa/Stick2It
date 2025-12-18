import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Sparkles, Brain, Lightbulb, TrendingUp, ArrowRight } from "lucide-react";

const recommendations = [
  {
    id: 1,
    icon: Brain,
    type: "optimization",
    title: "Optimize your study schedule",
    description: "Based on your patterns, you're most productive between 2-4 PM. Try scheduling important tasks during this window.",
    action: "Apply Schedule",
  },
  {
    id: 2,
    icon: Lightbulb,
    type: "suggestion",
    title: "Break down large tasks",
    description: "Your project deadline is approaching. I can help break it into smaller, manageable tasks with reminders.",
    action: "Create Tasks",
  },
  {
    id: 3,
    icon: TrendingUp,
    type: "insight",
    title: "Improve completion rate",
    description: "You tend to skip evening tasks. Consider rescheduling them to morning when you're 40% more likely to complete them.",
    action: "Reschedule",
  },
  {
    id: 4,
    icon: Sparkles,
    type: "automation",
    title: "Automate recurring reminders",
    description: "I noticed you create similar reminders weekly. Want me to set up automatic recurring reminders?",
    action: "Set Up Automation",
  },
];

const typeColors = {
  optimization: "border-blue-200",
  suggestion: "border-green-200",
  insight: "border-purple-200",
  automation: "border-orange-200",
};

const iconColors = {
  optimization: "text-blue-600",
  suggestion: "text-green-600",
  insight: "text-purple-600",
  automation: "text-orange-600",
};

interface AISuggestionsViewProps {
  addReminder: (title: string, time: string, priority: string, category: string) => void;
}

export function AISuggestionsView({ addReminder }: AISuggestionsViewProps) {
  const handleActionClick = (rec: typeof recommendations[0]) => {
    if (rec.id === 2) {
      // Break down large tasks
      addReminder("Research project topic", "Tomorrow, 9:00 AM", "High", "Academic");
      addReminder("Create project outline", "Dec 17, 10:00 AM", "High", "Academic");
      addReminder("Draft first section", "Dec 18, 2:00 PM", "Medium", "Academic");
      alert("Created 3 sub-tasks for your project!");
    } else if (rec.id === 4) {
      // Set up automation
      addReminder("Weekly review session", "Every Monday, 9:00 AM", "Medium", "Study");
      alert("Automated recurring reminder created!");
    } else {
      alert(`Applied: ${rec.title}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900 mb-2">AI Suggestions</h2>
        <p className="text-gray-600 text-sm md:text-base">Personalized recommendations to boost your productivity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {recommendations.map((rec) => (
          <Card key={rec.id} className={`border-2 ${typeColors[rec.type as keyof typeof typeColors]}`}>
            <CardContent className="p-4 md:p-6">
              <div className="flex items-start gap-3 md:gap-4 mb-4">
                <div className={`p-2 md:p-3 bg-white rounded-lg ${iconColors[rec.type as keyof typeof iconColors]} flex-shrink-0`}>
                  <rec.icon className="w-5 h-5 md:w-6 md:h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-gray-900 mb-2 text-sm md:text-base">{rec.title}</h3>
                  <p className="text-gray-600 text-sm">{rec.description}</p>
                </div>
              </div>
              <Button 
                onClick={() => handleActionClick(rec)}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm md:text-base"
              >
                {rec.action}
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <CardTitle className="text-base md:text-lg">How AI Suggestions Work</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm md:text-base">
              1
            </div>
            <div>
              <div className="text-gray-900 mb-1 text-sm md:text-base">Pattern Recognition</div>
              <div className="text-gray-600 text-sm">
                I analyze your reminder completion patterns and daily habits
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm md:text-base">
              2
            </div>
            <div>
              <div className="text-gray-900 mb-1 text-sm md:text-base">Smart Scheduling</div>
              <div className="text-gray-600 text-sm">
                I suggest optimal times based on when you're most productive
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm md:text-base">
              3
            </div>
            <div>
              <div className="text-gray-900 mb-1 text-sm md:text-base">Proactive Reminders</div>
              <div className="text-gray-600 text-sm">
                I detect recurring tasks and suggest automation to save you time
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}