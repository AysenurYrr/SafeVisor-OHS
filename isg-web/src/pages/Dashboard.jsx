import { Link } from 'react-router-dom';
import { useAuth, UserRole } from '../hooks/useAuth';

const Dashboard = () => {
  const { user, logout, hasRole } = useAuth();

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>SafeVisor OHS Dashboard</h1>
        <button
          onClick={logout}
          style={{
            padding: '8px 16px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <p><strong>Welcome, {user?.username || 'User'}!</strong></p>
        <p>Role: <span style={{ color: '#007bff', fontWeight: 'bold' }}>{user?.role}</span></p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px' }}>
          <h3>Features</h3>
          <ul>
            <li>Safety Monitoring</li>
            <li>Incident Reporting</li>
            <li>Compliance Tracking</li>
            <li>Risk Assessment</li>
          </ul>
        </div>
        
        {hasRole([UserRole.ADMIN, UserRole.MANAGER]) && (
          <div style={{ border: '1px solid #007bff', borderRadius: '8px', padding: '20px', backgroundColor: '#f8f9fa' }}>
            <h3>Camera Monitoring</h3>
            <p>Access camera feeds and demo videos for safety monitoring.</p>
            <Link
              to="/cameras"
              style={{
                display: 'inline-block',
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                marginTop: '10px'
              }}
            >
              View Camera Demo
            </Link>
          </div>
        )}
        
        <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px' }}>
          <h3>Quick Actions</h3>
          <ul>
            <li>Submit Safety Report</li>
            <li>View Incidents</li>
            <li>Check Compliance Status</li>
            <li>Generate Reports</li>
          </ul>
        </div>
      </div>
      
      {!hasRole([UserRole.ADMIN, UserRole.MANAGER]) && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff3cd', border: '1px solid #ffeaa7', borderRadius: '4px' }}>
          <p><strong>Note:</strong> Camera monitoring features are only available to users with ADMIN or MANAGER roles.</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;