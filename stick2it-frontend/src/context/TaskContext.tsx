import React, { createContext, useContext, useState, useEffect } from 'react';

const API_BASE_URL = "http://localhost:5000/api/v1";

interface TaskContextType {
  studentId: number | null;
  token: string | null;
  isAuthenticated: boolean; 
  currentStudent: any | null; 
  commitments: any[];
  nudges: any[];
  loading: boolean;
  supervisedTasks: any[];
  globalTaskInput: string;
  isSaving: boolean;
  login: (token: string, student: any) => void;
  logout: () => void;
  refreshData: () => Promise<void>;
  handleVerify: (vToken: string, action: 'kept' | 'broken') => Promise<void>;
  startTask: (assignmentId:number)=> void;
  setGlobalTaskInput: (value: string) => void;
  addReminder: (title: string, time: string, priority?:string)=> Promise<void>;
  toggleReminder: (id:number) => void;
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
  const [globalTaskInput, setGlobalTaskInput] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  
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
  
  useEffect(() => {
    if (token && studentId) {
      refreshData();
    }
  }, [token, studentId]);

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
    try {
      const [statsRes, nudgeRes, buddyRes] = await Promise.all([
        fetch(`http://localhost:5000/api/v1/students/${studentId}/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`http://localhost:5000/api/v1/students/${studentId}/nudges`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        // Fetch the tasks where YOU are the buddy
        fetch(`http://localhost:5000/api/v1/buddy/commitments`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      const statsData = await statsRes.json();
      const nudgeData = await nudgeRes.json();
      const buddyData = await buddyRes.json();
      
      setCommitments(statsData.commitments || []);
      setNudges(nudgeData.nudges || []);
      setSupervisedTasks(buddyData.commitments || [])
    } catch (err) {
      console.error("Data refresh failed", err);
    }
  };
  
  const handleVerify = async (vToken: string, action: 'kept' | 'broken') => {
    if (!token) return;
    try {
      const res = await fetch(`http://localhost:5000/api/v1/verify/${vToken}/${action}`, {
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

  const toggleReminder = (id: number) => {
    setCommitments(prev =>
      prev.map((r) => r.id === id ? { ...r, completed: !r.completed } : r)
    );
  };

  const addReminder = async (title: string, time: string, priority: string = "Medium") => {
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
          stake_value: 10
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
            aiSuggested: false,
            priority: priority ,
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
      const res = await fetch(`http://localhost:5000/api/v1/commitments/${assignmentId}/start`, {
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
    <TaskContext.Provider value={{ studentId, token, isAuthenticated: !!token, 
      currentStudent,commitments, nudges, loading, login, logout, refreshData, supervisedTasks, handleVerify, startTask, toggleReminder, addReminder, 
      globalTaskInput, 
      setGlobalTaskInput, 
      isSaving }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) throw new Error("useTasks must be used within a TaskProvider");
  return context;
};