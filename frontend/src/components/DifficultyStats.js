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
  Divider,
  LinearProgress
} from '@mui/material';
import { ENDPOINTS } from '../config';

const DifficultyStats = ({ token }) => {
  const [difficultyLevels, setDifficultyLevels] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch difficulty levels
        const difficultyResponse = await fetch(ENDPOINTS.ADMIN.DIFFICULTY_LEVELS, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (!difficultyResponse.ok) {
          throw new Error('Failed to fetch difficulty levels');
        }
        
        const difficultyData = await difficultyResponse.json();
        setDifficultyLevels(difficultyData);
        
        // Fetch quiz stats
        const statsResponse = await fetch(ENDPOINTS.ADMIN.STATS, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (!statsResponse.ok) {
          throw new Error('Failed to fetch quiz statistics');
        }
        
        const statsData = await statsResponse.json();
        setStats(statsData);
        
        setError(null);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Error fetching data: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token]);

  // Calculate stats by difficulty level
  const calculateDifficultyStats = () => {
    if (!stats || !difficultyLevels || !difficultyLevels.length) return [];
    
    const difficultyStats = [];
    
    // Process quiz attempts by difficulty
    const quizzesByDifficulty = {};
    const attemptsByDifficulty = {};
    const successByDifficulty = {};
    
    // Initialize counters
    difficultyLevels.forEach(level => {
      if (level && level.id) {
        quizzesByDifficulty[level.id] = 0;
        attemptsByDifficulty[level.id] = 0;
        successByDifficulty[level.id] = 0;
      }
    });
    
    // Count quizzes by difficulty
    if (stats && stats.most_attempted_quizzes && Array.isArray(stats.most_attempted_quizzes)) {
      stats.most_attempted_quizzes.forEach(quiz => {
        if (quiz && quiz.difficulty_level_id && quizzesByDifficulty[quiz.difficulty_level_id] !== undefined) {
          quizzesByDifficulty[quiz.difficulty_level_id] = 
            (quizzesByDifficulty[quiz.difficulty_level_id] || 0) + 1;
          attemptsByDifficulty[quiz.difficulty_level_id] = 
            (attemptsByDifficulty[quiz.difficulty_level_id] || 0) + (quiz.attempts || 0);
          successByDifficulty[quiz.difficulty_level_id] = 
            (successByDifficulty[quiz.difficulty_level_id] || 0) + ((quiz.attempts || 0) * (quiz.success_rate || 0));
        }
      });
    }
    
    // Calculate stats for each difficulty level
    difficultyLevels.forEach(level => {
      if (level && level.id) {
        const attempts = attemptsByDifficulty[level.id] || 0;
        const successRate = attempts > 0 ? (successByDifficulty[level.id] / attempts) : 0;
        
        difficultyStats.push({
          id: level.id,
          name: level.name || 'Unknown',
          value: level.value || 0,
          quizCount: quizzesByDifficulty[level.id] || 0,
          attempts: attempts,
          successRate: successRate
        });
      }
    });
    
    // Sort by difficulty value
    return difficultyStats.sort((a, b) => a.value - b.value);
  };

  const difficultyStats = calculateDifficultyStats();

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

  return (
    <Box sx={{ flexGrow: 1, mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        Quiz Difficulty Statistics
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {difficultyLevels && difficultyLevels.length > 0 ? (
          difficultyLevels.map(level => {
            if (!level || !level.id) return null;
            
            const statData = difficultyStats.find(stat => stat.id === level.id);
            
            return (
              <Grid item xs={12} sm={6} md={4} key={level.id}>
                <Card raised>
                  <CardHeader 
                    title={level.name || 'Unknown'} 
                    titleTypographyProps={{ align: 'center' }}
                    sx={{
                      backgroundColor: (theme) => theme.palette.mode === 'light' 
                        ? theme.palette.grey[200] 
                        : theme.palette.grey[700],
                    }}
                  />
                  <CardContent>
                    {statData ? (
                      <>
                        <Typography variant="body1">
                          <strong>Quizzes:</strong> {statData.quizCount}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Attempts:</strong> {statData.attempts}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Success Rate:</strong> {(statData.successRate * 100).toFixed(2)}%
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          <Box sx={{ width: '100%', mr: 1 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={statData.successRate * 100} 
                              color={
                                statData.successRate > 0.7 ? "success" : 
                                statData.successRate > 0.4 ? "warning" : "error"
                              }
                            />
                          </Box>
                        </Box>
                      </>
                    ) : (
                      <Typography variant="body2" color="text.secondary" align="center">
                        No data available
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })
        ) : (
          <Grid item xs={12}>
            <Alert severity="info">No difficulty levels found</Alert>
          </Grid>
        )}
      </Grid>
      
      <Divider sx={{ my: 4 }} />
      
      <Typography variant="h6" gutterBottom>
        Difficulty Level Comparison
      </Typography>
      
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Difficulty Level</TableCell>
              <TableCell align="right">Quizzes</TableCell>
              <TableCell align="right">Attempts</TableCell>
              <TableCell align="right">Success Rate</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {difficultyStats && difficultyStats.length > 0 ? (
              difficultyStats.map((stat) => (
                <TableRow key={stat.id}>
                  <TableCell component="th" scope="row">
                    {stat.name}
                  </TableCell>
                  <TableCell align="right">{stat.quizCount}</TableCell>
                  <TableCell align="right">{stat.attempts}</TableCell>
                  <TableCell align="right">{(stat.successRate * 100).toFixed(2)}%</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">No data available</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DifficultyStats;
