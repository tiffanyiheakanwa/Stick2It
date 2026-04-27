import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Clock, BookOpen, GraduationCap, AlertCircle } from "lucide-react";
import { useState } from "react";
import { useTasks } from "../../context/TaskContext"; 
import { CreateCommitmentModal } from "../../components/modal/CreateCommitmentModal";
import { Button } from "../../components/ui/button";
import { RemindersSkeleton } from "../../components/dashboard/RemindersSkeleton";

// const priorityColors = {
//   High: "bg-red-100 text-red-700 border-red-200",
//   Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
//   Low: "bg-green-100 text-green-700 border-green-200",
// };


export function RemindersView(){
  const { commitments, loading, token, refreshData, deleteReminder } = useTasks();
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [activeCommitId, setActiveCommitId] = useState<number | null>(null);
  const [activeTitle, setActiveTitle] = useState("");
  const [activeDate, setActiveDate] = useState("");

  const handleActivate = (id: number, title: string, datestr: string) => {
    setActiveCommitId(id);
    setActiveTitle(title);
    setActiveDate(datestr);
    setModalOpen(true);
  };

  const filteredReminders = commitments.filter((c) => {
    if (filter === "active") return c.status === "pending" || c.status === "requires_stake" || c.status === "in_progress";
    if (filter === "completed") return c.status === "kept" || c.status === "completed";
    return true;
  });

  if (loading) return <RemindersSkeleton />;

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
          <Card key={commitment.id} className={commitment.status === 'requires_stake' ? 'border-orange-300 bg-orange-50' : ''}>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className={`flex items-center gap-2 mb-2 ${commitment.status === 'kept' ? "line-through text-gray-400" : ""}`}>
                    {commitment.source_platform === 'google' && <span title="Google Classroom"><BookOpen className="w-5 h-5 text-indigo-600" /></span>}
                    {commitment.source_platform === 'moodle' && <span title="Moodle"><GraduationCap className="w-5 h-5 text-orange-600" /></span>}
                    <span className={`font-medium ${commitment.status === 'requires_stake' ? 'text-orange-900' : 'text-gray-900'}`}>
                        {commitment.title || "Active Commitment"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 mb-3 text-sm">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Deadline: {new Date(commitment.committed_datetime).toLocaleString()}</span>
                  </div>
                  
                  {commitment.status !== 'requires_stake' ? (
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className="bg-indigo-100 text-indigo-700">
                        Stake: {commitment.stake_value} {commitment.stake_type}
                      </Badge>
                      <Badge variant="outline">
                        Buddy: {commitment.buddy_name}
                      </Badge>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-orange-600 text-sm font-semibold">
                      <AlertCircle className="w-4 h-4" />
                      Requires valid stake and buddy to activate!
                    </div>
                  )}
                </div>
                
                <div className="flex flex-col items-end gap-2 shrink-0">
                  <Badge className={
                    commitment.status === 'kept' ? "bg-green-100 text-green-700" : 
                    commitment.status === 'requires_stake' ? "bg-orange-100 text-orange-700 border-orange-200" : 
                    "bg-blue-100 text-blue-700"
                  }>
                    {commitment.status === 'requires_stake' ? 'NEEDS ACTIVATION' : commitment.status.toUpperCase()}
                  </Badge>
                  {commitment.status === 'requires_stake' && (
                    <Button 
                      size="sm" 
                      className="bg-orange-500 hover:bg-orange-600 text-white shadow-sm mt-2 font-bold"
                      onClick={() => handleActivate(commitment.id, commitment.title, commitment.committed_datetime)}
                    >
                      Activate (Set Stake)
                    </Button>
                  )}
                  {commitment.status === 'requires_stake' && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => deleteReminder(commitment.id)} 
                      className="text-red-400 hover:text-red-500 hover:bg-red-50 mt-1 border-red-200"
                      title="Ignore/Delete Task"
                    >
                      Delete
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <CreateCommitmentModal 
        isOpen={modalOpen} 
        onOpenChange={(open) => {
          setModalOpen(open);
          if (!open) {
            setActiveCommitId(null);
            refreshData(); 
          }
        }} 
        initialTitle={activeTitle} 
        initialDate={activeDate}
        activationCommitmentId={activeCommitId}
        token={token || ""}
      />
    </div>
  );
}
