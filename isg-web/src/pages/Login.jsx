import React, { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Icon from '../components/Icon'
import Button from '../components/Button'

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
      setError('Invalid email or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in-custom">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-primary-600 rounded-2xl shadow-large">
            <Icon name="safety-solid" className="w-12 h-12 text-white" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-neutral-900">Welcome to SafeVisor</h1>
        <p className="text-neutral-600 mt-2">Occupational Health & Safety Management System</p>
      </div>

      {/* Login Form */}
      <form onSubmit={onSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Icon name="info" className="w-5 h-5 text-danger-600" />
              <span className="text-danger-600 text-sm font-medium">{error}</span>
            </div>
          </div>
        )}
        
        <div className="form-group">
          <label className="label">Email Address</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="user" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              placeholder="Enter your email"
              required 
            />
          </div>
        </div>
        
        <div className="form-group">
          <label className="label">Password</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="safety" className="w-5 h-5 text-neutral-400" />
            </div>
            <input 
              className="input pl-10" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Enter your password"
              required 
            />
          </div>
        </div>
        
        <Button 
          variant="primary" 
          size="lg"
          className="w-full" 
          type="submit" 
          loading={loading}
          icon={loading ? null : "safety"}
        >
          {loading ? 'Signing In...' : 'Sign In to SafeVisor'}
        </Button>
      </form>

      {/* Demo Credentials */}
      <div className="p-4 bg-neutral-50 rounded-lg border border-neutral-200">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3 flex items-center gap-2">
          <Icon name="info" className="w-4 h-4 text-primary-600" />
          Demo Credentials
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-2">
            <div>
              <span className="font-medium text-neutral-700">Admin:</span>
              <div className="text-neutral-600">admin@isg.local</div>
            </div>
            <div>
              <span className="font-medium text-neutral-700">Manager:</span>
              <div className="text-neutral-600">manager@isg.local</div>
            </div>
          </div>
          <div className="space-y-2">
            <div>
              <span className="font-medium text-neutral-700">HSE Officer:</span>
              <div className="text-neutral-600">hse@isg.local</div>
            </div>
            <div>
              <span className="font-medium text-neutral-700">Assistant:</span>
              <div className="text-neutral-600">assistant@isg.local</div>
            </div>
          </div>
        </div>
        <p className="text-xs text-neutral-500 mt-3">
          Use any of these emails with the password "password" to explore different role permissions.
        </p>
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-neutral-500">
        <p>© 2025 SafeVisor. Protecting your workplace, securing your future.</p>
      </div>
    </div>
  )
}
