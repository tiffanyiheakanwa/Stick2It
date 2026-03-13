import React, { createContext, useContext, useState, useEffect } from 'react';

interface TaskContextType {
  studentId: number | null;
  token: string | null;
  isAuthenticated: boolean; 
  currentStudent: any | null; 
  commitments: any[];
  nudges: any[];
  loading: boolean;
  login: (token: string, student: any) => void;
  logout: () => void;
  refreshData: () => Promise<void>;
  supervisedTasks: any[];
  handleVerify: (vToken: string, action: 'kept' | 'broken') => Promise<void>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export const TaskProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [studentId, setStudentId] = useState<number | null>(null);
  const [currentStudent, setCurrentStudent] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [commitments, setCommitments] = useState([]);
  const [nudges, setNudges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [supervisedTasks, setSupervisedTasks] = useState<any[]>([]);

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

  return (
    <TaskContext.Provider value={{ studentId, token, isAuthenticated: !!token, 
      currentStudent,commitments, nudges, loading, login, logout, refreshData, supervisedTasks, handleVerify }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) throw new Error("useTasks must be used within a TaskProvider");
  return context;
};