import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function PrivateRoute({ allowedRoles, children }) {
  const { token, user, hasRole } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  if (allowedRoles && !hasRole(allowedRoles)) return <Navigate to="/dashboard" replace />
  // Support wrapping a single element or acting as a wrapper route with Outlet
  return children ? children : <Outlet />
}
