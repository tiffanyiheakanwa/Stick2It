import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

interface AuthSignupViewProps {
  onSignupSuccess: (payload: {
    token: string;
    student: { id: number; name: string; email: string };
  }) => void;
  onSwitchToLogin: () => void;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api/v1";

export function AuthSignupView({
  onSignupSuccess,
  onSwitchToLogin,
}: AuthSignupViewProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // 1. Register
      const registerRes = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      });

      const registerData = await registerRes.json();

      if (!registerRes.ok || !registerData.success) {
        setError(registerData.error || "Could not create account.");
        return;
      }

      // 2. Auto-login to get token
      const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const loginData = await loginRes.json();

      if (!loginRes.ok || !loginData.success || !loginData.token) {
        setError(loginData.error || "Account created, but login failed.");
        return;
      }

      onSignupSuccess({
        token: loginData.token,
        student: loginData.student,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-indigo-500 to-purple-600 px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-6 text-white">
          <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-indigo-600" />
          </div>
          <span className="text-lg font-semibold">RemindAI</span>
        </div>
        <Card className="p-6 shadow-xl">
          <h1 className="text-2xl font-semibold mb-2 text-gray-900">
            Create your account
          </h1>
          <p className="text-gray-500 mb-6">
            Sign up to start creating smarter reminders and commitments.
          </p>

          {error && (
            <p className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Smith"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-700"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Sign up"}
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-500">
            Already have an account?{" "}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-indigo-600 font-medium hover:underline"
            >
              Log in
            </button>
          </p>
        </Card>
      </div>
    </div>
  );
}

