import { useEffect, useState } from "react";
import { useTasks } from "../../context/TaskContext";

export function OAuthCallbackView() {
  const [error, setError] = useState("");
  const { login } = useTasks();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      // Fetch user profile to complete login
      fetch(`${import.meta.env.VITE_API_URL}/api/v1/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch user");
        return res.json();
      })
      .then(student => {
        login(token, student);
        window.location.href = "/"; // Strip query params and reload
      })
      .catch(err => {
        setError(err.message);
      });
    } else {
      setError("No authentication token found in URL.");
    }
  }, [login]);

  if (error) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-red-600 text-white">
        <p className="text-xl mb-4">Error: {error}</p>
        <a href="/" className="underline text-lg">Return Home</a>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-indigo-600 text-white">
      <p className="text-2xl font-bold animate-pulse">Completing login...</p>
    </div>
  );
}
