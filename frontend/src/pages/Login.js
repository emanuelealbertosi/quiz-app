import React, { useState } from 'react';
import { Container, Paper, TextField, Button, Typography, Box, CircularProgress, Backdrop } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../config';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Prepara i dati del form
      const formBody = `username=${encodeURIComponent(formData.username)}&password=${encodeURIComponent(formData.password)}`;
      
      console.log('Logging in with URL:', ENDPOINTS.LOGIN);
      
      // First test if server is reachable at all
      try {
        const healthCheck = await fetch(`${window.location.origin}/health`, {
          method: 'GET',
        });
        console.log('Health check response:', healthCheck.status, await healthCheck.text());
      } catch (healthError) {
        console.error('Health check failed:', healthError);
      }
      
      // Now try the actual login
      const response = await fetch(ENDPOINTS.LOGIN, {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': '*/*',
        },
        body: formBody,
      });
      
      console.log('Login response status:', response.status);
      console.log('Login response headers:', Object.fromEntries([...response.headers]));
      
      const responseText = await response.text();
      console.log('Login response text:', responseText);
      
      if (response.ok) {
        try {
          const data = JSON.parse(responseText);
          console.log('Login successful, token received');
          localStorage.setItem('token', data.access_token);
          window.location.href = '/dashboard';
        } catch (e) {
          console.error('Error parsing JSON:', e);
          alert('Error parsing server response: ' + e.message);
          setLoading(false);
        }
      } else {
        // Handle error
        console.error('Login failed with status:', response.status);
        alert('Login failed: ' + responseText);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error during login:', error);
      console.error('Error details:', error.message, error.stack);
      alert('Error during login: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      {/* Loading indicator */}
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          flexDirection: 'column',
          gap: 2
        }}
        open={loading}
      >
        <CircularProgress color="primary" size={60} thickness={4} />
        <Typography variant="h6" color="white">
          Accesso in corso...
        </Typography>
      </Backdrop>
      
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Login
          </Typography>
          <Box sx={{ mb: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
            <Typography variant="body2">
              <strong>Credenziali di test:</strong><br />
              Username: <strong>admin</strong><br />
              Password: <strong>admin</strong>
            </Typography>
          </Box>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              sx={{ mt: 3 }}
            >
              Login
            </Button>
          </form>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2">
              Don't have an account?{' '}
              <Button color="primary" onClick={() => navigate('/register')}>
                Register
              </Button>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default Login;
