import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Sparkles, Brain, Loader2, ListPlus } from "lucide-react";
import { useTasks } from "../../context/TaskContext";
import { useState } from "react";
import { Checkbox } from "../../components/ui/checkbox";
import toast from "react-hot-toast";
import { AISuggestionsSkeleton } from "../../components/dashboard/AISuggestionsSkeleton";

export function AISuggestionsView() {
  const { addReminder, token, commitments, loading } = useTasks();
  
  const [breakdownLoading, setBreakdownLoading] = useState<Record<number, boolean>>({});
  const [taskBreakdowns, setTaskBreakdowns] = useState<Record<number, any[]>>({});
  const [selectedSubtasks, setSelectedSubtasks] = useState<Record<number, Set<string>>>({});

  // Show only pending, in_progress, or requires_stake tasks (not awaiting_verification, failed, etc.)
  const activeTasks = commitments.filter(c => 
    (c.status === 'pending' || c.status === 'in_progress' || c.status === 'requires_stake') && 
    c.stake_type !== 'AI_Subtask'
  );

  if (loading) return <AISuggestionsSkeleton />;

  const handleBreakdownTask = async (task: any) => {
    if (!token) return;
    setBreakdownLoading(prev => ({ ...prev, [task.id]: true }));
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ai/breakdown`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: task.title, description: task.description || "" })
      });
      
      const data = await response.json();
      if (data.success && data.subtasks) {
        setTaskBreakdowns(prev => ({ ...prev, [task.id]: data.subtasks }));
        
        // Auto-select all by default
        const allTitles = new Set<string>(data.subtasks.map((st: any) => st.title as string));
        setSelectedSubtasks(prev => ({ ...prev, [task.id]: allTitles }));
      } else {
        toast.error("Failed to generate breakdown.");
      }
    } catch (err) {
      console.error(err);
      toast.error("Error connecting to AI service.");
    } finally {
      setBreakdownLoading(prev => ({ ...prev, [task.id]: false }));
    }
  };

  const toggleSubtaskSelection = (taskId: number, subtaskTitle: string) => {
    setSelectedSubtasks(prev => {
      const selected = new Set<string>(prev[taskId] || []);
      if (selected.has(subtaskTitle)) {
        selected.delete(subtaskTitle);
      } else {
        selected.add(subtaskTitle);
      }
      return { ...prev, [taskId]: selected };
    });
  };

  const submitSubtasks = async (taskId: number) => {
    const selected = selectedSubtasks[taskId];
    if (!selected || selected.size === 0) return;

    for (const title of Array.from(selected)) {
      await addReminder(title, "Today", "High", true);
    }
    toast.success(`Added ${selected.size} subtasks to your reminders!`);
    
    // Phase 5 Feedback Loop
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/v1/interactions`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action_type: "task_breakdown_accepted" })
      });
    } catch (e) {
      console.error("Failed to log interaction", e);
    }
    
    // Clear out UI
    setTaskBreakdowns(prev => {
        const next = { ...prev };
        delete next[taskId];
        return next;
    });
  };

  // We are keeping only the Task Breakdown section as requested
  return (
    <div className="space-y-8">
      {/* SECTION: TASK BREAKDOWN */}
      <div>
        <div className="mb-4 text-gray-900 border-b pb-2 border-gray-200">
           <h2 className="flex items-center gap-2"><Sparkles className="w-5 h-5 text-indigo-600" /> AI Task Breakdown</h2>
           <p className="text-gray-600 text-sm">Got a huge task? Let Gemini slice it into manageable steps.</p>
        </div>
        
        {activeTasks.length === 0 ? (
           <p className="text-sm text-gray-400">No active tasks to break down right now. Create a reminder first!</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
             {activeTasks.map(task => (
                <Card key={`tk-${task.id}`} className="border-2 flex flex-col justify-between border-indigo-200 shadow-sm relative overflow-hidden">
                   {/* Background Gradient for aesthetic */}
                   <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/30 to-white pointer-events-none" />
                   
                   <CardContent className="p-4 md:p-6 flex-1 flex flex-col relative z-10">
                      <div className="flex items-start gap-3 md:gap-4 mb-4">
                         <div className="p-2 md:p-3 bg-white border border-indigo-100 rounded-lg text-indigo-600 flex-shrink-0 shadow-sm">
                            <ListPlus className="w-5 h-5 md:w-6 md:h-6" />
                         </div>
                         <div className="flex-1 min-w-0">
                            <h3 className="text-gray-900 mb-2 font-semibold text-sm md:text-base leading-tight">{task.title}</h3>
                            <p className="text-gray-600 text-sm capitalize">Status: {task.status.replace('_', ' ')}</p>
                         </div>
                      </div>

                      <div className="mt-auto pt-4 flex flex-col">
                         {!taskBreakdowns[task.id] && (
                             <Button 
                                onClick={() => handleBreakdownTask(task)}
                                disabled={breakdownLoading[task.id]}
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm md:text-base shadow-sm transition-all"
                             >
                                {breakdownLoading[task.id] ? <Loader2 className="w-4 h-4 mr-2 animate-spin"/> : <Brain className="w-4 h-4 mr-2"/>}
                                {breakdownLoading[task.id] ? "Thinking..." : "Break Down w/ AI"}
                             </Button>
                         )}

                         {/* Display breakdown if generated */}
                         {taskBreakdowns[task.id] && (
                            <div className="mt-2 border-t border-indigo-100 pt-4">
                               <h4 className="text-sm font-semibold text-indigo-700 mb-3 flex items-center gap-2">
                                  <Sparkles className="w-4 h-4"/> Suggested Action Plan
                               </h4>
                               <div className="space-y-2 mb-4">
                                   {taskBreakdowns[task.id].map((st: any, idx: number) => {
                                       const isSelected = selectedSubtasks[task.id]?.has(st.title);
                                       return (
                                           <div key={idx} className="flex items-start gap-3 p-2.5 bg-white border border-indigo-50 rounded-lg hover:border-indigo-100 transition-colors cursor-pointer shadow-sm" onClick={() => toggleSubtaskSelection(task.id, st.title)}>
                                               <Checkbox 
                                                   id={`st-${task.id}-${idx}`} 
                                                   checked={isSelected}
                                                   // @ts-ignore - onChange handled by parent div
                                                   onCheckedChange={() => {}} 
                                                   className="mt-0.5 border-indigo-300 text-indigo-600 focus:ring-indigo-500"
                                               />
                                               <div className="flex-1">
                                                   <label htmlFor={`st-${task.id}-${idx}`} className="text-sm font-medium text-gray-800 cursor-pointer">{st.title}</label>
                                                   <p className="text-xs text-gray-500 mt-0.5">{st.estimated_minutes} min</p>
                                               </div>
                                           </div>
                                       )
                                   })}
                               </div>
                               <div className="flex gap-2 justify-end">
                                   <Button size="sm" variant="ghost" className="text-gray-500 hover:text-gray-700" onClick={() => {
                                       setTaskBreakdowns(prev => {
                                           const next = { ...prev }; delete next[task.id]; return next;
                                       });
                                   }}>Cancel</Button>
                                   <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white" onClick={() => submitSubtasks(task.id)}>
                                       <ListPlus className="w-4 h-4 mr-2" />
                                       Add {selectedSubtasks[task.id]?.size || 0} tasks
                                   </Button>
                               </div>
                            </div>
                         )}
                      </div>
                   </CardContent>
                </Card>
             ))}
          </div>
        )}
      </div>

      {/* HOW IT WORKS SECTION */}
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
