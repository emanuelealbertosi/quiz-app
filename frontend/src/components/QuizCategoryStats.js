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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { ENDPOINTS } from '../config';

const QuizCategoryStats = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategoryStats = async () => {
      try {
        setLoading(true);
        const response = await fetch(ENDPOINTS.ADMIN.QUIZ_CATEGORIES_STATS, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch category statistics');
        }
        
        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (error) {
        console.error('Error fetching category statistics:', error);
        setError('Error fetching category statistics: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryStats();
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
        Quiz Category Statistics
      </Typography>
      
      {/* Total Categories */}
      <Card raised sx={{ mb: 4 }}>
        <CardHeader title="Total Categories" />
        <CardContent>
          <Typography variant="h3" align="center">
            {stats.total_categories}
          </Typography>
        </CardContent>
      </Card>

      {/* Popular Categories */}
      <Typography variant="h6" gutterBottom>
        Most Popular Categories (by number of quizzes)
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell align="right">Number of Quizzes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.popular_categories.length > 0 ? (
              stats.popular_categories.map((category, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {category.category}
                  </TableCell>
                  <TableCell align="right">{category.quiz_count}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={2} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Most Attempted Categories */}
      <Typography variant="h6" gutterBottom>
        Most Attempted Categories
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell align="right">Number of Attempts</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.most_attempted_categories.length > 0 ? (
              stats.most_attempted_categories.map((category, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {category.category}
                  </TableCell>
                  <TableCell align="right">{category.attempts_count}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={2} align="center">
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Best Accuracy Categories */}
      <Typography variant="h6" gutterBottom>
        Categories with Best Accuracy
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell align="right">Total Attempts</TableCell>
              <TableCell align="right">Correct Answers</TableCell>
              <TableCell align="right">Accuracy</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stats.best_accuracy_categories.length > 0 ? (
              stats.best_accuracy_categories.map((category, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {category.category}
                  </TableCell>
                  <TableCell align="right">{category.total_attempts}</TableCell>
                  <TableCell align="right">{category.correct_answers}</TableCell>
                  <TableCell align="right">{category.accuracy}%</TableCell>
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

      {/* Categories by Path */}
      <Typography variant="h6" gutterBottom>
        Categories by Quiz Path
      </Typography>
      {Object.keys(stats.categories_by_path).length > 0 ? (
        Object.entries(stats.categories_by_path).map(([pathName, categories], index) => (
          <Accordion key={index} sx={{ mb: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">{pathName}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Number of Quizzes</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {categories.map((category, idx) => (
                      <TableRow key={idx}>
                        <TableCell component="th" scope="row">
                          {category.category}
                        </TableCell>
                        <TableCell align="right">{category.quiz_count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        ))
      ) : (
        <Alert severity="info">No path data available</Alert>
      )}
    </Box>
  );
};

export default QuizCategoryStats;
