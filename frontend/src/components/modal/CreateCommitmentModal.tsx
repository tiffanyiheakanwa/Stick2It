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
  initialDate?: string;
  activationCommitmentId?: number | null;
  token: string;
}

export function CreateCommitmentModal({ isOpen, onOpenChange, initialTitle, initialDate, activationCommitmentId, token }: CommitmentModalProps) {
  const [loading, setLoading] = useState(false);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [formData, setFormData] = useState({
    title: initialTitle,
    date: "",
    buddyId: "",
    stakeValue: "10",
    stakeType: "Social",
    subjectiveDifficulty: "Medium"
  });

  useEffect(() => {
    const fetchPartners = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/partners`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        if (data.success) setPartners(data.partners);
      } catch (err) {
        console.error("Failed to fetch partners", err);
      }
    };

    if (isOpen) {
      let formattedDate = "";
      if (initialDate) {
        const d = new Date(initialDate);
        if (!isNaN(d.getTime())) {
          // Adjust for local timezone offset for datetime-local
          formattedDate = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        }
      }
      setFormData(prev => ({ 
        ...prev, 
        title: initialTitle,
        date: formattedDate
      }));
      fetchPartners();
    }
  }, [isOpen, initialTitle, initialDate, token]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const selectedPartner = partners.find(p => p.id.toString() === formData.buddyId);

    if (!formData.title || !formData.date) {
      return;
    }
    
    if (formData.stakeType === "Social" && !selectedPartner) {
        return;
    }

    setLoading(true);
    
    try {
      const isActivation = !!activationCommitmentId;
      const url = isActivation 
        ? `${import.meta.env.VITE_API_URL}/api/v1/commitments/${activationCommitmentId}/activate`
        : `${import.meta.env.VITE_API_URL}/api/v1/commitments`;
      const method = isActivation ? "PATCH" : "POST";

      const payload = isActivation ? {
          buddy_name: selectedPartner?.name || "",
          buddy_email: selectedPartner?.email || "",
          stake_value: parseInt(formData.stakeValue),
          stake_type: formData.stakeType,
          subjective_difficulty: formData.subjectiveDifficulty
      } : {
          title: formData.title,
          committed_datetime: new Date(formData.date).toISOString(),
          buddy_name: selectedPartner?.name || "",
          buddy_email: selectedPartner?.email || "",
          stake_value: parseInt(formData.stakeValue),
          stake_type: formData.stakeType,
          subjective_difficulty: formData.subjectiveDifficulty,
          content_id: null 
      };

      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload),
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
              disabled={!!activationCommitmentId}
              className={!!activationCommitmentId ? "bg-gray-100 text-gray-500 border-transparent shadow-none" : ""}
            />
          </div>

          {/* Time and Date */}
          <div className="space-y-2">
            <Label htmlFor="date" className="text-gray-600">Completion Deadline</Label>
            <div className="relative">
              <Calendar className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <Input 
                id="date" 
                type="datetime-local" 
                value={formData.date} 
                onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))} 
                className={`pl-10 rounded-lg ${!!activationCommitmentId ? "bg-gray-100 text-gray-500 border-transparent shadow-none" : ""}`}
                required 
                disabled={!!activationCommitmentId}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {/* 2. Buddy Selection Dropdown (Only if Social) */}
            {formData.stakeType === "Social" && (
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
            )}

            {/* Stake Selection */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="stakeType" className="text-gray-600">Commitment Type</Label>
                <Select value={formData.stakeType} onValueChange={(value) => setFormData(prev => ({ ...prev, stakeType: value }))}>
                  <SelectTrigger className="rounded-lg h-11">
                    <SelectValue placeholder="Select Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Social">Social</SelectItem>
                    <SelectItem value="Point-only">Point-only</SelectItem>
                    <SelectItem value="Lock-in">Lock-in</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="stake" className="text-gray-600">Stake Value</Label>
                <Select defaultValue="10" value={formData.stakeValue} onValueChange={(value) => setFormData(prev => ({ ...prev, stakeValue: value }))}>
                  <SelectTrigger className="rounded-lg h-11">
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

            {/* Subjective Difficulty */}
            <div className="space-y-2">
              <Label htmlFor="difficulty" className="text-gray-600">Task Difficulty</Label>
              <Select value={formData.subjectiveDifficulty} onValueChange={(value) => setFormData(prev => ({ ...prev, subjectiveDifficulty: value }))}>
                <SelectTrigger className="rounded-lg h-11">
                  <SelectValue placeholder="Select Difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Easy">Easy</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="Hard">Hard</SelectItem>
                  <SelectItem value="Anxiety-Inducing">Anxiety-Inducing</SelectItem>
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
