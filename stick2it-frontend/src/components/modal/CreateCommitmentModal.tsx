import React, { useEffect, useState } from "react";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, HeartHandshake, ShieldAlert } from "lucide-react";

interface CommitmentModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  initialTitle: string;
  token: string;
}

export function CreateCommitmentModal({ isOpen, onOpenChange, initialTitle, token }: CommitmentModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: initialTitle,
    date: "",
    buddyName: "",
    buddyEmail: "",
    stakeValue: "10"
  });

  useEffect(() => {
    if (isOpen) setFormData(prev => ({ ...prev, title: initialTitle }));  }, [isOpen, initialTitle]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!formData.title || !formData.date || !formData.buddyName) {
      console.error("Missing required fields!");
      return;
    }

    setLoading(true);
    
    try {
      const payload = {
        title: formData.title,
        committed_datetime: new Date(formData.date).toISOString(),
        buddy_name: formData.buddyName,
        buddy_email: formData.buddyEmail,
        stake_value: parseInt(formData.stakeValue),
      };
      console.log("Sending Payload:", payload);

      const response = await fetch("http://localhost:5000/api/v1/commitments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` // Use the JWT token from your auth state
        },
        body: JSON.stringify({
          student_id: "2",
          title: formData.title,
          committed_datetime: new Date(formData.date).toISOString(), // Format for backend
          buddy_name: formData.buddyName,
          buddy_email: formData.buddyEmail,
          stake_value: parseInt(formData.stakeValue),
          content_id: null // Set to null if not linked to specific learning content
        }),
      });

      if (response.ok) {
        onOpenChange(false);
        // Add a success toast notification here if available
      } else {
        const err = await response.json();
        console.error("Failed to create commitment:", err);
      }
    } catch (err) {
      console.error("Network error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] rounded-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-semibold flex items-center gap-2 text-indigo-600">
            <ShieldAlert className="w-6 h-6" />
            New Commitment
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          {/* Commitment Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-gray-600">What are you sticking to?</Label>
            <Input 
              id="title" 
              value={formData.title} 
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))} 
              required 
            />
          </div>

          {/* Time and Date */}
          <div className="space-y-2">
            <Label htmlFor="date" className="text-gray-600">Completion Deadline</Label>
            <div className="relative">
              <Calendar className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <Input id="date" type="datetime-local" value={formData.date} onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))} className="pl-10 rounded-lg" required />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="buddy_email" className="text-gray-600">Buddy Email</Label>
            <Input 
              id="buddy_email" 
              value={formData.buddyEmail} 
              onChange={(e) => setFormData(prev => ({ ...prev, buddyEmail: e.target.value }))} 
              required 
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Buddy Selection */}
            <div className="space-y-2">
              <Label htmlFor="buddy" className="text-gray-600">Buddy</Label>
              <div className="relative">
                <HeartHandshake className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <Input id="buddy" placeholder="Buddy name" value={formData.buddyName} onChange={(e) => setFormData(prev => ({ ...prev, buddyName: e.target.value }))} className="pl-10 rounded-lg" required />
              </div>
            </div>

            {/* Stake Selection */}
            <div className="space-y-2">
              <Label htmlFor="stake" className="text-gray-600">Stake Value</Label>
              <Select defaultValue="10" value={formData.stakeValue} onValueChange={(value) => setFormData(prev => ({ ...prev, stakeValue: value }))}>
                <SelectTrigger className="rounded-lg">
                  <SelectValue placeholder="Select Stake" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10 Points</SelectItem>
                  <SelectItem value="25">25 Points</SelectItem>
                  <SelectItem value="50">50 Points</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button 
              type="submit" 
              className="w-full bg-indigo-600 hover:bg-indigo-700 rounded-xl py-6 text-lg font-bold transition-all transform hover:scale-[1.02]"
              disabled={loading}
            >
              {loading ? "Staking..." : "Seal the Deal"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}