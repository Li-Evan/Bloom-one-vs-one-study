import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './lib/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import CreditsPage from './pages/CreditsPage'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-400">加载中...</div>
  if (!user) return <Navigate to="/login" />
  return children
}

function GuestRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-400">加载中...</div>
  if (user) return <Navigate to="/" />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
      <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
      <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/chat/:courseId" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
      <Route path="/credits" element={<ProtectedRoute><CreditsPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
