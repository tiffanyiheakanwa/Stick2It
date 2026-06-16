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
  refreshData: (isInitial?: boolean) => Promise<void>;
  handleVerify: (vToken: string, action: 'kept' | 'broken') => Promise<void>;
  startTask: (assignmentId: number) => void;
  setGlobalTaskInput: (value: string) => void;
  addReminder: (title: string, time: string, priority?: string, isSubtask?: boolean, parentId?: number) => Promise<boolean>;
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

  const parseCommittedDatetime = (timeLabel: string) => {
    const now = new Date();
    const lower = timeLabel.toLowerCase();

    if (lower.includes('in')) {
      const match = lower.match(/in\s*(\d+)\s*hour/);
      if (match) {
        const hours = parseInt(match[1], 10);
        const result = new Date(now.getTime() + hours * 60 * 60 * 1000);
        return result;
      }
    }

    if (lower.includes('tomorrow')) {
      const timeMatch = lower.match(/tomorrow(?:,\s*(.*))?/);
      const tomorrow = new Date(now);
      tomorrow.setDate(now.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);
      if (timeMatch && timeMatch[1]) {
        const parsed = new Date(`${tomorrow.toDateString()} ${timeMatch[1]}`);
        if (!isNaN(parsed.getTime())) {
          return parsed;
        }
      }
      return tomorrow;
    }

    if (lower.includes('today')) {
      const timeMatch = lower.match(/today(?:,\s*(.*))?/);
      const today = new Date(now);
      const defaultHour = now.getHours() < 18 ? 18 : 23;
      const defaultMinute = now.getHours() < 18 ? 0 : 59;
      today.setHours(defaultHour, defaultMinute, 0, 0);
      if (timeMatch && timeMatch[1]) {
        const parsed = new Date(`${today.toDateString()} ${timeMatch[1]}`);
        if (!isNaN(parsed.getTime())) {
          return parsed;
        }
      }
      return today;
    }

    // Default fallback: 2 hours from now
    return new Date(now.getTime() + 2 * 60 * 60 * 1000);
  };

  const markNotificationsViewed = () => {
    setLastSeenUnreadCount(unreadCount);
  };

  // Load auth from sessionStorage on mount
  useEffect(() => {
    const savedToken = sessionStorage.getItem('token');
    const savedId = sessionStorage.getItem('studentId');
    const savedStudent = sessionStorage.getItem('student');
    const cachedCommitments = sessionStorage.getItem('commitments');

    if (savedToken && savedId) {
      setToken(savedToken);
      setStudentId(parseInt(savedId));
      if (savedStudent) {
        setCurrentStudent(JSON.parse(savedStudent));
      }
      if (cachedCommitments) {
        setCommitments(JSON.parse(cachedCommitments));
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
              refreshData(true);
            } else if (resObj.status === 200 && resObj.data?.synced_count > 0) {
              toast.success(`Synced ${resObj.data.synced_count} tasks from your platforms!`, { duration: 4000 });
              refreshData(true);
            } else {
              refreshData(true);
            }
          }).catch(err => {
            console.error("Auto-sync error:", err);
            refreshData(true);
          });
      } else {
        refreshData(true);
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


  const refreshData = async (isInitial = false) => {
    if (!token || !studentId) return;
    if (isInitial) setLoading(true);
    
    try {
      const [statsRes, buddyRes, notifRes, partnersRes] = await Promise.allSettled([
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/buddy/commitments`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/notifications`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/partners`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      const statsData = statsRes.status === 'fulfilled' && statsRes.value.ok
        ? await statsRes.value.json()
        : { commitments: [], streak: 0, points: 0 };
      const buddyData = buddyRes.status === 'fulfilled' && buddyRes.value.ok
        ? await buddyRes.value.json()
        : { commitments: [] };
      const notifData = notifRes.status === 'fulfilled' && notifRes.value.ok
        ? await notifRes.value.json()
        : { notifications: [] };
      const partnersData = partnersRes.status === 'fulfilled' && partnersRes.value.ok
        ? await partnersRes.value.json()
        : { partners: [] };

      if (statsRes.status !== 'fulfilled' || !statsRes.value.ok) {
        console.error('Failed to load student stats', statsRes);
      }
      if (buddyRes.status !== 'fulfilled' || !buddyRes.value.ok) {
        console.error('Failed to load buddy commitments', buddyRes);
      }
      if (notifRes.status !== 'fulfilled' || !notifRes.value.ok) {
        console.error('Failed to load notifications', notifRes);
      }
      if (partnersRes.status !== 'fulfilled' || !partnersRes.value.ok) {
        console.error('Failed to load partners', partnersRes);
      }

      setCommitments(statsData.commitments || []);
      setStreak(statsData.streak || 0);
      setPoints(statsData.points || 0);
      setNotifications(notifData.notifications || []);
      setSupervisedTasks(buddyData.commitments || []);
      setPartners(partnersData.partners || []);

      // Cache commitments for instant load next time
      sessionStorage.setItem('commitments', JSON.stringify(statsData.commitments || []));

      // Fetch nudges and predictions in background — don't block UI
      Promise.all([
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/nudges`, {
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.json()).catch(() => ({ nudges: [] })),
        fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/${studentId}/predict`, {
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.json()).catch(() => ({ prediction: null }))
      ]).then(([nudgeData, predictData]) => {
        setNudges(nudgeData.nudges || []);
        setStressScore(predictData.prediction?.probability_high_risk || 0);
      });

    } catch (err) {
      console.error("Data refresh failed", err);
    } finally {
      if (isInitial) setLoading(false);
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

  const addReminder = async (title: string, time: string, priority: string = "Medium", isSubtask: boolean = false, parentId?: number) => {
    if (!title.trim()) return false;

    const dueDate = parseCommittedDatetime(time);
    const requestBody: any = {
      title,
      committed_datetime: dueDate.toISOString(),
      stake_value: 10,
      stake_type: isSubtask ? "AI_Subtask" : "Points"
    };

    if (parentId) {
      requestBody.parent_commitment_id = parentId;
    }

    setIsSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/commitments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const savedTask = await response.json();
        const newId = savedTask.id || savedTask.commitment_id;

        setCommitments((prev) => [
          ...prev,
          {
            id: newId,
            title,
            time,
            status: "pending",
            completed: false,
            date: dueDate.toISOString().split('T')[0],
            aiSuggested: isSubtask,
            stake_type: isSubtask ? "AI_Subtask" : "Points",
            priority,
            category: "General"
          },
        ]);
        setGlobalTaskInput("");
        await refreshData();
        return true;
      }

      const errorData = await response.json().catch(() => null);
      console.error("Failed to add reminder:", errorData || response.statusText);
      return false;
    } catch (error) {
      console.error("Context Error adding reminder:", error);
      return false;
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
