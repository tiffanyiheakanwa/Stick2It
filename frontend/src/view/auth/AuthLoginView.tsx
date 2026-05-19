import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
import { requestAndSaveToken } from "../../service/pushNotifications"; 

interface AuthLoginViewProps {
  onLoginSuccess: (payload: {
    token: string;
    student: { id: number; name: string; email: string };
  }) => void;
  onSwitchToSignup: () => void;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || `${import.meta.env.VITE_API_URL}/api/v1`;

export function AuthLoginView({
  onLoginSuccess,
  onSwitchToSignup,
}: AuthLoginViewProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok || !data.success || !data.token || !data.student) {
        setError(data.error || "Invalid email or password.");
        return;
      }

      try {
        // We pass the new token to the notification service
        // This fires off the "Can we send you notifications?" prompt
        await requestAndSaveToken(data.token);
      } catch (fcmError) {
        // We log it but don't stop the login process if notifications fail
        console.error("Failed to sync push token:", fcmError);
      }

      onLoginSuccess({
        token: data.token,
        student: data.student,
      });
    } catch (err) {
      setError("A connection error occurred.");
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
            Welcome back
          </h1>
          <p className="text-gray-500 mb-6">
            Log in to see your reminders and keep your streak going.
          </p>

          {error && (
            <p className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
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
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className="mt-2 relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-2 text-gray-500">Or continue with</span>
            </div>
          </div>

          <div className="mt-2 space-y-2">
            <Button
              type="button"
              variant="outline"
              className="w-full font-medium"
              onClick={() => {
                window.location.href = `${API_BASE_URL}/auth/google`;
              }}
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google Account
            </Button>
          </div>

          <p className="mt-2 text-center text-sm text-gray-500">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              onClick={onSwitchToSignup}
              className="text-indigo-600 font-medium hover:underline"
            >
              Sign up
            </button>
          </p>
        </Card>
      </div>
    </div>
  );
}
