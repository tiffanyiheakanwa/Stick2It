import React, { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const API_BASE_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

interface TaskContextType {
  studentId: number | null;
  token: string | null;
  isAuthenticated: boolean;
  currentStudent: any | null;
  commitments: any[];
  nudges: any[];
  loading: boolean;
  supervisedTasks: any[];
  notifications: any[];
  partners: any[];
  streak: number;
  points: number;
  stressScore: number;
  globalTaskInput: string;
  isSaving: boolean;
  displayedBadgeCount: number;
  markNotificationsViewed: () => void;
  login: (token: string, student: any) => void;
  logout: () => void;
  refreshData: () => Promise<void>;
  handleVerify: (vToken: string, action: 'kept' | 'broken') => Promise<void>;
  startTask: (assignmentId: number) => void;
  setGlobalTaskInput: (value: string) => void;
  addReminder: (title: string, time: string, priority?: string, isSubtask?: boolean) => Promise<void>;
  toggleReminder: (id: number) => void;
  submitReminder: (id: number) => Promise<void>;
  deleteReminder: (id: number) => Promise<void>;
  handleRespond: (id: number, action: 'accept' | 'refuse') => Promise<void>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export const TaskProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [studentId, setStudentId] = useState<number | null>(null);
  const [currentStudent, setCurrentStudent] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [commitments, setCommitments] = useState<any[]>([]);
  const [nudges, setNudges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [supervisedTasks, setSupervisedTasks] = useState<any[]>([]);
  const [streak, setStreak] = useState(0);
  const [points, setPoints] = useState(0);
  const [stressScore, setStressScore] = useState(0);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [globalTaskInput, setGlobalTaskInput] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [lastSeenUnreadCount, setLastSeenUnreadCount] = useState(0);
  const [partners, setPartners] = useState<any[]>([]);

  const unreadCount = notifications.filter(n => n.status === 'unread').length;

  useEffect(() => {
    if (unreadCount < lastSeenUnreadCount) {
      setLastSeenUnreadCount(unreadCount);
    }
  }, [unreadCount, lastSeenUnreadCount]);

  const displayedBadgeCount = Math.max(0, unreadCount - lastSeenUnreadCount);

  const markNotificationsViewed = () => {
    setLastSeenUnreadCount(unreadCount);
  };

  // Load auth from sessionStorage on mount
  useEffect(() => {
    const savedToken = sessionStorage.getItem('token');
    const savedId = sessionStorage.getItem('studentId');
    const savedStudent = sessionStorage.getItem('student');
    if (savedToken && savedId) {
      setToken(savedToken);
      setStudentId(parseInt(savedId));
      if (savedStudent) {
        setCurrentStudent(JSON.parse(savedStudent));
      }
    }
    setLoading(false);
  }, []);

  const [hasSyncedThisSession, setHasSyncedThisSession] = useState(false);

  useEffect(() => {
    if (token && studentId) {
      if (!hasSyncedThisSession) {
        setHasSyncedThisSession(true);
        // Trigger background sync on first load of the session
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/me/sync-assignments`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        })
          .then(res => res.json().then(data => ({ status: res.status, data })))
          .then(resObj => {
            if (resObj.status === 401 && resObj.data?.detail?.includes("expired")) {
              toast.error("Your external account token expired. Please completely sign out and logically click 'Continue with Google' to restore syncing.", { duration: 8000 });
              refreshData();
            } else if (resObj.status === 200 && resObj.data?.synced_count > 0) {
              toast.success(`Synced ${resObj.data.synced_count} tasks from your platforms!`, { duration: 4000 });
              refreshData();
            } else {
              refreshData();
            }
          }).catch(err => {
            console.error("Auto-sync error:", err);
            refreshData();
          });
      } else {
        refreshData();
      }
    }
  }, [token, studentId]);

  useEffect(() => {
    // Global WebSocket connection for cross-view updates
    if (!studentId) return;
    // Extract the host from VITE_API_URL and determine the protocol
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    const socket = new WebSocket(`${wsProtocol}://${wsHost}/ws/${studentId}`);

    socket.onopen = () => {
      console.log("Connected to RemindAI Real-time Sync (Global)");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "COMMITMENT_UPDATED") {
        console.log(`Global sync: Buddy marked task as ${data.status}!`);
        refreshData();

        if (data.status === "completed") {
          toast.success((_t) => (
            <span>
              <b>Task Verified!</b> <br />
              Buddy confirmed you finished your task. +{data.points_gained || 10} points!
            </span>
          ),
            { duration: 5000, icon: '✅' }
          );
        } else if (data.status === "failed") {
          toast.error(
            "Buddy marked the task as failed. Stake deducted.",
            { duration: 6000, icon: '⚠️' }
          );
        }
      }
    };

    socket.onerror = (error) => {
      console.error("Global WebSocket Error:", error);
    };

    return () => socket.close();
  }, [studentId]);

  const login = (newToken: string, student: any) => {
    setToken(newToken);
    setCurrentStudent(student);
    setStudentId(student.id);
    sessionStorage.setItem('token', newToken);
    sessionStorage.setItem('studentId', student.id.toString());
    sessionStorage.setItem('student', JSON.stringify(student));
  };

  const logout = () => {
    setToken(null);
    setCurrentStudent(null);
    setStudentId(null);
    sessionStorage.clear();
  };


  const refreshData = async () => {
    if (!token || !studentId) return;
    setLoading(true);
    try {
      const [statsRes, nudgeRes, buddyRes, predictRes, notifRes, partnersRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/nudges`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/buddy/commitments`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/predict`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/notifications`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/partners`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      const statsData = await statsRes.json();
      const nudgeData = await nudgeRes.json();
      const buddyData = await buddyRes.json();
      const predictData = await predictRes.json();
      const notifData = await notifRes.json();
      const partnersData = await partnersRes.json();

      setCommitments(statsData.commitments || []);
      setStreak(statsData.streak || 0);
      setPoints(statsData.points || 0);
      setStressScore(predictData.prediction?.probability_high_risk || 0);
      setNotifications(notifData.notifications || []);
      setNudges(nudgeData.nudges || []);
      setSupervisedTasks(buddyData.commitments || [])
      setPartners(partnersData.partners || []);
    } catch (err) {
      console.error("Data refresh failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (vToken: string, action: 'kept' | 'broken') => {
    if (!token) return;
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/verify/${vToken}/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (res.ok) {
        await refreshData();
      }
    } catch (error) {
      console.error("Verification failed:", error);
    }
  };

  const handleRespond = async (id: number, action: 'accept' | 'refuse') => {
    if (!token) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/notifications/${id}/respond`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });
      if (response.ok) {
        await refreshData();
      }
    } catch (err) {
      console.error("Error responding to request");
    }
  };

  const toggleReminder = (id: number) => {
    setCommitments(prev =>
      prev.map((r) => r.id === id ? { ...r, completed: !r.completed } : r)
    );
  };

  const deleteReminder = async (id: number) => {
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/commitments/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        toast.success("Task ignored.");
        await refreshData();
      }
    } catch (err) {
      console.error("Error deleting reminder", err);
    }
  };

  const submitReminder = async (id: number) => {
    if (!token) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/commitments/${id}/submit`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        toast.success("Task submitted for buddy verification!");
        await refreshData();
      } else {
        const data = await response.json();
        toast.error(data.detail || "Failed to submit task");
      }
    } catch (err) {
      console.error("Error submitting reminder", err);
    }
  };

  const addReminder = async (title: string, time: string, priority: string = "Medium", isSubtask: boolean = false) => {
    if (!title.trim()) return;

    setIsSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/commitments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          committed_datetime: new Date().toISOString(),
          stake_value: 10,
          stake_type: isSubtask ? "AI_Subtask" : "Points"
        }),
      });

      if (response.ok) {
        const savedTask = await response.json();

        setCommitments((prev) => [
          ...prev,
          {
            id: savedTask.id,
            title: title,
            time: time,
            status: "pending",
            completed: false,
            date: new Date().toISOString().split('T')[0],
            aiSuggested: isSubtask,
            stake_type: isSubtask ? "AI_Subtask" : "Points",
            priority: priority,
            category: "General"
          },
        ]);
        setGlobalTaskInput("");
        await refreshData();
      }
    } catch (error) {
      console.error("Context Error adding reminder:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const startTask = async (assignmentId: number) => {
    if (!token) return;
    console.log(" Attempting to start task ID:", assignmentId);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/commitments/${assignmentId}/start`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (res.ok) {
        console.log("Backend updated. Re-fetching risk scores...");
        await refreshData();
        alert("Task started! Focus mode activated. ");
      }
      else {
        const errorData = await res.json();
        console.error("Backend rejected the start request:", errorData);
      }
    } catch (error) {
      console.error("Failed to start task:", error);
    }
  };

  return (
    <TaskContext.Provider value={{
      studentId, token, isAuthenticated: !!token,
      currentStudent, commitments, nudges, loading, partners, login, logout, refreshData, supervisedTasks, streak, points, stressScore, notifications, handleVerify, handleRespond, startTask, toggleReminder, addReminder, deleteReminder,
      globalTaskInput, setGlobalTaskInput,
      isSaving,
      displayedBadgeCount,
      markNotificationsViewed,
      submitReminder
    }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) throw new Error("useTasks must be used within a TaskProvider");
  return context;
};
