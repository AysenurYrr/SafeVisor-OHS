import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

// Roles: Admin (IT), Manager, AssistantManager, HSEExpert
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  const login = async ({ email, password }) => {
    // Simulate API call and issue a dummy JWT
    await new Promise(r => setTimeout(r, 400))
    const dummyToken = 'dummy-jwt-token'
    const role = email?.includes('admin') ? 'Admin (IT)' : email?.includes('manager') ? 'Manager' : email?.includes('assistant') ? 'AssistantManager' : 'HSEExpert'
    const newUser = { email, name: email.split('@')[0] || 'User', role }
    setToken(dummyToken)
    setUser(newUser)
    return { token: dummyToken, user: newUser }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  const hasRole = (roles) => {
    if (!roles || roles.length === 0) return true
    return roles.includes(user?.role)
  }

  const value = useMemo(() => ({ token, user, login, logout, hasRole }), [token, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
