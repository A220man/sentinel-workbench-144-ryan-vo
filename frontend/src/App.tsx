import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './hooks/useAuthStore'
import Layout from './components/Layout'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Sessions from './components/Sessions'
import SessionDetail from './components/SessionDetail'
import Inbox from './components/Inbox'
import Settings from './components/Settings'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()
  
  // Check auth on mount
  React.useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" replace />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/sessions/:id" element={<SessionDetail />} />
        <Route path="/inbox" element={<Inbox />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

import React from 'react'

export default App
