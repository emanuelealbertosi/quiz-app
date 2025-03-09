import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Card, CardContent, CardActions, Button, Chip, CircularProgress, Alert, Tooltip, Badge } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../config';

// Utility function to adjust a color (darken/lighten)
const adjustColor = (color, amount) => {
  if (!color) return '#4961DC';
  
  // Handle hex colors without # prefix
  if (color.charAt(0) !== '#') {
    color = '#' + color;
  }
  
  // Convert to RGB
  let r = parseInt(color.substring(1, 3), 16);
  let g = parseInt(color.substring(3, 5), 16);
  let b = parseInt(color.substring(5, 7), 16);
  
  // Adjust each component
  r = Math.max(0, Math.min(255, r + amount));
  g = Math.max(0, Math.min(255, g + amount));
  b = Math.max(0, Math.min(255, b + amount));
  
  // Convert back to hex
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

// Funzione utility per determinare se un quiz è completato
const isQuizCompleted = (quizId, completedQuizzes) => {
  // Assicuriamoci che quizId sia un numero
  const quizIdNum = Number(quizId);
  return completedQuizzes.has(quizIdNum);
};

// Funzione utility per ottenere il punteggio aggiornato di un quiz
const getCurrentPoints = (quizId, completedQuizzes, defaultPoints) => {
  // Assicuriamoci che quizId sia un numero
  const quizIdNum = Number(quizId);
  
  console.log(`Cercando punteggio per quiz ID: ${quizIdNum}, tipo: ${typeof quizIdNum}`);
  
  // Primo controllo: verifichiamo se c'è un punteggio aggiornato in localStorage
  try {
    const updatedQuizPoints = JSON.parse(localStorage.getItem('updatedQuizPoints') || '{}');
    if (updatedQuizPoints[quizIdNum] !== undefined) {
      const storedPoints = Number(updatedQuizPoints[quizIdNum]);
      console.log(`Trovato punteggio in localStorage per quiz ID ${quizIdNum}: ${storedPoints}`);
      return storedPoints;
    }
  } catch (e) {
    console.error('Errore nel leggere i punteggi da localStorage:', e);
  }
  
  // Secondo controllo: verifichiamo se c'è un punteggio nella Map dei quiz completati
  if (completedQuizzes.has(quizIdNum)) {
    const points = completedQuizzes.get(quizIdNum);
    console.log(`Trovato quiz ID: ${quizIdNum}, punteggio: ${points}`);
    
    // Se il punteggio è null o undefined, restituiamo il punteggio predefinito
    if (points !== null && points !== undefined) {
      return points;
    }
  }
  
  // Se il quiz non è completato o non abbiamo informazioni sul punteggio, restituisci il punteggio predefinito
  console.log(`Quiz non completato o nessun punteggio trovato, restituisco punteggio predefinito: ${defaultPoints}`);
  return defaultPoints;
};

function Quizzes() {
  const [quizzes, setQuizzes] = useState([]);
  const [totalQuizzes, setTotalQuizzes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [completedQuizzes, setCompletedQuizzes] = useState(new Map());
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchQuizzes = async () => {
      setLoading(true);
      try {
        // Fetch all quizzes
        const quizzesResponse = await fetch(ENDPOINTS.QUIZZES, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!quizzesResponse.ok) {
          throw new Error('Failed to fetch quizzes');
        }
        
        // Fetch user's completed quizzes
        const completedResponse = await fetch(ENDPOINTS.COMPLETED_QUIZZES, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }).catch(err => {
          console.error('Error fetching completed quizzes:', err);
          return { ok: false };
        });
        
        // Extract completed quiz IDs if the request was successful
        if (completedResponse && completedResponse.ok) {
          const completedData = await completedResponse.json();
          console.log('Completed quiz attempts data DETTAGLIATO:', JSON.stringify(completedData, null, 2));
          
          // Usiamo una Map invece di un Set per memorizzare sia l'ID che il punteggio aggiornato
          const completedMap = new Map();
          completedData.forEach(attempt => {
            if (attempt && attempt.quiz_id !== undefined) {
              // Convertiamo sempre l'ID del quiz in un numero per la consistenza
              const quizId = Number(attempt.quiz_id);
              // Assicuriamoci che il punteggio sia un numero o null
              const currentPoints = attempt.current_points !== undefined && attempt.current_points !== null 
                ? Number(attempt.current_points) 
                : null;
              
              // Salviamo come chiave l'ID del quiz e come valore il punteggio attuale
              completedMap.set(quizId, currentPoints);
              console.log(`Quiz completato ID: ${quizId} (tipo: ${typeof quizId}), punteggio attuale: ${currentPoints}`);
            }
          });
            
          console.log('Completed quiz IDs:', Array.from(completedMap.keys()));
          console.log('Completed quiz Points:', Array.from(completedMap.entries()));
          setCompletedQuizzes(completedMap);
        }
        
        const data = await quizzesResponse.json();
        console.log('API Response:', data);
        
        // Handle the response based on the API structure
        if (data && typeof data === 'object') {
          // The API returns an object with 'quizzes' array and 'total' count
          if (Array.isArray(data.quizzes)) {
            console.log('Struttura di un quiz:', data.quizzes.length > 0 ? data.quizzes[0] : 'Nessun quiz disponibile');
            setQuizzes(data.quizzes);
            setTotalQuizzes(data.total || data.quizzes.length);
          } 
          // Handle the case where the API might return an array directly
          else if (Array.isArray(data)) {
            setQuizzes(data);
            setTotalQuizzes(data.length);
          }
          // Handle other possible response formats
          else if (Array.isArray(data.items)) {
            setQuizzes(data.items);
            setTotalQuizzes(data.total || data.items.length);
          }
          else if (Array.isArray(data.data)) {
            setQuizzes(data.data);
            setTotalQuizzes(data.total || data.data.length);
          }
          // If no quizzes are found, set an empty array
          else {
            console.log('No quizzes found in response');
            setQuizzes([]);
            setTotalQuizzes(0);
          }
        } else {
          // Handle unexpected response format
          console.error('Unexpected API response format:', data);
          setQuizzes([]);
          setTotalQuizzes(0);
        }
      } catch (err) {
        console.error('Error fetching quizzes:', err);
        setError('Failed to load quizzes. Please try again later.');
        setQuizzes([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchQuizzes();
    
    // Ascoltatore dell'evento personalizzato per aggiornamenti dei punteggi
    const handleQuizPointsUpdated = (event) => {
      console.log('Evento quizPointsUpdated ricevuto:', event.detail);
      // Forziamo un aggiornamento del componente quando viene aggiornato un punteggio
      // Questo è un trucco per forzare un re-render
      setQuizzes(prevQuizzes => [...prevQuizzes]);
    };
    
    // Aggiungi l'ascoltatore dell'evento
    window.addEventListener('quizPointsUpdated', handleQuizPointsUpdated);
    
    // Rimuovi l'ascoltatore quando il componente viene smontato
    return () => {
      window.removeEventListener('quizPointsUpdated', handleQuizPointsUpdated);
    };
  }, [token]);

  const handleStartQuiz = (quizId) => {
    navigate(`/quizzes/${quizId}`);
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
          <Typography variant="h6" sx={{ ml: 2 }}>Loading quizzes...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  if (quizzes.length === 0) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Available Quizzes
          </Typography>
          <Alert severity="info">
            No quizzes are currently available. Please check back later or contact your teacher.
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Available Quizzes
        </Typography>
        <Grid container spacing={3}>
          {quizzes.map((quiz) => (
            <Grid item xs={12} sm={6} md={4} key={quiz.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
                  borderRadius: 4,
                  overflow: 'hidden',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  position: 'relative',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                    '& .hover-info': {
                      opacity: 1,
                      visibility: 'visible'
                    }
                  }
                }}
              >
                {/* Hover info overlay */}
                <Box 
                  className="hover-info"
                  sx={{ 
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 70, // Ridotto per mostrare solo i punti
                    bgcolor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    padding: 2,
                    opacity: 0,
                    visibility: 'hidden',
                    transition: 'opacity 0.3s ease, visibility 0.3s ease',
                    zIndex: 20
                  }}
                >
                  {/* Messaggio diverso per quiz completati vs non completati */}
                  {isQuizCompleted(quiz.id, completedQuizzes) ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                      <Typography 
                        variant="h6"
                        sx={{ fontWeight: 'bold', color: 'white' }}
                      >
                        Quiz completato
                      </Typography>
                      <Typography 
                        variant="body2"
                        sx={{ color: 'rgba(255,255,255,0.8)' }}
                      >
                        Punteggio attuale: {getCurrentPoints(quiz.id, completedQuizzes, quiz.points)}
                      </Typography>
                      {getCurrentPoints(quiz.id, completedQuizzes, quiz.points) < quiz.points && (
                        <Typography 
                          variant="body2"
                          sx={{ 
                            color: 'rgba(255,100,100,0.9)', 
                            fontWeight: 'bold',
                            mt: 0.5
                          }}
                        >
                          Punteggio diminuito: {getCurrentPoints(quiz.id, completedQuizzes, quiz.points)} di {quiz.points}
                        </Typography>
                      )}
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Box sx={{ 
                        display: 'flex', 
                        bgcolor: 'rgba(76, 175, 80, 0.8)', 
                        borderRadius: '50%',
                        width: 48,
                        height: 48,
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 1.5,
                        boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
                      }}>
                        <Typography 
                          variant="h6"
                          sx={{ fontWeight: 'bold', fontSize: '1.3rem' }}
                        >
                          {getCurrentPoints(quiz.id, completedQuizzes, quiz.points)}
                        </Typography>
                      </Box>
                      <Typography 
                        variant="subtitle1"
                        sx={{ color: 'white', fontWeight: 'bold', fontSize: '1rem' }}
                      >
                        PUNTI
                      </Typography>
                    </Box>
                  )}
                </Box>
                

                
                {/* Category banner in alto - versione semplificata e ben visibile */}
                {quiz.categories && quiz.categories.length > 0 && quiz.categories[0] && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      right: 0,
                      left: 0,
                      height: 28,
                      bgcolor: quiz.categories[0].color || '#4361ee',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                      borderTopLeftRadius: '4px',
                      borderTopRightRadius: '4px',
                      zIndex: 5,
                    }}
                  >
                    {quiz.categories[0].name}
                  </Box>
                )}
                
                {/* Etichetta "Completato con successo" per quiz già completati */}
                {isQuizCompleted(quiz.id, completedQuizzes) && (
                  <Box
                    sx={{
                      position: 'absolute',
                      right: 0,
                      top: 28,
                      bgcolor: 'success.main',
                      color: 'white',
                      py: 0.7,
                      px: 1.8,
                      borderTopLeftRadius: 16,
                      borderBottomLeftRadius: 16,
                      fontWeight: 'bold',
                      fontSize: '0.8rem',
                      textTransform: 'uppercase',
                      boxShadow: '0 3px 8px rgba(0,0,0,0.5)',
                      zIndex: 10,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      border: '2px solid white'
                    }}
                  >
                    <span role="img" aria-label="Success">✅</span>
                    COMPLETATO
                  </Box>
                )}
                
                <Box sx={{ 
                  p: 2, 
                  background: quiz.categories && quiz.categories.length > 0 && quiz.categories[0] && quiz.categories[0].color
                    ? `linear-gradient(135deg, ${quiz.categories[0].color} 0%, ${adjustColor(quiz.categories[0].color, -30)} 100%)`
                    : 'linear-gradient(135deg, #6A98F0 0%, #4961DC 100%)',
                  height: 70,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative'
                }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '1.2rem',
                      textShadow: '0 1px 3px rgba(0,0,0,0.3)',
                      letterSpacing: '0.5px'
                    }}
                  >
                    {quiz.title}
                  </Typography>
                  
                  {/* ID numero in basso a destra */}
                  <Typography
                    variant="caption"
                    sx={{
                      position: 'absolute',
                      bottom: 5,
                      right: 10,
                      color: 'rgba(255,255,255,0.8)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                    }}
                  >
                    {quiz.id}
                  </Typography>
                </Box>
                
                <CardContent sx={{ position: 'relative', flexGrow: 1, pt: 5, py: 3, px: 3 }}>
                  {/* Badge per quiz completati */}
                  {isQuizCompleted(quiz.id, completedQuizzes) && (
                    <Tooltip title="Quiz già completato">
                      <CheckCircleIcon 
                        color="success"
                        sx={{ 
                          position: 'absolute',
                          top: 15,
                          right: 15,
                          fontSize: 28,
                          filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.2))'
                        }}
                      />
                    </Tooltip>
                  )}
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'text.primary',
                      mb: 2,
                      fontWeight: 600,
                      fontSize: '1.15rem',
                      lineHeight: 1.4,
                      overflow: 'hidden',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      height: 80,
                      textShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      fontFamily: '"Quicksand", "Roboto", sans-serif'
                    }}
                  >
                    {quiz.description || quiz.question.substring(0, 100) + '...'}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2, justifyContent: 'flex-end' }}>
                    {quiz.difficulty_level && (
                      <Chip 
                        label={quiz.difficulty_level.name} 
                        size="small" 
                        sx={{ 
                          fontWeight: 'bold',
                          px: 1
                        }}
                        color={
                          quiz.difficulty_level.value <= 1 ? 'success' : 
                          quiz.difficulty_level.value === 2 ? 'warning' : 'error'
                        } 
                      />
                    )}
                    
                    {/* Chip per il punteggio del quiz */}
                    <Chip
                      size="small"
                      label={
                        getCurrentPoints(quiz.id, completedQuizzes, quiz.points) < quiz.points
                          ? `${getCurrentPoints(quiz.id, completedQuizzes, quiz.points)}/${quiz.points} pt`
                          : `${getCurrentPoints(quiz.id, completedQuizzes, quiz.points)} pt`
                      }
                      color={
                        getCurrentPoints(quiz.id, completedQuizzes, quiz.points) < quiz.points
                          ? "warning"
                          : "primary"
                      }
                      sx={{
                        ml: 1,
                        height: 24
                      }}
                    />
                  </Box>
                </CardContent>
                <CardActions sx={{ p: 2, pt: 0 }}>
                  <Button 
                    size="medium" 
                    color="primary" 
                    variant="contained" 
                    fullWidth
                    onClick={() => handleStartQuiz(quiz.id)}
                    sx={{
                      borderRadius: 50,
                      py: 1,
                      fontWeight: 'bold',
                      textTransform: 'none',
                      fontSize: '0.95rem',
                      boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 12px rgba(0,0,0,0.2)'
                      }
                    }}
                  >
                    Inizia Quiz
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
}

export default Quizzes;
