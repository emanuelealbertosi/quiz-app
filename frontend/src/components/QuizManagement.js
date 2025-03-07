import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  TextField, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer,
  TableHead, 
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Grid,
  Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { ENDPOINTS, API_BASE_URL } from '../config';

const QuizManagement = ({ token }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [difficultyLevels, setDifficultyLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [totalQuizzes, setTotalQuizzes] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(10);

  // Dialog states
  const [openQuizDialog, setOpenQuizDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add' or 'edit'
  const [currentQuiz, setCurrentQuiz] = useState({
    question: '',
    options: ['', '', '', ''],
    correct_answer: '',
    explanation: '',
    points: 10,
    difficulty_level_id: null,
    category_ids: []
  });

  useEffect(() => {
    fetchQuizzes();
    fetchCategories();
    fetchDifficultyLevels();
  }, [token, page, limit]);

  // Fetch quizzes with pagination
  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const skip = page * limit;
      const response = await fetch(`${ENDPOINTS.ADMIN.QUIZZES_MANAGEMENT}?skip=${skip}&limit=${limit}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quizzes');
      }

      const data = await response.json();
      setQuizzes(data.quizzes || []);
      setTotalQuizzes(data.total || 0);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
      setError(`Error fetching quizzes: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch categories for the select dropdown
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/categories`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }

      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
      setError(`Error fetching categories: ${error.message}`);
    }
  };

  // Fetch difficulty levels for the select dropdown
  const fetchDifficultyLevels = async () => {
    try {
      const response = await fetch(ENDPOINTS.ADMIN.DIFFICULTY_LEVELS, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch difficulty levels');
      }

      const data = await response.json();
      setDifficultyLevels(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching difficulty levels:', error);
      setError(`Error fetching difficulty levels: ${error.message}`);
    }
  };

  // Open dialog for adding a new quiz
  const handleOpenQuizDialog = (mode, quiz = null) => {
    setDialogMode(mode);
    if (mode === 'edit' && quiz) {
      // Format quiz data for editing
      setCurrentQuiz({
        ...quiz,
        category_ids: quiz.categories ? quiz.categories.map(cat => cat.id) : []
      });
    } else {
      // Reset form for adding a new quiz
      setCurrentQuiz({
        question: '',
        options: ['', '', '', ''],
        correct_answer: '',
        explanation: '',
        points: 10,
        difficulty_level_id: null,
        category_ids: []
      });
    }
    setOpenQuizDialog(true);
  };

  const handleCloseQuizDialog = () => {
    setOpenQuizDialog(false);
  };

  // Update quiz option at specific index
  const handleOptionChange = (index, value) => {
    const newOptions = [...currentQuiz.options];
    newOptions[index] = value;
    setCurrentQuiz({
      ...currentQuiz,
      options: newOptions
    });
  };

  // Add more option fields (up to 6)
  const handleAddOption = () => {
    if (currentQuiz.options.length < 6) {
      setCurrentQuiz({
        ...currentQuiz,
        options: [...currentQuiz.options, '']
      });
    }
  };

  // Remove option field
  const handleRemoveOption = (index) => {
    if (currentQuiz.options.length > 2) {
      const newOptions = currentQuiz.options.filter((_, i) => i !== index);
      setCurrentQuiz({
        ...currentQuiz,
        options: newOptions,
        // Reset correct answer if it was the removed option
        correct_answer: currentQuiz.correct_answer === currentQuiz.options[index] ? '' : currentQuiz.correct_answer
      });
    }
  };

  // Handle category selection
  const handleCategoryChange = (event) => {
    setCurrentQuiz({
      ...currentQuiz,
      category_ids: event.target.value
    });
  };

  // Save quiz (create or update)
  const handleSaveQuiz = async () => {
    try {
      const url = dialogMode === 'add' ? ENDPOINTS.ADMIN.QUIZZES_MANAGEMENT : `${ENDPOINTS.ADMIN.QUIZZES_MANAGEMENT}/${currentQuiz.id}`;
      const method = dialogMode === 'add' ? 'POST' : 'PUT';

      // Validate that all required fields are filled in
      if (!currentQuiz.question || !currentQuiz.correct_answer || currentQuiz.options.some(opt => !opt)) {
        setError('Please fill in all required fields (question, options, and correct answer)');
        return;
      }

      // Format the quiz data for the API
      const quizData = {
        question: currentQuiz.question,
        options: currentQuiz.options.filter(opt => opt), // Remove empty options
        correct_answer: currentQuiz.correct_answer,
        explanation: currentQuiz.explanation || '',
        points: parseInt(currentQuiz.points) || 10,
        difficulty_level_id: currentQuiz.difficulty_level_id,
        category_ids: currentQuiz.category_ids
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(quizData)
      });

      if (!response.ok) {
        throw new Error(`Failed to ${dialogMode === 'add' ? 'create' : 'update'} quiz`);
      }

      setSuccessMessage(`Quiz ${dialogMode === 'add' ? 'created' : 'updated'} successfully`);
      handleCloseQuizDialog();
      fetchQuizzes(); // Refresh quiz list
    } catch (error) {
      console.error(`Error ${dialogMode === 'add' ? 'creating' : 'updating'} quiz:`, error);
      setError(`Error ${dialogMode === 'add' ? 'creating' : 'updating'} quiz: ${error.message}`);
    }
  };

  // Delete quiz
  const handleDeleteQuiz = async (quizId) => {
    if (window.confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) {
      try {
        const response = await fetch(`${ENDPOINTS.ADMIN.QUIZZES_MANAGEMENT}/${quizId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to delete quiz');
        }

        setSuccessMessage('Quiz deleted successfully');
        fetchQuizzes(); // Refresh quiz list
      } catch (error) {
        console.error('Error deleting quiz:', error);
        setError(`Error deleting quiz: ${error.message}`);
      }
    }
  };

  // Update quiz points
  const handleUpdatePoints = async (quizId, currentPoints) => {
    const newPoints = prompt('Enter new points value:', currentPoints);
    
    if (newPoints !== null && !isNaN(newPoints) && newPoints.trim() !== '') {
      try {
        const response = await fetch(`${ENDPOINTS.ADMIN.QUIZZES_MANAGEMENT}/${quizId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ points: parseInt(newPoints) })
        });

        if (!response.ok) {
          throw new Error('Failed to update quiz points');
        }

        setSuccessMessage('Quiz points updated successfully');
        fetchQuizzes(); // Refresh quiz list
      } catch (error) {
        console.error('Error updating quiz points:', error);
        setError(`Error updating quiz points: ${error.message}`);
      }
    }
  };

  // Handle pagination
  const handleChangePage = (newPage) => {
    setPage(newPage);
  };

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Quiz Management</Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={() => handleOpenQuizDialog('add')}
        >
          Add New Quiz
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Question</TableCell>
                  <TableCell>Categories</TableCell>
                  <TableCell>Difficulty</TableCell>
                  <TableCell>Points</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {quizzes.length > 0 ? (
                  quizzes.map((quiz) => (
                    <TableRow key={quiz.id}>
                      <TableCell>{quiz.id}</TableCell>
                      <TableCell>
                        {quiz.question.length > 50 
                          ? `${quiz.question.substring(0, 50)}...` 
                          : quiz.question}
                      </TableCell>
                      <TableCell>
                        {quiz.categories && quiz.categories.map((category) => (
                          <Chip 
                            key={category.id} 
                            label={category.name} 
                            size="small" 
                            sx={{ m: 0.5 }}
                            style={{ 
                              backgroundColor: category.color || '#1976d2',
                              color: 'white'
                            }} 
                          />
                        ))}
                      </TableCell>
                      <TableCell>
                        {quiz.difficulty_level ? quiz.difficulty_level.name : 'N/A'}
                      </TableCell>
                      <TableCell>{quiz.points}</TableCell>
                      <TableCell>
                        <IconButton 
                          color="primary" 
                          onClick={() => handleOpenQuizDialog('edit', quiz)}
                          title="Edit quiz"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          color="secondary" 
                          onClick={() => handleUpdatePoints(quiz.id, quiz.points)}
                          title="Update points"
                        >
                          <i className="material-icons">stars</i>
                        </IconButton>
                        <IconButton 
                          color="error" 
                          onClick={() => handleDeleteQuiz(quiz.id)}
                          title="Delete quiz"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No quizzes found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination Controls */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 2 }}>
            <Button 
              disabled={page === 0} 
              onClick={() => handleChangePage(page - 1)}
            >
              Previous
            </Button>
            <Typography>
              Page {page + 1} of {Math.ceil(totalQuizzes / limit)}
            </Typography>
            <Button 
              disabled={page >= Math.ceil(totalQuizzes / limit) - 1} 
              onClick={() => handleChangePage(page + 1)}
            >
              Next
            </Button>
          </Box>
        </>
      )}

      {/* Dialog for creating/editing quizzes */}
      <Dialog open={openQuizDialog} onClose={handleCloseQuizDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Quiz' : 'Edit Quiz'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {dialogMode === 'add' 
              ? 'Create a new quiz with questions, options, and answers.' 
              : 'Edit the existing quiz details.'}
          </DialogContentText>
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                margin="dense"
                label="Question"
                type="text"
                fullWidth
                multiline
                rows={2}
                variant="outlined"
                value={currentQuiz.question}
                onChange={(e) => setCurrentQuiz({...currentQuiz, question: e.target.value})}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Options</Typography>
              {currentQuiz.options.map((option, index) => (
                <Box key={index} sx={{ display: 'flex', mb: 1 }}>
                  <TextField
                    margin="dense"
                    label={`Option ${index + 1}`}
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={option}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    required
                  />
                  {index > 1 && (
                    <IconButton 
                      color="error" 
                      onClick={() => handleRemoveOption(index)}
                      sx={{ mt: 1 }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
              ))}
              
              {currentQuiz.options.length < 6 && (
                <Button 
                  variant="outlined" 
                  startIcon={<AddIcon />} 
                  onClick={handleAddOption}
                  sx={{ mt: 1 }}
                >
                  Add Option
                </Button>
              )}
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="outlined" margin="dense">
                <InputLabel id="correct-answer-label">Correct Answer</InputLabel>
                <Select
                  labelId="correct-answer-label"
                  value={currentQuiz.correct_answer}
                  onChange={(e) => setCurrentQuiz({...currentQuiz, correct_answer: e.target.value})}
                  label="Correct Answer"
                  required
                >
                  {currentQuiz.options.map((option, index) => (
                    option && (
                      <MenuItem key={index} value={option}>
                        {option}
                      </MenuItem>
                    )
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                margin="dense"
                label="Points"
                type="number"
                fullWidth
                variant="outlined"
                value={currentQuiz.points}
                onChange={(e) => setCurrentQuiz({...currentQuiz, points: e.target.value})}
                InputProps={{ inputProps: { min: 1 } }}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="outlined" margin="dense">
                <InputLabel id="difficulty-level-label">Difficulty Level</InputLabel>
                <Select
                  labelId="difficulty-level-label"
                  value={currentQuiz.difficulty_level_id || ''}
                  onChange={(e) => setCurrentQuiz({...currentQuiz, difficulty_level_id: e.target.value})}
                  label="Difficulty Level"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {difficultyLevels.map((level) => (
                    <MenuItem key={level.id} value={level.id}>
                      {level.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="outlined" margin="dense">
                <InputLabel id="categories-label">Categories</InputLabel>
                <Select
                  labelId="categories-label"
                  multiple
                  value={currentQuiz.category_ids || []}
                  onChange={handleCategoryChange}
                  label="Categories"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((categoryId) => {
                        const category = categories.find(cat => cat.id === categoryId);
                        return category ? (
                          <Chip 
                            key={category.id} 
                            label={category.name} 
                            size="small"
                            style={{ 
                              backgroundColor: category.color || '#1976d2',
                              color: 'white'
                            }}
                          />
                        ) : null;
                      })}
                    </Box>
                  )}
                >
                  {categories.map((category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Explanation (Optional)"
                type="text"
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                value={currentQuiz.explanation || ''}
                onChange={(e) => setCurrentQuiz({...currentQuiz, explanation: e.target.value})}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseQuizDialog}>Cancel</Button>
          <Button onClick={handleSaveQuiz} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QuizManagement;
