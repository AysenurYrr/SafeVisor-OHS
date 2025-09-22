import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';

const Cameras = () => {
  const { token } = useAuth();
  const [videoError, setVideoError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [demoMessage, setDemoMessage] = useState('');
  const videoRef = useRef(null);

  const handleVideoLoad = () => {
    setLoading(false);
    setVideoError(false);
  };

  const handleVideoError = () => {
    setLoading(false);
    setVideoError(true);
  };

  // Load the video with authentication
  useEffect(() => {
    if (token && videoRef.current) {
      setLoading(true);
      setVideoError(false);
      setDemoMessage('');
      
      fetch('/api/v1/cameras/demo', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) {
          // Check if it's a demo placeholder
          const isDemo = response.headers.get('X-Demo');
          if (isDemo) {
            return response.text().then(text => {
              setDemoMessage(text);
              setLoading(false);
              return null;
            });
          } else {
            return response.blob();
          }
        }
        throw new Error(`Failed to load video: ${response.status} ${response.statusText}`);
      })
      .then(blob => {
        if (blob && videoRef.current) {
          const videoUrl = URL.createObjectURL(blob);
          videoRef.current.src = videoUrl;
          setLoading(false);
          setVideoError(false);
        }
      })
      .catch(error => {
        console.error('Error loading video:', error);
        setLoading(false);
        setVideoError(true);
      });
    }
  }, [token]);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Camera Demo</h1>
      <p>Demo video stream for safety monitoring cameras.</p>
      
      <div style={{ marginTop: '20px' }}>
        {loading && <p>Loading video...</p>}
        
        {demoMessage && (
          <div style={{ color: 'blue', padding: '20px', border: '1px solid blue', borderRadius: '4px', backgroundColor: '#e7f3ff' }}>
            <h3>Demo Mode</h3>
            <p>{demoMessage}</p>
            <p>The video streaming endpoint is working correctly and accessible only to ADMIN/MANAGER users.</p>
            <p>To use with a real video:</p>
            <ol>
              <li>Replace the demo.mp4 file in <code>isg-api/app/static/videos/</code> with an actual MP4 video file</li>
              <li>Ensure the file is H.264 encoded for browser compatibility</li>
              <li>The video will then play in this player with proper authentication</li>
            </ol>
          </div>
        )}
        
        {videoError ? (
          <div style={{ color: 'red', padding: '20px', border: '1px solid red', borderRadius: '4px' }}>
            <h3>Video Error</h3>
            <p>Unable to load the demo video. This might be because:</p>
            <ul>
              <li>The video file is missing on the server</li>
              <li>You don't have permission to access this video</li>
              <li>There's a network connection issue</li>
            </ul>
          </div>
        ) : (
          !demoMessage && (
            <video
              ref={videoRef}
              width="800"
              height="450"
              controls
              onLoadedData={handleVideoLoad}
              onError={handleVideoError}
              style={{ maxWidth: '100%', border: '1px solid #ccc' }}
            >
              Your browser does not support the video tag.
            </video>
          )
        )}
      </div>
      
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p><strong>Note:</strong> Only users with ADMIN or MANAGER roles can access this demo video.</p>
        <p><strong>API Endpoint:</strong> <code>GET /api/v1/cameras/demo</code> (requires Bearer token authentication)</p>
      </div>
    </div>
  );
};

export default Cameras;