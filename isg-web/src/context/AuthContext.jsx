import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { AuthAPI } from '../services/api'

// Roles: Admin (IT), Manager, AssistantManager, HSEExpert
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refreshToken'))
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  useEffect(() => {
    if (refreshToken) localStorage.setItem('refreshToken', refreshToken)
    else localStorage.removeItem('refreshToken')
  }, [refreshToken])

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  // Check if user is still authenticated on app load
  useEffect(() => {
    const initAuth = async () => {
      if (token && !user) {
        try {
          setLoading(true)
          const userData = await AuthAPI.getCurrentUser()
          setUser(userData)
        } catch (error) {
          console.error('Failed to get current user:', error)
          // Clear invalid token
          setToken(null)
          setRefreshToken(null)
        } finally {
          setLoading(false)
        }
      }
    }

    initAuth()
  }, [token, user])

  const login = async ({ email, password }) => {
    try {
      setLoading(true)
      setError(null)
      
      // Call the real ISG API login endpoint
      const response = await AuthAPI.login(email, password)
      
      // Store tokens immediately so interceptors pick them up for the next request
      if (response?.access_token) localStorage.setItem('token', response.access_token)
      if (response?.refresh_token) localStorage.setItem('refreshToken', response.refresh_token)
      setToken(response.access_token)
      setRefreshToken(response.refresh_token)
      
      // Get user info
      const userData = await AuthAPI.getCurrentUser()
      setUser(userData)
      
      return { token: response.access_token, user: userData }
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
      if (token) {
        await AuthAPI.logout()
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setToken(null)
      setRefreshToken(null)
      setUser(null)
      setError(null)
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
    token, 
    refreshToken,
    user, 
    loading,
    error,
    login, 
    logout, 
    hasRole,
    clearError,
    isAuthenticated: !!token && !!user
  }), [token, refreshToken, user, loading, error])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
