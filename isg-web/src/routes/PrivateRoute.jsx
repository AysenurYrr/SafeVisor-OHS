import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function PrivateRoute({ allowedRoles, children }) {
  const { user, hasRole, loading } = useAuth()
  
  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  // Redirect to login if not authenticated
  if (!user) return <Navigate to="/login" replace />
  
  // Check role-based access if roles are specified
  if (allowedRoles && !hasRole(allowedRoles)) return <Navigate to="/dashboard" replace />
  
  // Support wrapping a single element or acting as a wrapper route with Outlet
  return children ? children : <Outlet />
}
