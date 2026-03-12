// stick2it-frontend/src/view/dashboard/BuddyView.tsx

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react";

export function BuddyView({ token }: { token: string }) {
  const [commitments, setCommitments] = useState<any[]>([]);

  const fetchBuddyTasks = async () => {
    const res = await fetch("http://localhost:5000/api/v1/buddy/commitments", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (data.success) setCommitments(data.commitments);
  };

  useEffect(() => { fetchBuddyTasks(); }, [token]);

  const handleVerify = async (vToken: string, action: 'kept' | 'broken') => {
    // Calls the endpoint defined in your main.py
    const res = await fetch(`http://localhost:5000/api/v1/verify/${vToken}/${action}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    if (res.ok) fetchBuddyTasks(); // Refresh list
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
              {commitments.map((c) => (
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
                    <Button size="sm" variant="outline" className="text-red-600" onClick={() => handleVerify(c.verification_token, 'broken')}>
                      <XCircle className="w-4 h-4 mr-1" /> Broken
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}