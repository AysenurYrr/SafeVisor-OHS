import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { AuthAPI } from '../services/api'

// Roles: Admin (IT), Manager, AssistantManager, HSEExpert
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // Remove token storage from state - will use HttpOnly cookies instead
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  // Check if user is still authenticated on app load
  useEffect(() => {
    const initAuth = async () => {
      // Try to get current user if we have a session cookie
      if (!user) {
        try {
          setLoading(true)
          const userData = await AuthAPI.getCurrentUser()
          setUser(userData)
        } catch (error) {
          // No valid session, that's okay
          console.debug('No active session found')
        } finally {
          setLoading(false)
        }
      }
    }

    initAuth()
  }, [])

  const login = async ({ email, password }) => {
    try {
      setLoading(true)
      setError(null)
      
      // Call the ISG API login endpoint - tokens are set in HttpOnly cookies
      const response = await AuthAPI.login(email, password)
      
      // Get user info - the access token cookie is automatically sent
      const userData = await AuthAPI.getCurrentUser()
      setUser(userData)
      
      return { user: userData }
    } catch (error) {
      console.error('Login failed:', error)
      setError(error.response?.data?.detail || 'Login failed')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await AuthAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setError(null)
      // Clean up any remaining localStorage items
      localStorage.removeItem('user')
    }
  }

  const hasRole = (roles) => {
    if (!roles || roles.length === 0) return true
    if (!user) return false

    // Normalize allowed roles to uppercase for comparison
    const allowedUpper = new Set(roles.map(r => String(r).toUpperCase()))

    // Collect user role names (primary + any m2m roles if present)
    const names = new Set()
    const add = (n) => { if (n) names.add(String(n).toUpperCase()) }
    add(user.role?.name)
    if (Array.isArray(user.roles)) user.roles.forEach(r => add(r?.name))

    // Add friendly aliases to cover UI labels
    const aliases = new Set()
    if (names.has('ADMIN')) { aliases.add('ADMIN'); aliases.add('ADMIN (IT)'); aliases.add('ADMIN (IT)'.toUpperCase()) }
    if (names.has('MANAGER')) { aliases.add('MANAGER') }
    if (names.has('HSE_EXPERT')) { aliases.add('HSE_EXPERT'); aliases.add('HSEEXPERT') }

    // Compare
    const userUpper = new Set([...names, ...Array.from(aliases).map(a => String(a).toUpperCase())])
    // Superuser can access all
    if (user.is_superuser) return true
    for (const r of userUpper) {
      if (allowedUpper.has(r)) return true
    }
    return false
  }

  const clearError = () => setError(null)

  const value = useMemo(() => ({ 
    user, 
    loading,
    error,
    login, 
    logout, 
    hasRole,
    clearError,
    isAuthenticated: !!user
  }), [user, loading, error])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
