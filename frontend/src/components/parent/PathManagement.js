import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, TextField, Grid, Card, CardContent, 
  CardActions, Chip, Tooltip, Dialog, DialogTitle, 
  DialogContent, DialogActions, FormControl, InputLabel, 
  Select, MenuItem, CircularProgress, Alert
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import axios from 'axios';
import { ENDPOINTS } from '../../config';

const PathManagement = ({ student = null }) => {
  const [paths, setPaths] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [completedQuizzes, setCompletedQuizzes] = useState([]);
  const [open, setOpen] = useState(false);
  const [editPath, setEditPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bonus_points: 10,
    quiz_ids: []
  });
  const [selectedStudent, setSelectedStudent] = useState(student ? student.id : null);
  const [students, setStudents] = useState([]);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [selectedPath, setSelectedPath] = useState(null);
  const [assignedPaths, setAssignedPaths] = useState([]);

  // Fetch paths
  const fetchPaths = async () => {
    try {
      setLoading(true);
      const response = await axios.get(ENDPOINTS.PATHS || '');
      setPaths(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Errore nel recupero dei percorsi:', err);
      setError('Si è verificato un errore nel recupero dei percorsi.');
      setLoading(false);
    }
  };

  // Fetch quizzes
  const fetchQuizzes = async () => {
    try {
      const response = await axios.get(ENDPOINTS.QUIZZES || '');
      setQuizzes(response.data || []);
      
      // Fetch completed quizzes
      const completedResponse = await axios.get(ENDPOINTS.COMPLETED_QUIZZES || '');
      const completedIds = completedResponse.data ? completedResponse.data.map(q => q.quiz_id) : [];
      setCompletedQuizzes(completedIds);
    } catch (err) {
      console.error('Errore nel recupero dei quiz:', err);
      setQuizzes([]); // Assicura che quizzes sia un array vuoto in caso di errore
      setCompletedQuizzes([]);
    }
  };
  
  // Fetch students
  const fetchStudents = async () => {
    try {
      const response = await axios.get(ENDPOINTS.ME || '');
      const currentUser = response.data;
      
      if (currentUser.children && currentUser.children.length > 0) {
        setStudents(currentUser.children);
        if (!selectedStudent && currentUser.children.length > 0) {
          setSelectedStudent(currentUser.children[0].id);
        }
      }
    } catch (err) {
      console.error('Errore nel recupero degli studenti:', err);
    }
  };
  
  // Fetch assigned paths
  const fetchAssignedPaths = async () => {
    if (!selectedStudent) return;
    
    try {
      const response = await axios.get(ENDPOINTS.ASSIGNED_PATHS(selectedStudent) || '');
      setAssignedPaths(response.data);
    } catch (err) {
      console.error('Errore nel recupero dei percorsi assegnati:', err);
    }
  };

  useEffect(() => {
    fetchPaths();
    fetchQuizzes();
    if (!student) {
      fetchStudents();
    }
  }, [student]);
  
  useEffect(() => {
    if (selectedStudent) {
      fetchAssignedPaths();
    }
  }, [selectedStudent]);

  const handleOpen = (path = null) => {
    if (path) {
      // Edit mode
      setEditPath(path);
      setFormData({
        name: path.name,
        description: path.description || '',
        bonus_points: path.bonus_points,
        quiz_ids: Array.isArray(path.quizzes) ? path.quizzes.map(q => q.id) : []
      });
    } else {
      // Create mode
      setEditPath(null);
      setFormData({
        name: '',
        description: '',
        bonus_points: 10,
        quiz_ids: []
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuizSelect = (e) => {
    setFormData(prev => ({
      ...prev,
      quiz_ids: e.target.value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (formData.quiz_ids.length === 0) {
        setError('Devi selezionare almeno un quiz per creare un percorso.');
        setLoading(false);
        return;
      }
      
      if (!formData.name) {
        setError('Il nome del percorso è obbligatorio.');
        setLoading(false);
        return;
      }
      
      if (editPath) {
        // Update
        await axios.put(`${ENDPOINTS.PATHS}/${editPath.id}` || '', formData);
      } else {
        // Create
        await axios.post(ENDPOINTS.PATHS || '', formData);
      }
      
      setLoading(false);
      handleClose();
      fetchPaths();
    } catch (err) {
      console.error('Errore nel salvataggio del percorso:', err);
      setError('Si è verificato un errore nel salvataggio del percorso.');
      setLoading(false);
    }
  };

  const handleDelete = async (pathId) => {
    if (window.confirm('Sei sicuro di voler eliminare questo percorso?')) {
      try {
        await axios.delete(`${ENDPOINTS.PATHS}/${pathId}` || '');
        fetchPaths();
      } catch (err) {
        console.error('Errore nell\'eliminazione del percorso:', err);
        setError('Si è verificato un errore nell\'eliminazione del percorso.');
      }
    }
  };
  
  const handleOpenAssignDialog = (path) => {
    setSelectedPath(path);
    setOpenAssignDialog(true);
  };
  
  const handleCloseAssignDialog = () => {
    setOpenAssignDialog(false);
  };
  
  const handleAssignPath = async () => {
    try {
      if (!selectedStudent || !selectedPath) return;
      
      await axios.post(ENDPOINTS.ASSIGN_PATH || '', {
        path_id: selectedPath.id,
        user_id: selectedStudent
      });
      
      handleCloseAssignDialog();
      fetchAssignedPaths();
    } catch (err) {
      console.error('Errore nell\'assegnazione del percorso:', err);
      setError('Si è verificato un errore nell\'assegnazione del percorso.');
    }
  };
  
  const handleStudentChange = (e) => {
    setSelectedStudent(e.target.value);
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Gestione Percorsi</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />} 
          onClick={() => handleOpen()}
        >
          Nuovo Percorso
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {!student && students.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel>Seleziona Studente</InputLabel>
            <Select
              value={selectedStudent || ''}
              onChange={handleStudentChange}
              label="Seleziona Studente"
            >
              {students.map(student => (
                <MenuItem key={student.id} value={student.id}>
                  {student.first_name} {student.last_name} ({student.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}
      
      {/* Percorsi assegnati */}
      {selectedStudent && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Percorsi Assegnati
          </Typography>
          
          {assignedPaths.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Nessun percorso assegnato a questo studente.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {assignedPaths.map(path => (
                <Grid item xs={12} sm={6} md={4} key={`assigned-${path.id}`}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="div">
                        {path.name}
                      </Typography>
                      {path.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {path.description}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        Bonus: <Chip label={`+${path.bonus_points} punti`} color="primary" size="small" />
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Progresso: {path.completed_quizzes || 0}/{path.total_quizzes || path.quizzes.length} quiz completati
                      </Typography>
                      {path.completed && (
                        <Chip 
                          label="Completato" 
                          color="success" 
                          size="small" 
                          sx={{ mt: 1 }} 
                        />
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {/* Lista dei percorsi */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        I Tuoi Percorsi
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : paths.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          Non hai ancora creato nessun percorso.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {paths.map(path => (
            <Grid item xs={12} sm={6} md={4} key={path.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="div">
                    {path.name}
                  </Typography>
                  {path.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {path.description}
                    </Typography>
                  )}
                  <Typography variant="body2">
                    Bonus: <Chip label={`+${path.bonus_points} punti`} color="primary" size="small" />
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {path.quizzes.length} quiz nel percorso
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    {path.quizzes.slice(0, 3).map(quiz => (
                      <Tooltip key={quiz.id} title={quiz.question}>
                        <Chip 
                          label={quiz.question.length > 20 ? quiz.question.substring(0, 20) + '...' : quiz.question} 
                          size="small" 
                          sx={{ mr: 0.5, mb: 0.5 }} 
                        />
                      </Tooltip>
                    ))}
                    {path.quizzes.length > 3 && (
                      <Chip 
                        label={`+${path.quizzes.length - 3} altri`} 
                        size="small" 
                        variant="outlined"
                        sx={{ mb: 0.5 }} 
                      />
                    )}
                  </Box>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<EditIcon />} 
                    onClick={() => handleOpen(path)}
                  >
                    Modifica
                  </Button>
                  <Button 
                    size="small" 
                    color="error" 
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDelete(path.id)}
                  >
                    Elimina
                  </Button>
                  {selectedStudent && (
                    <Button 
                      size="small" 
                      color="primary" 
                      onClick={() => handleOpenAssignDialog(path)}
                    >
                      Assegna
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog per creazione/modifica percorso */}
      <Dialog 
        open={open} 
        onClose={handleClose} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {editPath ? `Modifica Percorso: ${editPath.name}` : 'Crea Nuovo Percorso'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Nome Percorso"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.name}
              onChange={handleChange}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              name="description"
              label="Descrizione (opzionale)"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.description}
              onChange={handleChange}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              name="bonus_points"
              label="Punti Bonus al Completamento"
              type="number"
              fullWidth
              variant="outlined"
              value={formData.bonus_points}
              onChange={handleChange}
              sx={{ mb: 2 }}
              InputProps={{ inputProps: { min: 1 } }}
              helperText="Quanti punti bonus otterrà lo studente completando questo percorso"
            />
            
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Seleziona Quiz</InputLabel>
              <Select
                multiple
                value={formData.quiz_ids}
                onChange={handleQuizSelect}
                label="Seleziona Quiz"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => {
                      const quiz = quizzes.find(q => q.id === value);
                      return quiz ? (
                        <Chip key={value} label={quiz.question.substring(0, 20) + '...'} />
                      ) : null;
                    })}
                  </Box>
                )}
              >
                {(Array.isArray(quizzes) ? quizzes : []).map((quiz) => (
                  <MenuItem key={quiz.id} value={quiz.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Typography variant="body2" sx={{ flex: 1 }}>
                        {quiz.question}
                      </Typography>
                      <Chip 
                        label={`${quiz.points} pt`} 
                        size="small" 
                        color="primary" 
                        sx={{ ml: 1 }} 
                      />
                      {completedQuizzes.includes(quiz.id) && (
                        <Chip 
                          label="Completato" 
                          size="small" 
                          color="success" 
                          sx={{ ml: 1 }} 
                        />
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Annulla</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : editPath ? 'Aggiorna' : 'Crea'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog per assegnazione percorso */}
      <Dialog
        open={openAssignDialog}
        onClose={handleCloseAssignDialog}
      >
        <DialogTitle>
          Assegna Percorso
        </DialogTitle>
        <DialogContent>
          {selectedPath && (
            <Typography variant="body1" sx={{ mt: 2 }}>
              Sei sicuro di voler assegnare il percorso "{selectedPath.name}" allo studente selezionato?
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAssignDialog}>Annulla</Button>
          <Button 
            onClick={handleAssignPath} 
            variant="contained" 
            color="primary"
          >
            Assegna
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PathManagement;
