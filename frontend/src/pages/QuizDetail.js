import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Typography, Box, Paper, Radio, RadioGroup, 
  FormControlLabel, FormControl, FormLabel, Button, 
  CircularProgress, Alert, Card, CardContent, Divider,
  Stepper, Step, StepLabel, StepContent, Zoom, Grow, Fade,
  useTheme, Chip
} from '@mui/material';
import { keyframes } from '@mui/system';
import ReactConfetti from 'react-confetti';
import { ENDPOINTS } from '../config';

// Animazione per il pulsante celebrativo
const bounce = keyframes`
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
`;

// Animazione per il punteggio che sale
const countUp = keyframes`
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  60% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

function QuizDetail() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const theme = useTheme();
  const [quiz, setQuiz] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [animation, setAnimation] = useState(false);
  const [userPoints, setUserPoints] = useState(0);
  const [oldPoints, setOldPoints] = useState(0);
  const [counting, setCounting] = useState(false);
  const token = localStorage.getItem('token');
  
  // Array di emoji divertenti per i bambini
  const happyEmojis = ['😊', '🎉', '🌟', '👏', '🦄', '🚀', '👍', '🏆', '💪', '🎯', '🎊'];
  const sadEmojis = ['😕', '🤔', '🧐', '📚', '💡', '🔍', '📝', '✏️'];
  
  // Funzione per ottenere emoji casuali
  const getRandomEmoji = (isHappy) => {
    const emojis = isHappy ? happyEmojis : sadEmojis;
    return emojis[Math.floor(Math.random() * emojis.length)];
  };

  useEffect(() => {
    const fetchQuiz = async () => {
      setLoading(true);
      try {
        const response = await fetch(ENDPOINTS.QUIZ_DETAIL(quizId), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          const errorData = await response.text();
          console.error('API error response:', errorData);
          throw new Error(`Failed to fetch quiz: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Quiz data received:', data);
        
        // Verifica che tutti i dati necessari siano presenti
        if (!data || !data.question) {
          throw new Error('Invalid quiz data format');
        }
        
        // Assicuriamoci che categories sia sempre un array
        if (!data.categories) {
          data.categories = [];
        }
        
        // Assicuriamoci che ogni categoria abbia un colore predefinito se non definito
        data.categories = data.categories.map(cat => ({
          ...cat,
          color: cat.color || '#6A98F0'
        }));
        
        setQuiz(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching quiz:', err);
        setError('Failed to load quiz. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchQuiz();
  }, [quizId, token]);

  const handleAnswerChange = (event) => {
    setSelectedAnswer(event.target.value);
  };

  const handleSubmit = async () => {
    if (!selectedAnswer) {
      setError('Scegli una risposta prima di continuare!');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Aggiungiamo un breve ritardo per creare suspense (opzionale)
      await new Promise(resolve => setTimeout(resolve, 600));
      
      // Utilizziamo l'endpoint corretto per il tentativo di quiz
      const response = await fetch(`${ENDPOINTS.QUIZZES}/attempt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          quiz_id: parseInt(quizId),
          answer: selectedAnswer,
          attempt_time: null // Opzionale, si può aggiungere se vogliamo tracciare il tempo
        })
      });
      
      if (!response.ok) {
        // Se otteniamo errore 403, significa che l'utente non è uno studente
        if (response.status === 403) {
          throw new Error('Solo gli studenti possono rispondere ai quiz. Accedi con un account studente.');
        }
        
        // Proviamo a ottenere il messaggio di errore dal server se disponibile
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Non è stato possibile inviare la risposta');
      }
      
      const data = await response.json();
      // Converti la risposta nel formato previsto dal componente result
      setResult({
        correct: data.correct, // Nel modello è 'correct' non 'is_correct'
        explanation: quiz.explanation,
        points: data.points_earned,
        emoji: getRandomEmoji(data.correct) // Aggiunge un'emoji casuale
      });
      
      // Attiva l'animazione dopo il risultato
      setAnimation(true);
    } catch (err) {
      console.error('Error submitting answer:', err);
      setError(err.message || 'Non è stato possibile inviare la risposta. Riprova!');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBackToQuizzes = () => {
    navigate('/quizzes');
  };

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ 
          mt: 4, 
          display: 'flex', 
          flexDirection: 'column',
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '60vh' 
        }}>
          <Typography variant="h5" color="primary" sx={{ 
            mb: 3, 
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <span style={{ fontSize: '1.7rem' }}>🤓</span>
            Preparando il quiz...
          </Typography>
          <CircularProgress 
            size={80} 
            thickness={5}
            sx={{ 
              color: theme.palette.secondary.main,
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                borderRadius: '50%',
                boxShadow: '0 0 15px rgba(0,180,180,0.3)'
              }
            }}
          />
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ mt: 3, fontStyle: 'italic', textAlign: 'center' }}
          >
            Un attimo di pazienza,<br/>stiamo caricando una domanda super interessante!
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              borderRadius: 3, 
              bgcolor: '#FFF5F5',
              border: '1px solid #FFD7D7'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography 
                variant="h5" 
                color="error" 
                sx={{ 
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <span style={{ fontSize: '2rem' }}>😧</span>
                Oops! C'è stato un problema
              </Typography>
            </Box>
            
            <Alert 
              severity="error" 
              variant="outlined"
              sx={{ 
                mb: 3, 
                borderRadius: 2,
                '& .MuiAlert-message': { fontWeight: 500 }
              }}>
              {error}
            </Alert>
            
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button 
                variant="contained" 
                color="primary" 
                size="large"
                onClick={handleBackToQuizzes}
                sx={{ 
                  mt: 2,
                  px: 3,
                  py: 1.5,
                  borderRadius: 50,
                  fontWeight: 'bold'
                }}
              >
                <span style={{ marginRight: 8 }}>🔙</span>
                Torna ai Quiz
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  if (!quiz) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Alert severity="warning">Quiz not found</Alert>
          <Button 
            variant="outlined" 
            color="primary" 
            sx={{ mt: 2 }}
            onClick={handleBackToQuizzes}
          >
            Back to Quizzes
          </Button>
        </Box>
      </Container>
    );
  }

  if (result) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Zoom in={animation} timeout={800}>
            <Card sx={{ 
              mb: 4, 
              boxShadow: '0 10px 30px rgba(0,0,0,0.15), 0 0 30px rgba(0,200,180,0.2)',
              overflow: 'visible',
              borderRadius: 4,
              position: 'relative'
            }}>
              <Box sx={{
                position: 'absolute',
                top: '-30px',
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 10,
                animation: result.correct ? `${bounce} 1s ease 0.5s` : 'none',
                animationIterationCount: 3
              }}>
                <Typography variant="h3" component="span" sx={{
                  fontSize: '4rem', 
                  filter: 'drop-shadow(0 3px 5px rgba(0,0,0,0.2))'
                }}>
                  {result.emoji || (result.correct ? '🎉' : '📚')}
                </Typography>
              </Box>
              
              <CardContent sx={{ pt: 5, pb: 4, px: { xs: 2, sm: 4 } }}>
                <Grow in={true}>
                  <Typography 
                    variant="h4" 
                    component="h1" 
                    gutterBottom 
                    sx={{ 
                      textAlign: 'center',
                      color: result.correct ? 'success.main' : 'secondary.main',
                      fontWeight: 'bold',
                      fontSize: { xs: '1.8rem', md: '2.25rem' },
                      mt: 1
                    }}
                  >
                    {result.correct ? 'Risposta Corretta!' : 'Riprova!'}
                  </Typography>
                </Grow>
                
                <Divider sx={{ 
                  my: 3, 
                  height: '3px', 
                  borderRadius: 2,
                  background: result.correct 
                    ? 'linear-gradient(90deg, #66BB6A 0%, #A5D6A7 100%)' 
                    : 'linear-gradient(90deg, #FF88A2 0%, #FFC1D0 100%)'
                }} />
                
                <Fade in={true} timeout={1000}>
                  <Box sx={{ 
                    my: 3, 
                    p: 3, 
                    bgcolor: result.correct ? 'success.light' : 'secondary.light', 
                    color: result.correct ? 'success.contrastText' : 'secondary.contrastText',
                    borderRadius: 3,
                    boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.1)',
                    position: 'relative',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      width: '20px',
                      height: '20px',
                      top: '-10px',
                      left: '30px',
                      transform: 'rotate(45deg)',
                      bgcolor: result.correct ? 'success.light' : 'secondary.light',
                    }
                  }}>
                    <Typography 
                      variant="body1" 
                      paragraph 
                      sx={{ 
                        fontWeight: 500,
                        fontSize: '1.1rem',
                        mb: 0,
                        fontFamily: 'Nunito, sans-serif'
                      }}
                    >
                      {result.explanation || (result.correct ? 
                        'Fantastico! Hai risposto correttamente.' : 
                        'Peccato, la risposta non è corretta. Riprova con un altro quiz!'
                      )}
                    </Typography>
                  </Box>
                </Fade>
                
                {/* Punti guadagnati */}
                {result.points !== undefined && (
                  <Zoom in={true} timeout={500} style={{ transitionDelay: '500ms' }}>
                    <Box sx={{ 
                      my: 3, 
                      p: 3, 
                      bgcolor: 'white',
                      borderRadius: 3,
                      boxShadow: '0 6px 20px rgba(0,0,0,0.1)',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 2,
                      border: '2px dashed',
                      borderColor: result.correct ? 'success.main' : 'grey.300',
                      position: 'relative',
                      animation: result.correct ? `${countUp} 1.5s ease` : 'none'
                    }}>
                      <Typography variant="h6" color="text.primary" sx={{ fontWeight: 600 }}>
                        {result.points === 0 && result.correct ? "Quiz già completato!" : "Punti guadagnati:"}
                      </Typography>
                      
                      <Typography 
                        variant="h2" 
                        fontWeight="bold" 
                        color={result.correct ? (result.points > 0 ? "success.main" : "primary.main") : "text.secondary"}
                        sx={{ 
                          fontSize: { xs: '3rem', md: '4rem' },
                          textShadow: result.correct ? '0 2px 10px rgba(102,187,106,0.4)' : 'none'
                        }}
                      >
                        {result.points}
                      </Typography>
                      
                      {result.correct && result.points === 0 && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                          Hai già completato questo quiz con successo in precedenza!
                        </Typography>
                      )}
                      
                      {result.correct && result.points > 0 && (
                        <Box sx={{ 
                          position: 'absolute',
                          top: -15,
                          right: -15,
                          bgcolor: 'warning.main',
                          color: 'white',
                          borderRadius: '50%',
                          width: 60,
                          height: 60,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold',
                          fontSize: '1.2rem',
                          boxShadow: '0 4px 10px rgba(255,202,40,0.5)',
                          transform: 'rotate(15deg)',
                          animation: `${bounce} 1s ease 1s`,
                          animationIterationCount: 2
                        }}>
                          +{result.points}!
                        </Box>
                      )}
                    </Box>
                  </Zoom>
                )}
                
                <Box sx={{ 
                  mt: 4, 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: 2,
                  alignItems: 'center' 
                }}>
                  {result.correct && (
                    <Grow in={true} timeout={1000} style={{ transitionDelay: '800ms' }}>
                      <Alert 
                        severity="info" 
                        icon={<span style={{ fontSize: '1.5rem' }}>👍</span>}
                        sx={{ 
                          width: '100%', 
                          borderRadius: 2,
                          '& .MuiAlert-message': { fontWeight: 500 }
                        }}
                      >
                        {result.points > 0 ? 
                          "Il tuo punteggio è stato aggiornato! Controlla il tuo nuovo punteggio nella Dashboard." :
                          "Hai già completato questo quiz in precedenza! Il quiz è ora contrassegnato come completato, ma non riceverai punti aggiuntivi."}
                      </Alert>
                    </Grow>
                  )}
                  
                  <Box sx={{ 
                    display: 'flex', 
                    gap: 2, 
                    mt: 2,
                    flexWrap: { xs: 'wrap', sm: 'nowrap' },
                    justifyContent: 'center',
                    width: '100%'
                  }}>
                    <Button 
                      variant="contained" 
                      color="primary"
                      onClick={handleBackToQuizzes}
                      size="large"
                      sx={{ 
                        py: 1.5, 
                        px: 3,
                        flex: { xs: '1 1 100%', sm: 1 },
                        borderRadius: 50,
                        fontWeight: 'bold',
                        fontSize: '1rem'
                      }}
                    >
                      <span style={{ marginRight: 8 }}>🔙</span> 
                      Torna ai Quiz
                    </Button>
                    
                    <Button 
                      variant="contained" 
                      color="secondary"
                      component="a"
                      href="/dashboard"
                      size="large"
                      sx={{ 
                        py: 1.5, 
                        px: 3,
                        flex: { xs: '1 1 100%', sm: 1 },
                        borderRadius: 50,
                        fontWeight: 'bold',
                        fontSize: '1rem'
                      }}
                    >
                      <span style={{ marginRight: 8 }}>📊</span> 
                      Vai alla Dashboard
                    </Button>
                  </Box>
                </Box>
                
                {/* Confetti per celebrare la risposta corretta */}
                {result.correct && (
                  <Box sx={{ 
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    pointerEvents: 'none',
                    zIndex: 100
                  }}>
                    <ReactConfetti
                      width={window.innerWidth}
                      height={window.innerHeight}
                      recycle={false}
                      numberOfPieces={500}
                      tweenDuration={10000}
                      gravity={0.1}
                      colors={[
                        '#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845',
                        '#2ECC71', '#3498DB', '#9B59B6', '#FFC300', '#16A085'
                      ]}
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Zoom>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Card sx={{ mb: 4, boxShadow: 3 }}>
          <CardContent>
            <Typography variant="h4" component="h1" gutterBottom sx={{ 
              fontSize: { xs: '1.8rem', sm: '2.125rem' },
              fontWeight: 'bold',
              color: 'primary.main',
              textShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              {quiz.title || 'Quiz'}
            </Typography>
            
            {/* Visualizzazione categorie come chip colorati */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {quiz.categories && quiz.categories.map((category) => (
                <Chip
                  key={category.id}
                  label={category.name}
                  sx={{
                    bgcolor: category.color || '#4361ee',
                    color: 'white',
                    fontWeight: 'bold',
                    '&:hover': {
                      bgcolor: category.color ? `${category.color}DD` : '#3651ce',
                    }
                  }}
                />
              ))}
              
              {quiz.difficulty_level && (
                <Chip
                  label={quiz.difficulty_level.name}
                  size="medium"
                  sx={{
                    bgcolor: quiz.difficulty_level.value <= 1 ? 'success.main' : 
                            quiz.difficulty_level.value === 2 ? 'warning.main' : 'error.main',
                    color: 'white',
                    fontWeight: 'bold',
                    ml: 1
                  }}
                />
              )}
            </Box>
            <Divider sx={{ mb: 3 }} />
            <Typography variant="h6" gutterBottom sx={{
              fontSize: { xs: '1.1rem', sm: '1.25rem' },
              fontWeight: '500',
              lineHeight: 1.5,
              mb: 3,
              color: 'text.primary',
              textShadow: '0 1px 1px rgba(0,0,0,0.05)',
              padding: '16px',
              backgroundColor: 'rgba(25, 118, 210, 0.05)',
              borderRadius: '8px',
              border: '1px solid rgba(25, 118, 210, 0.2)',
            }}>
              {quiz.question}
            </Typography>
            
            <Box sx={{ display: 'inline-block', bgcolor: 'primary.light', color: 'primary.contrastText', px: 2, py: 1, borderRadius: 2, mb: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Punti disponibili: {quiz.points}
              </Typography>
            </Box>
            <FormControl component="fieldset" sx={{ mt: 2, width: '100%' }}>
              <FormLabel component="legend">Seleziona la risposta corretta:</FormLabel>
              <RadioGroup
                aria-label="quiz answer"
                name="quiz-answer"
                value={selectedAnswer}
                onChange={handleAnswerChange}
              >
                {/* Mostriamo le opzioni senza lettere */}
                {Array.isArray(quiz.options) ? (
                  quiz.options.map((option, index) => {
                    // Utilizziamo il valore effettivo dell'opzione
                    const keyValue = String.fromCharCode(97 + index); // Solo per chiave unica
                    return (
                      <FormControlLabel 
                        key={keyValue} 
                        value={option} 
                        control={<Radio />} 
                        label={option} 
                        sx={{ 
                          mb: 1.5,
                          '.MuiFormControlLabel-label': {
                            fontSize: '1rem',
                            fontWeight: selectedAnswer === option ? 'bold' : 'normal'
                          }
                        }}
                      />
                    );
                  })
                ) : (
                  // Fallback alle vecchie opzioni nel caso in cui il backend utilizzi ancora il vecchio formato
                  <>
                    {quiz.option_a && <FormControlLabel value={quiz.option_a} control={<Radio />} label={quiz.option_a} sx={{ mb: 1 }} />}
                    {quiz.option_b && <FormControlLabel value={quiz.option_b} control={<Radio />} label={quiz.option_b} sx={{ mb: 1 }} />}
                    {quiz.option_c && <FormControlLabel value={quiz.option_c} control={<Radio />} label={quiz.option_c} sx={{ mb: 1 }} />}
                    {quiz.option_d && <FormControlLabel value={quiz.option_d} control={<Radio />} label={quiz.option_d} sx={{ mb: 1 }} />}
                  </>
                )}
              </RadioGroup>
            </FormControl>
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button 
                variant="outlined" 
                color="primary"
                onClick={handleBackToQuizzes}
              >
                Back to Quizzes
              </Button>
              <Button 
                variant="contained" 
                color="primary"
                disabled={!selectedAnswer || submitting}
                onClick={handleSubmit}
              >
                {submitting ? <CircularProgress size={24} /> : 'Submit Answer'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}

export default QuizDetail;
