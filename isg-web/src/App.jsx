import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './routes/PrivateRoute'

import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Employees from './pages/Employees'
import Cameras from './pages/Cameras'
import Violations from './pages/Events/Violations'
import Pose from './pages/Events/Pose'
import Users from './pages/Admin/Users'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<AuthLayout />}> 
          <Route path="/login" element={<Login />} />
        </Route>

        <Route element={<PrivateRoute />}> 
          <Route element={<DashboardLayout />}> 
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/cameras" element={<Cameras />} />
            <Route path="/events/violations" element={<Violations />} />
            <Route path="/events/pose" element={<Pose />} />
            <Route path="/admin/users" element={<PrivateRoute allowedRoles={["Admin (IT)"]}><Users /></PrivateRoute>} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}
