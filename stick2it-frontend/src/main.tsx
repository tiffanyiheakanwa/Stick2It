import React from 'react'
import ReactDOM from 'react-dom/client' // Add this line
import App from './App.tsx'
import "./styles/index.css";
import { TaskProvider } from './context/TaskContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TaskProvider>
      <App />
    </TaskProvider>
  </React.StrictMode>,
)