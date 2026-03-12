import React, { useEffect, useState } from "react";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, ShieldAlert } from "lucide-react";

interface Partner {
  id: number;
  name: string;
  email: string;
}

interface CommitmentModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  initialTitle: string;
  token: string;
}

export function CreateCommitmentModal({ isOpen, onOpenChange, initialTitle, token }: CommitmentModalProps) {
  const [loading, setLoading] = useState(false);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [formData, setFormData] = useState({
    title: initialTitle,
    date: "",
    buddyId: "",
    stakeValue: "10"
  });

  useEffect(() => {
    const fetchPartners = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/v1/partners", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        if (data.success) setPartners(data.partners);
      } catch (err) {
        console.error("Failed to fetch partners", err);
      }
    };

    if (isOpen) {
      setFormData(prev => ({ ...prev, title: initialTitle }));
      fetchPartners();
    }
  }, [isOpen, initialTitle, token]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const selectedPartner = partners.find(p => p.id.toString() === formData.buddyId);

    if (!formData.title || !formData.date || !selectedPartner) {
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:5000/api/v1/commitments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          title: formData.title,
          committed_datetime: new Date(formData.date).toISOString(),
          buddy_name: selectedPartner.name,
          buddy_email: selectedPartner.email,
          stake_value: parseInt(formData.stakeValue),
          content_id: null 
        }),
      });

      if (response.ok) {
        onOpenChange(false);
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

          <div className="grid grid-cols-1 gap-4">
            {/* 2. Buddy Selection Dropdown */}
            <div className="space-y-2">
              <Label htmlFor="buddy" className="text-gray-600">Select Buddy</Label>
              <Select 
                value={formData.buddyId} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, buddyId: value }))}
              >
                <SelectTrigger className="rounded-lg h-11">
                  <SelectValue placeholder={partners.length > 0 ? "Choose a buddy" : "Add buddies first"} />
                </SelectTrigger>
                <SelectContent>
                  {partners.map((partner) => (
                    <SelectItem key={partner.id} value={partner.id.toString()}>
                      {partner.name} ({partner.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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