import React, { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, token } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@isg.local')
  const [password, setPassword] = useState('password')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (token) return <Navigate to="/dashboard" replace />

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login({ email, password })
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError('Login failed')
    } finally {
      setLoading(false)
    }
  }

  const demoUsers = [
    { email: 'admin@isg.local', role: 'Admin (IT)' },
    { email: 'manager@isg.local', role: 'Manager' },
    { email: 'assistant@isg.local', role: 'Assistant Manager' },
    { email: 'hse@isg.local', role: 'HSE Expert' },
  ]

  return (
    <div className="max-w-md w-full space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <span className="text-6xl">🛡️</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-900">SafeVisor</h1>
        <p className="mt-2 text-gray-600">Occupational Health & Safety System</p>
      </div>

      {/* Login Form */}
      <div className="card p-8">
        <h2 className="text-xl font-semibold mb-6 text-center">Sign in to your account</h2>
        
        <form onSubmit={onSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label className="label">Email address</label>
            <input 
              className="input" 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label className="label">Password</label>
            <input 
              className="input" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              placeholder="Enter your password"
            />
          </div>
          
          <button 
            className="btn w-full justify-center py-3 text-base" 
            type="submit" 
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Signing in...
              </>
            ) : (
              'Sign in'
            )}
          </button>
        </form>
      </div>

      {/* Demo Users */}
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="text-sm font-medium text-blue-900 mb-3">Demo Accounts</h3>
        <div className="grid grid-cols-1 gap-2">
          {demoUsers.map((user) => (
            <button
              key={user.email}
              onClick={() => setEmail(user.email)}
              className="text-left p-2 rounded-md hover:bg-blue-100 transition-colors text-sm"
            >
              <div className="font-medium text-blue-900">{user.email}</div>
              <div className="text-blue-700">{user.role}</div>
            </button>
          ))}
        </div>
        <p className="text-xs text-blue-700 mt-3">
          Click any email above to auto-fill. Default password: "password"
        </p>
      </div>
    </div>
  )
}
