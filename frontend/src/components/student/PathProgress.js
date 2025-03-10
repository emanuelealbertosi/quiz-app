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
  const [completedQuizzes, setCompletedQuizzes] = useState([]); // Quiz completati globalmente
  const [pathCompletedQuizzes, setPathCompletedQuizzes] = useState({}); // Mappa pathId -> array di quiz completati
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [notification, setNotification] = useState(null);

  // Fetch assigned paths
  const fetchPaths = async () => {
    try {
      setLoading(true);
      console.log(`Richiesta percorsi studente a: ${ENDPOINTS.MY_PATHS}`);
      const response = await axios.get(ENDPOINTS.MY_PATHS || '');
      console.log('Risposta ricevuta dal server per i percorsi:', response);
      setPaths(response.data || []);
      
      // Get completed quizzes (ancora necessario per compatibilità con quiz standard)
      const completedResponse = await axios.get(ENDPOINTS.COMPLETED_QUIZZES || '');
      setCompletedQuizzes(completedResponse.data ? completedResponse.data.map(q => q.quiz_id) : []);
      
      // Ora carica anche i quiz completati per ciascun percorso
      if (response.data && Array.isArray(response.data)) {
        console.log(`Percorsi trovati: ${response.data.length}`);
        const pathQuizzes = {};
        
        for (const path of response.data) {
          try {
            // Ottieni i quiz completati per questo percorso specifico
            const pathCompletedResponse = await axios.get(ENDPOINTS.PATH_COMPLETED_QUIZZES(path.id) || '');
            pathQuizzes[path.id] = pathCompletedResponse.data || [];
            console.log(`Quiz completati per il percorso ${path.id}:`, pathQuizzes[path.id]);
          } catch (err) {
            console.error(`Errore nel recupero dei quiz completati per il percorso ${path.id}:`, err);
            pathQuizzes[path.id] = [];
          }
        }
        
        setPathCompletedQuizzes(pathQuizzes);
      } else {
        console.log('Nessun percorso trovato o risposta in formato non valido:', response.data);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Errore nel recupero dei percorsi:', err);
      setError('Si è verificato un errore nel recupero dei percorsi assegnati.');
      setPaths([]); // Assicura che i percorsi siano un array vuoto in caso di errore
      setCompletedQuizzes([]);
      setPathCompletedQuizzes({});
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
  
  const isQuizCompleted = (quizId, pathId) => {
    // Verifica prima se abbiamo i dati specifici per il percorso
    if (pathCompletedQuizzes[pathId] && Array.isArray(pathCompletedQuizzes[pathId])) {
      return pathCompletedQuizzes[pathId].includes(quizId);
    }
    
    // Fallback al vecchio metodo per compatibilità
    return completedQuizzes.includes(quizId);
  };
  
  const calculateProgress = (path) => {
    if (!path) return 0;
    if (!path.quizzes || !Array.isArray(path.quizzes) || path.quizzes.length === 0) {
      // Se non ci sono quiz o non è un array, usa il numero totale di quiz se disponibile
      if (path.total_quizzes && path.completed_quizzes) {
        return (path.completed_quizzes / path.total_quizzes) * 100;
      }
      return 0;
    }
    
    // Usa i quiz completati specifici per il percorso se disponibili
    if (pathCompletedQuizzes[path.id] && Array.isArray(pathCompletedQuizzes[path.id])) {
      const completedCount = path.quizzes.filter(quiz => 
        pathCompletedQuizzes[path.id].includes(quiz.id)
      ).length;
      return (completedCount / path.quizzes.length) * 100;
    }
    
    // Fallback al vecchio metodo
    const completedCount = path.quizzes.filter(quiz => completedQuizzes.includes(quiz.id)).length;
    return (completedCount / path.quizzes.length) * 100;
  };
  
  const handleQuizClick = async (quiz, path) => {
    // Reindirizza alla pagina del quiz
    // Se il quiz è un PathQuiz, utilizza l'ID del quiz originale
    const quizId = quiz.original_quiz_id || quiz.id;
    window.location.href = `/quizzes/${quizId}?pathId=${path.id}`;
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
            {path.completed_quizzes || 0}/{(path.quizzes && Array.isArray(path.quizzes) ? path.quizzes.length : path.total_quizzes || 0)} completati
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
          {paths.map(path => {
            // Assicurati che path abbia tutte le proprietà necessarie
            const safePath = {
              ...path,
              quizzes: Array.isArray(path.quizzes) ? path.quizzes : [],
              total_quizzes: path.total_quizzes || 0,
              completed_quizzes: path.completed_quizzes || 0
            };
            
            return (
              <Grid item xs={12} sm={6} md={4} key={safePath.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="div" sx={{ mb: 1 }}>
                      {safePath.name}
                    </Typography>
                    
                    {safePath.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {safePath.description}
                      </Typography>
                    )}
                    
                    <Box sx={{ mb: 2 }}>
                      {renderPathStatus(safePath)}
                    </Box>
                    
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <Box component="span" sx={{ fontWeight: 'bold' }}>Bonus al completamento:</Box>{' '}
                      <Chip 
                        label={`+${safePath.bonus_points} punti`} 
                        color="primary" 
                        size="small" 
                      />
                    </Typography>
                    
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => handleOpenDetails(safePath)}
                      fullWidth
                      sx={{ mt: 1 }}
                    >
                      Dettagli
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
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
                {renderPathStatus({
                  ...selectedPath,
                  quizzes: Array.isArray(selectedPath.quizzes) ? selectedPath.quizzes : [],
                  total_quizzes: selectedPath.total_quizzes || 0,
                  completed_quizzes: selectedPath.completed_quizzes || 0
                })}
              </Box>
              
              <Typography variant="h6" sx={{ mb: 1 }}>
                Quiz nel percorso:
              </Typography>
              
              <List>
                {(Array.isArray(selectedPath?.path_quizzes) && selectedPath.path_quizzes.length > 0) 
                  ? selectedPath.path_quizzes.map(quiz => {
                    const completed = isQuizCompleted(quiz.id, selectedPath.id);
                    
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
                  })
                  // Fallback ai quiz standard se path_quizzes non è disponibile
                  : (Array.isArray(selectedPath?.quizzes) && selectedPath.quizzes.length > 0 ? selectedPath.quizzes : []).map(quiz => {
                    const completed = isQuizCompleted(quiz.id, selectedPath.id);
                    
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
                  })
                }
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
