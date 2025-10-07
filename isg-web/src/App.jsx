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
import FactoryAreas from './pages/FactoryAreas'
import Violations from './pages/Events/Violations'
import Pose from './pages/Events/Pose'
import Users from './pages/Admin/Users'
import LiveCamera from './pages/LiveCamera'

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
            <Route path="/cameras" element={<PrivateRoute allowedRoles={["Admin (IT)", "Manager"]}><Cameras /></PrivateRoute>} />
            <Route path="/factory-areas" element={<PrivateRoute allowedRoles={["Admin (IT)", "Manager"]}><FactoryAreas /></PrivateRoute>} />
            <Route path="/live-camera" element={<LiveCamera />} />
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
