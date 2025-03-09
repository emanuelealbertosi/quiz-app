import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, 
  LinearProgress, Button, Dialog, DialogTitle, 
  DialogContent, DialogActions, List, ListItem, 
  ListItemText, CircularProgress, Alert
} from '@mui/material';
import { Check as CheckIcon, Error as ErrorIcon } from '@mui/icons-material';
import axios from 'axios';
import { ENDPOINTS } from '../../config';

const PathProgress = () => {
  const [paths, setPaths] = useState([]);
  const [completedQuizzes, setCompletedQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [notification, setNotification] = useState(null);

  // Fetch assigned paths
  const fetchPaths = async () => {
    try {
      setLoading(true);
      const response = await axios.get(ENDPOINTS.MY_PATHS || '');
      setPaths(response.data || []);
      
      // Get completed quizzes
      const completedResponse = await axios.get(ENDPOINTS.COMPLETED_QUIZZES || '');
      setCompletedQuizzes(completedResponse.data ? completedResponse.data.map(q => q.quiz_id) : []);
      
      setLoading(false);
    } catch (err) {
      console.error('Errore nel recupero dei percorsi:', err);
      setError('Si è verificato un errore nel recupero dei percorsi assegnati.');
      setPaths([]); // Assicura che i percorsi siano un array vuoto in caso di errore
      setCompletedQuizzes([]);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPaths();
  }, []);

  const handleOpenDetails = (path) => {
    setSelectedPath(path);
    setOpenDialog(true);
  };

  const handleCloseDetails = () => {
    setOpenDialog(false);
  };
  
  const isQuizCompleted = (quizId) => {
    return completedQuizzes.includes(quizId);
  };
  
  const calculateProgress = (path) => {
    if (!path.quizzes || !Array.isArray(path.quizzes) || path.quizzes.length === 0) return 0;
    
    const completedCount = path.quizzes.filter(quiz => isQuizCompleted(quiz.id)).length;
    return (completedCount / path.quizzes.length) * 100;
  };
  
  const handleQuizClick = async (quiz, path) => {
    // Reindirizza alla pagina del quiz
    window.location.href = `/quiz/${quiz.id}`;
  };

  const renderPathStatus = (path) => {
    if (path.completed) {
      return (
        <Chip 
          icon={<CheckIcon />} 
          label="Completato" 
          color="success" 
          sx={{ fontWeight: 'bold' }} 
        />
      );
    }
    
    const progress = calculateProgress(path);
    return (
      <Box sx={{ width: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2">Progresso: {Math.round(progress)}%</Typography>
          <Typography variant="body2">
            {path.completed_quizzes || 0}/{path.quizzes.length} completati
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} />
      </Box>
    );
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" sx={{ mb: 3 }}>
        I Tuoi Percorsi
      </Typography>
      
      {notification && (
        <Alert 
          severity={notification.type} 
          sx={{ mb: 2 }}
          onClose={() => setNotification(null)}
        >
          {notification.message}
        </Alert>
      )}
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : paths.length === 0 ? (
        <Typography variant="body1" color="text.secondary">
          Non hai ancora nessun percorso assegnato.
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {paths.map(path => (
            <Grid item xs={12} sm={6} md={4} key={path.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="div" sx={{ mb: 1 }}>
                    {path.name}
                  </Typography>
                  
                  {path.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {path.description}
                    </Typography>
                  )}
                  
                  <Box sx={{ mb: 2 }}>
                    {renderPathStatus(path)}
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <Box component="span" sx={{ fontWeight: 'bold' }}>Bonus al completamento:</Box>{' '}
                    <Chip 
                      label={`+${path.bonus_points} punti`} 
                      color="primary" 
                      size="small" 
                    />
                  </Typography>
                  
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => handleOpenDetails(path)}
                    fullWidth
                    sx={{ mt: 1 }}
                  >
                    Dettagli
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Dialog per i dettagli del percorso */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDetails}
        maxWidth="sm"
        fullWidth
      >
        {selectedPath && (
          <>
            <DialogTitle>
              {selectedPath.name}
            </DialogTitle>
            <DialogContent>
              {selectedPath.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedPath.description}
                </Typography>
              )}
              
              <Box sx={{ mb: 3 }}>
                {renderPathStatus(selectedPath)}
              </Box>
              
              <Typography variant="h6" sx={{ mb: 1 }}>
                Quiz nel percorso:
              </Typography>
              
              <List>
                {(Array.isArray(selectedPath?.quizzes) ? selectedPath.quizzes : []).map(quiz => {
                  const completed = isQuizCompleted(quiz.id);
                  
                  return (
                    <ListItem 
                      key={quiz.id}
                      secondaryAction={
                        completed ? (
                          <Chip 
                            icon={<CheckIcon />} 
                            label="Completato" 
                            color="success" 
                            size="small" 
                          />
                        ) : (
                          <Button
                            variant="contained"
                            size="small"
                            onClick={() => handleQuizClick(quiz, selectedPath)}
                          >
                            Affronta
                          </Button>
                        )
                      }
                      sx={{
                        bgcolor: completed ? 'action.hover' : 'inherit',
                        borderRadius: 1,
                        mb: 1
                      }}
                    >
                      <ListItemText
                        primary={quiz.question}
                        secondary={`${quiz.points} punti`}
                        primaryTypographyProps={{
                          color: completed ? 'text.secondary' : 'text.primary',
                        }}
                      />
                    </ListItem>
                  );
                })}
              </List>
              
              {selectedPath.completed ? (
                <Alert 
                  severity="success" 
                  icon={<CheckIcon fontSize="inherit" />}
                  sx={{ mt: 2 }}
                >
                  Hai completato questo percorso! Hai guadagnato {selectedPath.bonus_points} punti bonus.
                </Alert>
              ) : (
                <Alert 
                  severity="info"
                  sx={{ mt: 2 }}
                >
                  Completa tutti i quiz per guadagnare {selectedPath.bonus_points} punti bonus!
                </Alert>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Chiudi</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default PathProgress;
