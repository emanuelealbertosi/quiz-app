import React, { useState } from 'react';
import { Container, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function TestRedirect() {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');

  const handleTestRedirect = () => {
    setMessage('Attempting to redirect to dashboard using navigate...');
    try {
      navigate('/dashboard');
      setMessage('Navigation function called. Check if page changed.');
    } catch (error) {
      setMessage('Error during navigation: ' + error.message);
    }
  };

  const handleTestWindowLocation = () => {
    setMessage('Attempting to redirect to dashboard using window.location...');
    try {
      window.location.href = '/dashboard';
      setMessage('Window location changed. Page should be reloading.');
    } catch (error) {
      setMessage('Error during redirect: ' + error.message);
    }
  };

  const handleSetToken = () => {
    try {
      localStorage.setItem('token', 'test-token');
      setMessage('Test token set in localStorage');
    } catch (error) {
      setMessage('Error setting token: ' + error.message);
    }
  };

  const handleClearToken = () => {
    try {
      localStorage.removeItem('token');
      setMessage('Token removed from localStorage');
    } catch (error) {
      setMessage('Error removing token: ' + error.message);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Redirect Test Page
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleTestRedirect}
            sx={{ mr: 2 }}
          >
            Test Navigate to Dashboard
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleTestWindowLocation}
            sx={{ mr: 2 }}
          >
            Test Window.Location Redirect
          </Button>
          <Button 
            variant="contained" 
            color="secondary" 
            onClick={handleSetToken}
            sx={{ mr: 2 }}
          >
            Set Test Token
          </Button>
          <Button 
            variant="outlined" 
            color="error" 
            onClick={handleClearToken}
          >
            Clear Token
          </Button>
        </Box>
        {message && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography>{message}</Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default TestRedirect;
