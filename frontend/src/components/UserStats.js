import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert
} from '@mui/material';
import { ENDPOINTS } from '../config';

const UserStats = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUserStats = () => {
      if (!token) {
        setError('Authentication error: No token found');
        setLoading(false);
        return;
      }
      
      setLoading(true);
      console.log('Fetching user stats with token:', token ? `${token.substring(0, 10)}...` : 'null');
      
      // Using XMLHttpRequest instead of fetch for better compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('GET', ENDPOINTS.ADMIN.USERS_STATS, true);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.withCredentials = false; // Set to false to prevent CORS preflight issues
      
      xhr.onload = function() {
        console.log('User stats response status:', xhr.status);
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('User stats data received:', data);
            setStats(data);
            setError(null);
          } catch (e) {
            console.error('Error parsing JSON from user stats endpoint:', e);
            setError('Error parsing user statistics data');
          }
        } else {
          console.error(`Failed to fetch user statistics: ${xhr.status} ${xhr.statusText}`);
          setError(`Failed to fetch user statistics: ${xhr.status} ${xhr.statusText}`);
        }
        setLoading(false);
      };
      
      xhr.onerror = function() {
        console.error('Network error occurred while fetching user statistics');
        setError('Network error occurred while fetching user statistics');
        setLoading(false);
      };
      
      xhr.send();
    };

    fetchUserStats();
  }, [token]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        No statistics available.
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        User Statistics Dashboard
      </Typography>
      
      {/* General Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card raised>
            <CardHeader title="Total Users" />
            <CardContent>
              <Typography variant="h3" align="center">
                {stats.general.total_users}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card raised>
            <CardHeader title="Active Users" />
            <CardContent>
              <Typography variant="h3" align="center" color="success.main">
                {stats.general.active_users}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card raised>
            <CardHeader title="Inactive Users" />
            <CardContent>
              <Typography variant="h3" align="center" color="error.main">
                {stats.general.inactive_users}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Role Statistics */}
      <Typography variant="h6" gutterBottom>
        Users by Role
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Role</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="right">Active</TableCell>
              <TableCell align="right">Inactive</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(stats.role_stats).map(([role, data]) => (
              <TableRow key={role}>
                <TableCell component="th" scope="row">
                  {role.charAt(0).toUpperCase() + role.slice(1)}
                </TableCell>
                <TableCell align="right">{data.total}</TableCell>
                <TableCell align="right">{data.active}</TableCell>
                <TableCell align="right">{data.inactive}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Top Students */}
      <Typography variant="h6" gutterBottom>
        Top Students by Points
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell align="right">Points</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.top_students.length > 0 ? (
              stats.top_students.map((student) => (
                <TableRow key={student.id}>
                  <TableCell component="th" scope="row">
                    {student.username}
                  </TableCell>
                  <TableCell>{student.email}</TableCell>
                  <TableCell align="right">{student.points}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Most Active Students */}
      <Typography variant="h6" gutterBottom>
        Most Active Students
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell align="right">Points</TableCell>
              <TableCell align="right">Quiz Attempts</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.most_active_students.length > 0 ? (
              stats.most_active_students.map((student) => (
                <TableRow key={student.id}>
                  <TableCell component="th" scope="row">
                    {student.username}
                  </TableCell>
                  <TableCell>{student.email}</TableCell>
                  <TableCell align="right">{student.points}</TableCell>
                  <TableCell align="right">{student.attempts_count}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Best Accuracy Students */}
      <Typography variant="h6" gutterBottom>
        Students with Best Accuracy
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell align="right">Attempts</TableCell>
              <TableCell align="right">Correct</TableCell>
              <TableCell align="right">Accuracy</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.best_accuracy_students.length > 0 ? (
              stats.best_accuracy_students.map((student) => (
                <TableRow key={student.id}>
                  <TableCell component="th" scope="row">
                    {student.username}
                  </TableCell>
                  <TableCell>{student.email}</TableCell>
                  <TableCell align="right">{student.total_attempts}</TableCell>
                  <TableCell align="right">{student.correct_answers}</TableCell>
                  <TableCell align="right">{student.accuracy}%</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default UserStats;
