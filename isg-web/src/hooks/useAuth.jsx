// Authentication context and utilities
import { createContext, useContext, useState, useEffect } from 'react';

export const UserRole = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  HSE_EXPERT: 'HSE_EXPERT',
  IT_ADMIN: 'IT_ADMIN',
  USER: 'USER'
};

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // For demo purposes, get a real token from the backend
      fetch(`/api/v1/auth/demo-token/${localStorage.getItem('selectedRole') || 'ADMIN'}`)
        .then(response => response.json())
        .then(data => {
          if (data.access_token) {
            const realToken = data.access_token;
            localStorage.setItem('token', realToken);
            setToken(realToken);
            
            // Decode JWT token to get user info
            try {
              const payload = JSON.parse(atob(realToken.split('.')[1]));
              setUser({
                username: payload.sub,
                role: payload.role
              });
            } catch (error) {
              console.error('Invalid token:', error);
              localStorage.removeItem('token');
              setToken(null);
            }
          }
        })
        .catch(error => {
          console.error('Error getting token:', error);
          localStorage.removeItem('token');
          setToken(null);
        });
    }
  }, []);

  const login = (role) => {
    localStorage.setItem('selectedRole', role);
    // Get real token from backend
    fetch(`/api/v1/auth/demo-token/${role}`)
      .then(response => response.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem('token', data.access_token);
          setToken(data.access_token);
          
          // Decode JWT token to get user info
          try {
            const payload = JSON.parse(atob(data.access_token.split('.')[1]));
            setUser({
              username: payload.sub,
              role: payload.role
            });
          } catch (error) {
            console.error('Invalid token:', error);
          }
        }
      })
      .catch(error => {
        console.error('Login error:', error);
      });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('selectedRole');
    setToken(null);
    setUser(null);
  };

  const hasRole = (roles) => {
    if (!user) return false;
    return Array.isArray(roles) ? roles.includes(user.role) : user.role === roles;
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};