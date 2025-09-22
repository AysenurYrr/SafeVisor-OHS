import { useState } from 'react';
import { useAuth, UserRole } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [selectedRole, setSelectedRole] = useState(UserRole.ADMIN);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Demo login function - gets a real JWT token from backend
  const handleLogin = () => {
    login(selectedRole);
    navigate('/dashboard');
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h1>SafeVisor OHS Login</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="role-select" style={{ display: 'block', marginBottom: '8px' }}>
          Select Role (Demo):
        </label>
        <select
          id="role-select"
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
          style={{ padding: '8px', width: '100%' }}
        >
          <option value={UserRole.ADMIN}>Admin</option>
          <option value={UserRole.MANAGER}>Manager</option>
          <option value={UserRole.HSE_EXPERT}>HSE Expert</option>
          <option value={UserRole.IT_ADMIN}>IT Admin</option>
          <option value={UserRole.USER}>User</option>
        </select>
      </div>
      
      <button
        onClick={handleLogin}
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          width: '100%'
        }}
      >
        Login as {selectedRole}
      </button>
      
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p><strong>Demo Note:</strong> This is a demo login. In a real application, you would enter actual credentials.</p>
        <p>Only <strong>ADMIN</strong> and <strong>MANAGER</strong> roles can access the camera demo.</p>
      </div>
    </div>
  );
};

export default Login;