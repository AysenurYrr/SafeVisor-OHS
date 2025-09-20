import React from 'react'
import Icon from './Icon'
import Loading from './Loading'

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  icon, 
  iconPosition = 'left',
  loading = false,
  disabled = false,
  className = '',
  ...props 
}) {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    success: 'btn-success',
    danger: 'btn-danger',
    ghost: 'btn-ghost'
  }
  
  const sizes = {
    sm: 'btn-sm',
    md: '',
    lg: 'btn-lg'
  }
  
  const baseClasses = variants[variant] || variants.primary
  const sizeClasses = sizes[size] || ''
  
  const isDisabled = disabled || loading
  
  return (
    <button 
      className={`${baseClasses} ${sizeClasses} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {loading && <Loading type="spinner" size="sm" />}
      {!loading && icon && iconPosition === 'left' && (
        <Icon name={icon} className="w-4 h-4" />
      )}
      {children}
      {!loading && icon && iconPosition === 'right' && (
        <Icon name={icon} className="w-4 h-4" />
      )}
    </button>
  )
}