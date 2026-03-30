import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Sparkles, Brain, Lightbulb, TrendingUp, ArrowRight, Loader2 } from "lucide-react";
import { useTasks } from "../../context/TaskContext";
import { useEffect, useState } from "react";


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

export function AISuggestionsView() {
  const { addReminder, studentId, token } = useTasks();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [strategy, setStrategy] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecommendations() {
      if (!studentId || !token) return;
      try {
        const response = await fetch(`http://localhost:8000/api/v1/students/${studentId}/recommendations`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        // Map backend topic to UI types
        const mapped = (data.recommendations || []).map((rec: any) => {
          let type = "optimization";
          let icon = Brain;
          let description = `Estimated time: ${rec.minutes} mins. Great for your current module: ${rec.module}`;
          
          if (rec.topic.includes("Goal")) {
            type = "suggestion"; icon = Lightbulb;
          } else if (rec.topic.includes("Mindset")) {
            type = "insight"; icon = TrendingUp;
          } else if (rec.topic.includes("Focus")) {
            type = "automation"; icon = Sparkles;
          }
          
          return {
            ...rec,
            icon,
            type,
            description,
            action: "Add to Reminders"
          }
        });

        setRecommendations(mapped);
        setStrategy(data.strategy);
      } catch (err) {
        console.error("Failed to fetch recommendations");
      } finally {
        setLoading(false);
      }
    }
    loadRecommendations();
  }, [studentId, token]);

  const handleActionClick = (rec: any) => {
    // Add the AI task to reminders
    addReminder(`Complete Module: ${rec.title}`, "Today", "High");
    alert(`Added "${rec.title}" to your reminders!`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-gray-900 mb-2">AI Suggestions</h2>
        <p className="text-gray-600 text-sm md:text-base">
          {strategy ? `Strategy: ${strategy}` : "Personalized recommendations to boost your productivity"}
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          {recommendations.map((rec) => (
            <Card key={rec.id} className={`border-2 flex flex-col justify-between ${typeColors[rec.type as keyof typeof typeColors]}`}>
              <CardContent className="p-4 md:p-6 flex-1 flex flex-col">
                <div className="flex items-start gap-3 md:gap-4 mb-4">
                  <div className={`p-2 md:p-3 bg-white rounded-lg ${iconColors[rec.type as keyof typeof iconColors]} flex-shrink-0`}>
                    <rec.icon className="w-5 h-5 md:w-6 md:h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-gray-900 mb-2 font-semibold text-sm md:text-base">{rec.title}</h3>
                    <p className="text-gray-600 text-sm">{rec.description}</p>
                  </div>
                </div>
                <div className="mt-auto pt-4">
                  <Button 
                    onClick={() => handleActionClick(rec)}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm md:text-base"
                  >
                    {rec.action}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

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
