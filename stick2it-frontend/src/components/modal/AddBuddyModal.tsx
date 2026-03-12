import * as React from "react";
import { useState } from "react";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {  Handshake, Loader2,  } from "lucide-react";

interface AdBuddyModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  token: string;
}

export function AddBuddyModal({ isOpen, onOpenChange, token }: AdBuddyModalProps) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddBuddy = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {

      const response = await fetch("http://localhost:5000/api/v1/partners", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` // Use the JWT token from your auth state
        },
        body: JSON.stringify({
          partner_email: email,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setEmail("");
        onOpenChange(false);
        // Add a success toast notification here if available
      } else {
        setError(data.error || "Failed to add buddy");
      }
    } catch (err) {
        setError("Network error. Please try again.");    
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[400px] rounded-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-semibold flex items-center gap-2 text-indigo-600">
            <Handshake className="w-6 h-6" />
            Add Accountability Buddy
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleAddBuddy} className="space-y-6 pt-4">
          <div className="space-y-2">
            <Label htmlFor="buddy_email" className="text-gray-600">Buddy's Email Address</Label>
            <Input 
              id="buddy_email" 
              placeholder="friend@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
            {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
          </div>

          <DialogFooter>
            <Button 
              type="submit" 
              className="w-full bg-indigo-600 hover:bg-indigo-700 rounded-xl py-6 text-lg font-bold transition-all transform hover:scale-[1.02]"
              disabled={loading || !email}
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Searching...</>
              ) : (
                "Send Request"
              )}            
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}