import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, Button, Divider, Tab, Tabs } from '@mui/material';
import AdminPanel from '../components/AdminPanel';
import RewardManagement from '../components/RewardManagement';
import RewardShop from '../components/RewardShop';
import ParentRewardManagement from '../components/ParentRewardManagement';
import { ENDPOINTS } from '../config';

function Dashboard() {
  const [token, setToken] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [isParent, setIsParent] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    setToken(storedToken || 'No token found');

    if (storedToken) {
      fetchUserInfo(storedToken);
    }
  }, []);

  const fetchUserInfo = (token) => {
    if (!token) {
      console.error('No token provided for user info fetch');
      return;
    }
    
    console.log('Dashboard: Fetching user info with token:', token ? `${token.substring(0, 10)}...` : 'null');
    
    const xhr = new XMLHttpRequest();
    xhr.open('GET', ENDPOINTS.ME, true);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.withCredentials = false; // Disabilitato per evitare problemi CORS preflight
    
    xhr.onload = function() {
      console.log('Dashboard: User info response status:', xhr.status);
      
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          console.log('Dashboard: User info data received:', data);
          setUserInfo(data);
          
          // Check user roles
          const isUserAdmin = data.role === 'admin';
          const isUserParent = data.role === 'parent';
          setIsAdmin(isUserAdmin);
          setIsParent(isUserParent);
        } catch (e) {
          console.error('Error parsing user info JSON:', e);
        }
      } else {
        console.error(`Failed to fetch user info: ${xhr.status} ${xhr.statusText}`);
      }
    };
    
    xhr.onerror = function() {
      console.error('Network error occurred while fetching user info');
    };
    
    xhr.send();
  };



  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle points update after reward purchase
  const handlePointsUpdate = (newPointsValue) => {
    if (userInfo) {
      setUserInfo({
        ...userInfo,
        points: newPointsValue
      });
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


        {userInfo && userInfo.role === 'student' && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 4 }} />
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={tabValue} onChange={handleTabChange}>
                <Tab label="Dashboard" />
                <Tab label="Rewards Shop" />
              </Tabs>
            </Box>

            {tabValue === 0 ? (
              <Typography paragraph>
                More dashboard content would go here...
              </Typography>
            ) : (
              <RewardShop 
                token={token} 
                userPoints={userInfo.points || 0} 
                onPointsUpdated={handlePointsUpdate} 
              />
            )}
          </Box>
        )}

        {isParent && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 4 }} />
            <Typography variant="h5" component="h2" gutterBottom>
              Parent Management
            </Typography>
            <Typography paragraph>
              As a parent, you can manage rewards for your children.
            </Typography>
            <ParentRewardManagement token={token} />
          </Box>
        )}

        {isAdmin && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 4 }} />
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={tabValue} onChange={handleTabChange}>
                <Tab label="Quiz Management" />
                <Tab label="Reward Management" />
              </Tabs>
            </Box>

            {tabValue === 0 ? (
              <>
                <Typography variant="h5" component="h2" gutterBottom>
                  Administration Panel
                </Typography>
                <Typography paragraph>
                  As an administrator, you have access to additional features to manage the quiz application.
                </Typography>
                <AdminPanel token={token} />
              </>
            ) : (
              <>
                <Typography variant="h5" component="h2" gutterBottom>
                  Reward Management
                </Typography>
                <Typography paragraph>
                  Manage rewards that students can purchase with their points.
                </Typography>
                <RewardManagement token={token} />
              </>
            )}
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default Dashboard;
