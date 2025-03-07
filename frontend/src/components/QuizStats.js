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
  Alert,
  Divider
} from '@mui/material';
import { ENDPOINTS } from '../config';

const QuizStats = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuizStats = async () => {
      try {
        setLoading(true);
        const response = await fetch(ENDPOINTS.ADMIN.STATS, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch quiz statistics');
        }
        
        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (error) {
        console.error('Error fetching quiz statistics:', error);
        setError('Error fetching quiz statistics: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchQuizStats();
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
        Quiz System Statistics
      </Typography>
      
      <Grid container spacing={3}>
        {/* Quiz Stats */}
        <Grid item xs={12} md={6}>
          <Card raised sx={{ height: '100%' }}>
            <CardHeader title="Quiz Statistics" />
            <CardContent>
              <Typography variant="body1">
                <strong>Total Quizzes:</strong> {stats.total_quizzes}
              </Typography>
              <Typography variant="body1">
                <strong>Total Quiz Attempts:</strong> {stats.total_attempts}
              </Typography>
              <Typography variant="body1">
                <strong>Average Score:</strong> {stats.average_score ? stats.average_score.toFixed(2) : 'N/A'}
              </Typography>
              <Typography variant="body1">
                <strong>Success Rate:</strong> {stats.success_rate ? (stats.success_rate * 100).toFixed(2) + '%' : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Path Stats */}
        <Grid item xs={12} md={6}>
          <Card raised sx={{ height: '100%' }}>
            <CardHeader title="Path Statistics" />
            <CardContent>
              <Typography variant="body1">
                <strong>Total Paths:</strong> {stats.total_paths}
              </Typography>
              <Typography variant="body1">
                <strong>Most Popular Path:</strong> {stats.most_popular_path ? stats.most_popular_path.name : 'N/A'}
              </Typography>
              <Typography variant="body1">
                <strong>Most Difficult Path:</strong> {stats.most_difficult_path ? stats.most_difficult_path.name : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 4 }} />
      
      {/* Top Quizzes */}
      <Typography variant="h6" gutterBottom>
        Most Attempted Quizzes
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Question</TableCell>
              <TableCell align="right">Attempts</TableCell>
              <TableCell align="right">Success Rate</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.most_attempted_quizzes && stats.most_attempted_quizzes.length > 0 ? (
              stats.most_attempted_quizzes.map((quiz, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {quiz.question.length > 100 ? quiz.question.substring(0, 100) + '...' : quiz.question}
                  </TableCell>
                  <TableCell align="right">{quiz.attempts}</TableCell>
                  <TableCell align="right">{(quiz.success_rate * 100).toFixed(2)}%</TableCell>
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
      
      {/* Hardest Quizzes */}
      <Typography variant="h6" gutterBottom>
        Hardest Quizzes (Lowest Success Rate)
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Question</TableCell>
              <TableCell align="right">Attempts</TableCell>
              <TableCell align="right">Success Rate</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.hardest_quizzes && stats.hardest_quizzes.length > 0 ? (
              stats.hardest_quizzes.map((quiz, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {quiz.question.length > 100 ? quiz.question.substring(0, 100) + '...' : quiz.question}
                  </TableCell>
                  <TableCell align="right">{quiz.attempts}</TableCell>
                  <TableCell align="right">{(quiz.success_rate * 100).toFixed(2)}%</TableCell>
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
    </Box>
  );
};

export default QuizStats;
