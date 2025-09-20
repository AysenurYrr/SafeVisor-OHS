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
      
      // Demo mode - simulate login for UI demonstration
      if (email && password === 'password') {
        const demoUser = {
          id: 1,
          name: 'John Doe',
          email: email,
          role: { name: 'Admin' }
        }
        const demoToken = 'demo-token-' + Date.now()
        
        setToken(demoToken)
        setUser(demoUser)
        
        return { token: demoToken, user: demoUser }
      }
      
      // Original API call (will fail if backend not running)
      const response = await AuthAPI.login(email, password)
      
      // Store tokens
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
    if (!user?.role?.name) return false
    
    // Map backend role names to frontend role names
    const roleMapping = {
      'Admin': 'Admin (IT)',
      'Manager': 'Manager',
      'AssistantManager': 'AssistantManager',
      'HSEExpert': 'HSEExpert'
    }
    
    const userRole = roleMapping[user.role.name] || user.role.name
    return roles.includes(userRole)
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
