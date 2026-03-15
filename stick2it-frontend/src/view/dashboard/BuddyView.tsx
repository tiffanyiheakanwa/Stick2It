import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react";
import { useTasks } from '../../context/TaskContext';

export function BuddyView() {
  const { supervisedTasks, handleVerify, refreshData, token, studentId } = useTasks();

  const [confirmingTask, setConfirmingTask] = useState<any | null>(null);

  useEffect(() => {
    if (token && studentId) {
      refreshData();
    }
  }, [token, studentId, refreshData]);

  const triggerBrokenConfirmation = (task: any) => {
    setConfirmingTask(task);
  };

  const executeBrokenAction = () => {
    if (confirmingTask) {
      handleVerify(confirmingTask.verification_token, 'broken');
      setConfirmingTask(null);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="text-indigo-600" />
            Commitments You're Supervising
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Student</TableHead>
                <TableHead>Task</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Stake</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {supervisedTasks.map((c:any) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.owner_name}</TableCell>
                  <TableCell>{c.title}</TableCell>
                  <TableCell>
                    <Badge variant={parseFloat(c.risk_score) > 70 ? "destructive" : "secondary"}>
                      {c.risk_score}% Risk
                    </Badge>
                  </TableCell>
                  <TableCell>${c.stake}</TableCell>
                  <TableCell className="text-right flex justify-end gap-2">
                    <Button size="sm" variant="outline" className="text-green-600" onClick={() => handleVerify(c.verification_token, 'kept')}>
                      <CheckCircle2 className="w-4 h-4 mr-1" /> Kept
                    </Button>
                    <Button size="sm" variant="outline" className="text-red-600" onClick={() => triggerBrokenConfirmation(c)}>
                      <XCircle className="w-4 h-4 mr-1" /> Broken
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      {/* 🌟 THE CONFIRMATION MODAL */}
      {confirmingTask && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full animate-in fade-in zoom-in duration-200">
            <CardHeader>
              <CardTitle className="text-red-600 flex items-center gap-2">
                <AlertCircle /> Confirm Penalty
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">
                Are you sure you want to mark <strong>{confirmingTask.title}</strong> as broken?
              </p>
              <div className="bg-red-50 p-4 rounded-lg border border-red-100 text-sm text-red-800">
                <strong>Consequences:</strong>
                <ul className="list-disc ml-5 mt-1">
                  <li>{confirmingTask.owner_name} will lose {confirmingTask.stake} points.</li>
                  <li>Their current success streak will be reset to 0.</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setConfirmingTask(null)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={executeBrokenAction}>
                Yes, Mark as Broken
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </div>
  );
}
