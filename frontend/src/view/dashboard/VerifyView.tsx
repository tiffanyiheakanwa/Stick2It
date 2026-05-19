import { useEffect, useState } from "react";
import { Card, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { CheckCircle, XCircle, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

interface CommitmentDetails {
  id: number;
  title: string;
  student_name: string;
  stake_type: string;
  stake_value: number;
  penalty_message: string;
  status: string;
}

export function VerifyView() {
  const [token, setToken] = useState<string | null>(null);
  const [commitment, setCommitment] = useState<CommitmentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    // Extract token from URL /verify/{token}
    const pathParts = window.location.pathname.split('/verify/');
    if (pathParts.length > 1 && pathParts[1]) {
      const extractedToken = pathParts[1];
      setToken(extractedToken);
      fetchCommitment(extractedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCommitment = async (verifyToken: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/verify/${verifyToken}`);
      if (res.ok) {
        const data = await res.json();
        setCommitment(data);
      } else {
        toast.error("Failed to load verification details.");
      }
    } catch (e) {
      toast.error("Error connecting to server.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (action: 'kept' | 'broken') => {
    if (!token) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/verify/${token}/${action}`, {
        method: "POST"
      });
      if (res.ok) {
        toast.success(`Task marked as ${action}!`);
        // Update local state to reflect change
        setCommitment(prev => prev ? { ...prev, status: action === 'kept' ? 'completed' : 'broken' } : null);
      } else {
        const err = await res.json();
        toast.error(err.detail || "Verification failed");
      }
    } catch (e) {
      toast.error("Error connecting to server.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-indigo-50">
        <p className="text-gray-500">Loading verification details...</p>
      </div>
    );
  }

  if (!token || !commitment) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-indigo-50">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Invalid Verification Link</h2>
            <p className="text-gray-500">This link may be expired or malformed.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isAlreadyVerified = commitment.status === 'completed' || commitment.status === 'kept' || commitment.status === 'broken';

  return (
    <div className="flex items-center justify-center min-h-screen bg-indigo-50 p-4">
      <Card className="max-w-lg w-full bg-white shadow-xl border-0">
        <CardContent className="p-8">
          <div className="flex items-center gap-2 justify-center mb-6">
             <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
               <Sparkles className="w-6 h-6 text-indigo-600" />
             </div>
             <span className="text-2xl font-bold text-indigo-600">RemindAI Verification</span>
          </div>

          {isAlreadyVerified ? (
            <div className="text-center py-6">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Already Verified!</h2>
              <p className="text-gray-600">
                This task has already been marked as {commitment.status.toUpperCase()}.
              </p>
            </div>
          ) : (
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Accountability Check</h2>
              <p className="text-gray-600 mb-6">
                <strong className="text-indigo-600">{commitment.student_name}</strong> claims they completed:
              </p>
              
              <div className="bg-gray-50 rounded-xl p-6 mb-8 border border-gray-100 shadow-inner">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">"{commitment.title}"</h3>
                <div className="space-y-3 text-left">
                  <div className="flex items-start gap-2">
                    <span className="text-gray-500 font-medium w-20">Stake:</span>
                    <span className="text-gray-900">{commitment.stake_value} {commitment.stake_type}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-gray-500 font-medium w-20">Penalty:</span>
                    <span className="text-red-600 font-medium">{commitment.penalty_message}</span>
                  </div>
                </div>
              </div>

              <p className="text-gray-600 font-medium mb-6">Did they actually do it?</p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={() => handleVerify('kept')}
                  disabled={actionLoading}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white py-6 text-lg rounded-xl shadow-lg hover:shadow-green-500/25 transition-all"
                >
                  <CheckCircle className="w-6 h-6 mr-2" />
                  Yes, they kept it!
                </Button>
                
                <Button 
                  onClick={() => handleVerify('broken')}
                  disabled={actionLoading}
                  className="flex-1 bg-red-500 hover:bg-red-600 text-white py-6 text-lg rounded-xl shadow-lg hover:shadow-red-500/25 transition-all"
                >
                  <XCircle className="w-6 h-6 mr-2" />
                  No, they broke it
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
