import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, Button, Divider } from '@mui/material';
import AdminPanel from '../components/AdminPanel';
import { ENDPOINTS } from '../config';

function Dashboard() {
  const [token, setToken] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    setToken(storedToken || 'No token found');

    if (storedToken) {
      fetchUserInfo(storedToken);
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch(ENDPOINTS.ME, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors',
        credentials: 'same-origin'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserInfo(data);
        
        // Check if the user has the admin role
        const isUserAdmin = data.role === 'admin';
        setIsAdmin(isUserAdmin);
      } else {
        console.error('Failed to fetch user info:', await response.text());
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };



  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>



        {userInfo && (
          <Box 
            sx={{ 
              mb: 3, 
              p: 2, 
              borderRadius: 3,
              background: 'linear-gradient(135deg, #6a9ee5 0%, #9381ff 100%)',
              boxShadow: '0 4px 20px rgba(107, 155, 227, 0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: 2
            }}
          >
            <Box
              sx={{
                width: 50,
                height: 50,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'white',
                color: '#6a9ee5',
                fontSize: '1.5rem',
                fontWeight: 'bold'
              }}
            >
              {userInfo.username.charAt(0).toUpperCase()}
            </Box>
            <Typography 
              variant="h5" 
              sx={{ 
                color: 'white', 
                fontWeight: 600,
                fontSize: '1.5rem',
                letterSpacing: '0.02em',
                fontFamily: '"Comic Neue", "Baloo 2", sans-serif'
              }}
            >
              {userInfo.username}
            </Typography>
          </Box>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Your Progress
              </Typography>
              {/* Add progress content here */}
              {userInfo && userInfo.role === 'student' && (
                <Box sx={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  alignItems: 'center',
                  mt: 2, 
                  mb: 3, 
                  p: 2, 
                  bgcolor: 'primary.light',
                  borderRadius: 2
                }}>
                  <Typography variant="h5" gutterBottom color="primary.contrastText">
                    Punti totali
                  </Typography>
                  <Typography variant="h3" fontWeight="bold" color="primary.contrastText">
                    {userInfo.points || 0}
                  </Typography>
                </Box>
              )}
              <Typography paragraph>
                Track your quiz progress and performance statistics here.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Quizzes
              </Typography>
              {/* Add recent quizzes content here */}
              <Typography paragraph>
                View your recently taken quizzes and continue where you left off.
              </Typography>
            </Paper>
          </Grid>
        </Grid>


        {isAdmin ? (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 4 }} />
            <Typography variant="h5" component="h2" gutterBottom>
              Administration Panel
            </Typography>
            <Typography paragraph>
              As an administrator, you have access to additional features to manage the quiz application.
            </Typography>
            <AdminPanel token={token} />
          </Box>
        ) : null}
      </Box>
    </Container>
  );
}

export default Dashboard;
