import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Clock } from "lucide-react";
import { useState } from "react";
import { useTasks } from "../../context/TaskContext"; 

// const priorityColors = {
//   High: "bg-red-100 text-red-700 border-red-200",
//   Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
//   Low: "bg-green-100 text-green-700 border-green-200",
// };


export function RemindersView(){
  const { commitments, loading } = useTasks();
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  const filteredReminders = commitments.filter((c) => {
    if (filter === "active") return c.status === "pending";
    if (filter === "completed") return c.status === "kept" || c.status === "completed";
    return true;
  });

  if (loading) return <div className="p-8 text-center text-indigo-600 animate-pulse">Loading your commitments...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 className="text-gray-900">All Reminders</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "all"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter("active")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "active"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-3 md:px-4 py-2 rounded-lg text-sm md:text-base ${
              filter === "completed"
                ? "bg-indigo-600 text-white"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredReminders.map((commitment) => (
          <Card key={commitment.id}>
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className={`flex items-center gap-2 mb-2 ${commitment.status === 'kept' ? "line-through text-gray-400" : ""}`}>
                    {/* Backend commitments use penalty_message or title if you updated the model */}
                    <span className="text-gray-900 font-medium">
                        {commitment.penalty_message?.split(" if ")[1]?.split(" is ")[0] || "Active Commitment"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 mb-3 text-sm">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Deadline: {new Date(commitment.committed_datetime).toLocaleString()}</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge className="bg-indigo-100 text-indigo-700">
                      Stake: {commitment.stake_value} {commitment.stake_type}
                    </Badge>
                    <Badge variant="outline">
                      Buddy: {commitment.buddy_name}
                    </Badge>
                  </div>
                </div>
                <Badge className={commitment.status === 'kept' ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}>
                  {commitment.status.toUpperCase()}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}