import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
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
  CircularProgress
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import BarChartIcon from '@mui/icons-material/BarChart';
import CategoryIcon from '@mui/icons-material/Category';
import QuizIcon from '@mui/icons-material/Quiz';
import SpeedIcon from '@mui/icons-material/Speed';
import { ENDPOINTS } from '../config';
import UserStats from './UserStats';
import QuizCategoryStats from './QuizCategoryStats';
import QuizStats from './QuizStats';
import RewardManagement from './RewardManagement';
import DifficultyStats from './DifficultyStats';
import QuizManagement from './QuizManagement';

// Componente TabPanel per gestire il contenuto delle tab
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `admin-tab-${index}`,
    'aria-controls': `admin-tabpanel-${index}`,
  };
}

const AdminPanel = ({ token }) => {
  const [value, setValue] = useState(0);
  const [difficultyLevels, setDifficultyLevels] = useState([]);
  const [paths, setPaths] = useState([]);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [importing, setImporting] = useState(false);
  
  // Dialog states
  const [openDifficultyDialog, setOpenDifficultyDialog] = useState(false);
  const [openPathDialog, setOpenPathDialog] = useState(false);
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [openUserDetailDialog, setOpenUserDetailDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add' or 'edit'
  const [currentDifficulty, setCurrentDifficulty] = useState({ name: '', value: '' });
  const [currentPath, setCurrentPath] = useState({ name: '', description: '' });
  const [currentUser, setCurrentUser] = useState({ 
    username: '', 
    email: '', 
    password: '', 
    role: 'student',
    parent_id: null 
  });
  const [userDetail, setUserDetail] = useState(null);
  const [userQuizzes, setUserQuizzes] = useState(null);
  const [childrenProgress, setChildrenProgress] = useState(null);
  
  // Ref per l'input file
  const fileInputRef = useRef(null);
  
  // Il token è già passato come prop
  
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  
  // Funzione per caricare i livelli di difficoltà
  const fetchDifficultyLevels = useCallback(() => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      console.log('Fetching difficulty levels with token:', token ? `${token.substring(0, 10)}...` : 'null');
      
      // Using XMLHttpRequest instead of fetch for better compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('GET', ENDPOINTS.ADMIN.DIFFICULTY_LEVELS, true);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.withCredentials = false; // Set to false to prevent CORS preflight issues
      
      xhr.onload = function() {
        console.log('Difficulty levels response status:', xhr.status);
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('Difficulty levels data received:', data);
            
            // Assicuriamoci che difficultyLevels sia sempre un array
            if (Array.isArray(data)) {
              console.log('Setting difficulty levels array with', data.length, 'items');
              setDifficultyLevels(data);
            } else if (data.items && Array.isArray(data.items)) {
              console.log('Setting difficulty levels from data.items with', data.items.length, 'items');
              setDifficultyLevels(data.items);
            } else {
              console.error('Unexpected difficulty levels data format:', data);
              setDifficultyLevels([]);
            }
          } catch (e) {
            console.error('Error parsing JSON from difficulty levels endpoint:', e);
            setError('Error parsing difficulty levels data');
            setDifficultyLevels([]);
          }
        } else {
          console.error(`Failed to fetch difficulty levels: ${xhr.status} ${xhr.statusText}`);
          setError(`Failed to fetch difficulty levels: ${xhr.status} ${xhr.statusText}`);
          setDifficultyLevels([]);
        }
      };
      
      xhr.onerror = function() {
        console.error('Network error occurred while fetching difficulty levels');
        setError('Network error occurred while fetching difficulty levels');
        setDifficultyLevels([]);
      };
      
      xhr.send();
    } catch (error) {
      console.error('Error fetching difficulty levels:', error);
      setError('Error fetching difficulty levels: ' + error.message);
      setDifficultyLevels([]);
    }
  }, [token]);
  
  // Funzione per caricare i percorsi
  const fetchPaths = useCallback(() => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      console.log('Fetching paths with token:', token ? `${token.substring(0, 10)}...` : 'null');
      
      // Using XMLHttpRequest instead of fetch for better compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('GET', ENDPOINTS.ADMIN.PATHS, true);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.withCredentials = false; // Set to false to prevent CORS preflight issues
      
      xhr.onload = function() {
        console.log('Paths response status:', xhr.status);
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('Paths data received:', data);
            
            // La risposta è in formato {paths: [...], total: n}
            if (data.paths && Array.isArray(data.paths)) {
              console.log('Setting paths from data.paths with', data.paths.length, 'items');
              setPaths(data.paths);
            } else if (Array.isArray(data)) {
              console.log('Setting paths array with', data.length, 'items');
              setPaths(data);
            } else if (data.items && Array.isArray(data.items)) {
              setPaths(data.items);
            } else {
              console.error('Unexpected paths data format:', data);
              setPaths([]);
            }
          } catch (e) {
            console.error('Error parsing JSON from paths endpoint:', e);
            setError('Error parsing paths data');
            setPaths([]);
          }
        } else {
          console.error(`Failed to fetch paths: ${xhr.status} ${xhr.statusText}`);
          setError(`Failed to fetch paths: ${xhr.status} ${xhr.statusText}`);
          setPaths([]);
        }
      };
      
      xhr.onerror = function() {
        console.error('Network error occurred while fetching paths');
        setError('Network error occurred while fetching paths');
        setPaths([]);
      };
      
      xhr.send();
    } catch (error) {
      console.error('Error fetching paths:', error);
      setError('Error fetching paths: ' + error.message);
      setPaths([]);
    }
  }, [token]);
  
  // Funzione per caricare le statistiche di sistema
  const fetchStats = useCallback(async () => {
    try {
      // Using XMLHttpRequest instead of fetch for better compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('GET', ENDPOINTS.ADMIN.STATS, true);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.withCredentials = false; // Set to false to prevent CORS preflight issues
      
      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            setStats(data);
            setError(null);
          } catch (e) {
            console.error('Error parsing JSON:', e);
            setError('Error parsing system stats data');
          }
        } else {
          setError(`Failed to fetch system stats: ${xhr.status} ${xhr.statusText}`);
        }
      };
      
      xhr.onerror = function() {
        setError('Network error occurred while fetching system stats');
      };
      
      xhr.send();
    } catch (error) {
      console.error('Error fetching system stats:', error);
      setError('Error fetching system stats: ' + error.message);
    }
  }, [token]);
  
  // Funzione per caricare gli utenti
  const fetchUsers = useCallback(async () => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      console.log('Fetching users with token:', token ? `${token.substring(0, 10)}...` : 'null');
      
      // Using XMLHttpRequest instead of fetch for better compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('GET', ENDPOINTS.ADMIN.USERS, true);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.withCredentials = false; // Set to false to prevent CORS preflight issues
      
      xhr.onload = function() {
        console.log('Users response status:', xhr.status);
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('Users data received:', data);
            
            if (data.users && Array.isArray(data.users)) {
              setUsers(data.users);
            } else if (Array.isArray(data)) {
              setUsers(data);
            } else {
              console.error('Unexpected users data format:', data);
              setUsers([]);
            }
            setError(null);
          } catch (e) {
            console.error('Error parsing JSON:', e);
            setError('Error parsing users data');
          }
        } else {
          let errorMessage = `Failed to fetch users: ${xhr.status} ${xhr.statusText}`;
          try {
            const errorData = JSON.parse(xhr.responseText);
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          } catch (e) {
            console.error('Error parsing error response:', e);
          }
          console.error(errorMessage);
          setError(errorMessage);
        }
      };
      
      xhr.onerror = function() {
        setError('Network error occurred while fetching users');
      };
      
      xhr.send();
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Error fetching users: ' + error.message);
    }
  }, [token]);
  
  // Funzione per importare quiz da CSV
  const handleImportQuizzes = async (file) => {
    if (!file) {
      return;
    }
    
    setImporting(true);
    setImportResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(ENDPOINTS.ADMIN.IMPORT_QUIZZES, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
        mode: 'cors',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to import quizzes');
      }
      
      const result = await response.json();
      setImportResult(result);
      console.log('Import result:', result);
      
      // Aggiorna le statistiche dopo l'importazione
      fetchStats();
    } catch (error) {
      console.error('Error importing quizzes:', error);
      setImportResult({ error: error.message, imported_count: 0, errors: [] });
    } finally {
      setImporting(false);
    }
  }
  
  // Gestione del dialogo per l'importazione di quiz
  const handleOpenImportDialog = () => {
    setOpenImportDialog(true);
  };
  
  const handleCloseImportDialog = () => {
    setOpenImportDialog(false);
    setImportResult(null);
  };
  
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleImportQuizzes(file);
    }
  };
  
  // Gestione del dialogo per gli utenti
  const handleOpenUserDialog = (mode, user = null) => {
    setDialogMode(mode);
    if (mode === 'edit' && user) {
      // Quando modifichiamo un utente esistente, non includiamo la password
      // perché non vogliamo sovrascriverla a meno che non venga specificata una nuova
      const parent_id = user.parents && user.parents.length > 0 ? user.parents[0].id : null;
      setCurrentUser({
        ...user,
        password: '', // Password vuota per la modifica
        parent_id: parent_id // Imposta il parent_id dal primo genitore
      });
      console.log('Editing user with parent_id:', parent_id);
    } else {
      // Per un nuovo utente, inizializziamo tutti i campi
      setCurrentUser({ 
        username: '', 
        email: '', 
        password: '', 
        role: 'student',
        parent_id: null 
      });
    }
    setOpenUserDialog(true);
  };
  
  const handleCloseUserDialog = () => {
    setOpenUserDialog(false);
  };
  
  const handleSaveUser = useCallback(async () => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      console.log('Attempting to save user with data:', currentUser);
      
      // Determina se stiamo aggiungendo o modificando un utente
      const isEditing = dialogMode === 'edit';
      const url = isEditing ? `${ENDPOINTS.ADMIN.USERS}/${currentUser.id}` : ENDPOINTS.ADMIN.USERS;
      const method = isEditing ? 'PUT' : 'POST';
      
      console.log('Making request to:', url);
      console.log('With method:', method);
      console.log('With headers:', {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.substring(0, 10)}...`
      });
      
      // Prepara i dati da inviare (rimuovi la password se è vuota durante la modifica)
      const userData = {...currentUser};
      if (isEditing && !userData.password) {
        delete userData.password;
      }
      
      console.log('Sending user data:', JSON.stringify(userData));
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData),
        mode: 'cors',
        credentials: 'include'
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        let errorMessage = 'Failed to save user';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          console.error('Error parsing error response:', e);
        }
        throw new Error(errorMessage);
      }
      
      await fetchUsers();
      handleCloseUserDialog();
    } catch (error) {
      console.error('Error saving user:', error);
      setError('Error saving user: ' + error.message);
    }
  }, [token, currentUser, dialogMode, fetchUsers]);
  
  // Funzione per visualizzare i dettagli di un utente
  const handleToggleUserActive = useCallback(async (userId) => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      const response = await fetch(ENDPOINTS.ADMIN.TOGGLE_USER_ACTIVE(userId), {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        mode: 'cors',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to toggle user active status');
      }
      
      const data = await response.json();
      
      // Aggiorna la lista degli utenti
      await fetchUsers();
      
      // Se il dialog dei dettagli è aperto, aggiorna anche i dettagli dell'utente
      if (openUserDetailDialog && userDetail && userDetail.id === userId) {
        handleViewUserDetail(userId);
      }
      
      // Mostra un messaggio di successo
      setSuccessMessage(data.message || `User status updated successfully`);
    } catch (error) {
      console.error('Error toggling user active status:', error);
      setError('Error toggling user active status: ' + error.message);
    }
  }, [token, fetchUsers, openUserDetailDialog, userDetail]);

  const handleUpdateStudentPoints = useCallback(async (userId, points) => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      const response = await fetch(`${ENDPOINTS.ADMIN.UPDATE_STUDENT_POINTS(userId)}?points=${points}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        mode: 'cors',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to update student points');
      }
      
      const data = await response.json();
      
      // Aggiorna la lista degli utenti
      await fetchUsers();
      
      // Se il dialog dei dettagli è aperto, aggiorna anche i dettagli dell'utente
      if (openUserDetailDialog && userDetail && userDetail.id === userId) {
        handleViewUserDetail(userId);
      }
      
      // Mostra un messaggio di successo
      setSuccessMessage(data.message || `Student points updated successfully`);
    } catch (error) {
      console.error('Error updating student points:', error);
      setError('Error updating student points: ' + error.message);
    }
  }, [token, fetchUsers, openUserDetailDialog, userDetail]);

  const handleViewUserDetail = useCallback(async (userId) => {
    try {
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication error: No token found. Please log in again.');
        return;
      }
      
      // Resetta gli stati precedenti
      setUserDetail(null);
      setUserQuizzes(null);
      setChildrenProgress(null);
      
      // Ottieni i dettagli dell'utente
      const response = await fetch(ENDPOINTS.ADMIN.USER_DETAIL(userId), {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        mode: 'cors',
        credentials: 'same-origin'
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch user details');
      }
      
      const userData = await response.json();
      setUserDetail(userData);
      
      // Se l'utente è uno studente, ottieni i quiz completati
      if (userData.role === 'student') {
        const quizzesResponse = await fetch(ENDPOINTS.ADMIN.STUDENT_QUIZZES(userId), {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (quizzesResponse.ok) {
          const quizzesData = await quizzesResponse.json();
          setUserQuizzes(quizzesData);
        }
      }
      
      // Se l'utente è un genitore, ottieni i progressi dei figli
      if (userData.role === 'parent') {
        const progressResponse = await fetch(ENDPOINTS.ADMIN.CHILDREN_PROGRESS(userId), {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        if (progressResponse.ok) {
          const progressData = await progressResponse.json();
          setChildrenProgress(progressData);
        }
      }
      
      setOpenUserDetailDialog(true);
    } catch (error) {
      console.error('Error fetching user details:', error);
      setError('Error fetching user details: ' + error.message);
    }
  }, [token]);
  
  const handleCloseUserDetailDialog = () => {
    setOpenUserDetailDialog(false);
  };
  
  // Funzione per attivare/disattivare un utente

  
  // Funzione per eliminare un utente
  const handleDeleteUser = useCallback(async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        if (!token) {
          console.error('No authentication token found');
          setError('Authentication error: No token found. Please log in again.');
          return;
        }
        
        console.log(`Deleting user with ID: ${id}`);
        
        const response = await fetch(`${ENDPOINTS.ADMIN.USERS}/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          mode: 'cors',
          credentials: 'include'
        });
        
        console.log('Delete response status:', response.status);
        
        if (!response.ok) {
          let errorMessage = 'Failed to delete user';
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            console.error('Error parsing error response:', e);
          }
          throw new Error(errorMessage);
        }
        
        // Aggiorna la lista degli utenti
        await fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        setError('Error deleting user: ' + error.message);
      }
    }
  }, [token, fetchUsers]);
  
  // Carica i dati all'avvio del componente
  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchDifficultyLevels(),
      fetchPaths(),
      fetchStats(),
      fetchUsers()
    ]).finally(() => {
      setLoading(false);
    });
  }, [token, fetchDifficultyLevels, fetchPaths, fetchStats, fetchUsers]); // Dipende dal token e dalle funzioni
  
  // Gestione del dialogo per i livelli di difficoltà
  const handleOpenDifficultyDialog = (mode, difficulty = null) => {
    setDialogMode(mode);
    if (difficulty) {
      setCurrentDifficulty(difficulty);
    } else {
      setCurrentDifficulty({ name: '', value: '' });
    }
    setOpenDifficultyDialog(true);
  };
  
  const handleCloseDifficultyDialog = () => {
    setOpenDifficultyDialog(false);
  };
  
  const handleSaveDifficulty = useCallback(async () => {
    try {
      const url = dialogMode === 'add' 
        ? ENDPOINTS.ADMIN.DIFFICULTY_LEVELS
        : `${ENDPOINTS.ADMIN.DIFFICULTY_LEVELS}/${currentDifficulty.id}`;
        
      const method = dialogMode === 'add' ? 'POST' : 'PUT';
      
      console.log('Saving difficulty level:', {
        url,
        method,
        token,
        data: {
          name: currentDifficulty.name,
          value: parseInt(currentDifficulty.value)
        }
      });
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: currentDifficulty.name,
          value: parseInt(currentDifficulty.value)
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save difficulty level');
      }
      
      // Aggiorna la lista
      fetchDifficultyLevels();
      handleCloseDifficultyDialog();
    } catch (error) {
      console.error('Error saving difficulty level:', error);
      setError('Error saving difficulty level: ' + error.message);
    }
  }, [token, dialogMode, currentDifficulty, fetchDifficultyLevels, handleCloseDifficultyDialog]);
  
  const handleDeleteDifficulty = useCallback(async (id) => {
    if (window.confirm('Are you sure you want to delete this difficulty level?')) {
      try {
        console.log('Deleting difficulty level:', id);
        
        const response = await fetch(`${ENDPOINTS.ADMIN.DIFFICULTY_LEVELS}/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to delete difficulty level');
        }
        
        // Aggiorna la lista
        fetchDifficultyLevels();
      } catch (error) {
        console.error('Error deleting difficulty level:', error);
        setError('Error deleting difficulty level: ' + error.message);
      }
    }
  }, [token, fetchDifficultyLevels]);
  
  // Gestione del dialogo per i percorsi
  const handleOpenPathDialog = (mode, path = null) => {
    setDialogMode(mode);
    if (path) {
      setCurrentPath(path);
    } else {
      setCurrentPath({ name: '', description: '' });
    }
    setOpenPathDialog(true);
  };
  
  const handleClosePathDialog = () => {
    setOpenPathDialog(false);
  };
  
  const handleSavePath = useCallback(async () => {
    try {
      const url = dialogMode === 'add' 
        ? ENDPOINTS.ADMIN.PATHS
        : `${ENDPOINTS.ADMIN.PATHS}/${currentPath.id}`;
        
      const method = dialogMode === 'add' ? 'POST' : 'PUT';
      
      console.log('Saving path:', {
        url,
        method,
        token,
        data: {
          name: currentPath.name,
          description: currentPath.description
        }
      });
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: currentPath.name,
          description: currentPath.description
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save path');
      }
      
      // Aggiorna la lista
      fetchPaths();
      handleClosePathDialog();
    } catch (error) {
      console.error('Error saving path:', error);
      setError('Error saving path: ' + error.message);
    }
  }, [token, dialogMode, currentPath, fetchPaths, handleClosePathDialog]);
  
  const handleDeletePath = useCallback(async (id) => {
    if (window.confirm('Are you sure you want to delete this path?')) {
      try {
        console.log('Deleting path:', id);
        
        const response = await fetch(`${ENDPOINTS.ADMIN.PATHS}/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to delete path');
        }
        
        // Aggiorna la lista
        fetchPaths();
      } catch (error) {
        console.error('Error deleting path:', error);
        setError('Error deleting path: ' + error.message);
      }
    }
  }, [token, fetchPaths]);

  
  return (
    <Box sx={{ width: '100%' }}>
      <Paper elevation={3}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
          <IconButton
            onClick={() => {
              const tabsContainer = document.querySelector('.MuiTabs-flexContainer');
              if (tabsContainer && tabsContainer.parentElement) {
                tabsContainer.parentElement.scrollBy({ left: -300, behavior: 'smooth' });
              }
            }}
            sx={{ minWidth: 40, zIndex: 10 }}
          >
            <i className="material-icons">keyboard_arrow_left</i>
          </IconButton>
          
          <Box sx={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
            <Tabs 
              value={value} 
              onChange={handleChange} 
              aria-label="admin tabs"
              variant="scrollable"
              scrollButtons={false}
              sx={{ overflowX: 'hidden' }}
            >
              <Tab label="Difficulty Levels" {...a11yProps(0)} />
              <Tab label="Quiz Paths" {...a11yProps(1)} />
              <Tab label="System Stats" {...a11yProps(2)} />
              <Tab label="Users" {...a11yProps(3)} />
              <Tab label="Import Quiz" {...a11yProps(4)} />
              <Tab label="Quiz Management" icon={<QuizIcon />} iconPosition="start" {...a11yProps(5)} />
              <Tab label="User Stats" icon={<BarChartIcon />} iconPosition="start" {...a11yProps(6)} />
              <Tab label="Quiz Categories" icon={<CategoryIcon />} iconPosition="start" {...a11yProps(7)} />
              <Tab label="Quiz Stats" icon={<QuizIcon />} iconPosition="start" {...a11yProps(8)} />
              <Tab label="Difficulty Stats" icon={<SpeedIcon />} iconPosition="start" {...a11yProps(9)} />
              <Tab label="Rewards" icon={<i className="material-icons">card_giftcard</i>} iconPosition="start" {...a11yProps(10)} />
            </Tabs>
          </Box>
          
          <IconButton
            onClick={() => {
              const tabsContainer = document.querySelector('.MuiTabs-flexContainer');
              if (tabsContainer && tabsContainer.parentElement) {
                tabsContainer.parentElement.scrollBy({ left: 300, behavior: 'smooth' });
              }
            }}
            sx={{ minWidth: 40, zIndex: 10 }}
          >
            <i className="material-icons">keyboard_arrow_right</i>
          </IconButton>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {successMessage && (
          <Alert severity="success" sx={{ m: 2 }} onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}
        
        {loading ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography>Loading...</Typography>
          </Box>
        ) : (
          <>
            {/* Difficulty Levels Tab */}
            <TabPanel value={value} index={0}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Difficulty Levels</Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenDifficultyDialog('add')}
                >
                  Add New Level
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {difficultyLevels.map((level) => (
                      <TableRow key={level.id}>
                        <TableCell>{level.id}</TableCell>
                        <TableCell>{level.name}</TableCell>
                        <TableCell>{level.value}</TableCell>
                        <TableCell>
                          <IconButton 
                            color="primary" 
                            onClick={() => handleOpenDifficultyDialog('edit', level)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error" 
                            onClick={() => handleDeleteDifficulty(level.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </TabPanel>
            
            {/* Quiz Paths Tab */}
            <TabPanel value={value} index={1}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Quiz Paths</Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenPathDialog('add')}
                >
                  Add New Path
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paths.map((path) => (
                      <TableRow key={path.id}>
                        <TableCell>{path.id}</TableCell>
                        <TableCell>{path.name}</TableCell>
                        <TableCell>{path.description}</TableCell>
                        <TableCell>
                          <IconButton 
                            color="primary" 
                            onClick={() => handleOpenPathDialog('edit', path)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error" 
                            onClick={() => handleDeletePath(path.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </TabPanel>
            
            {/* System Stats Tab */}
            <TabPanel value={value} index={2}>
              <Typography variant="h6" gutterBottom>System Statistics</Typography>
              
              {stats ? (
                <Box sx={{ mt: 2 }}>
                  <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6">User Statistics</Typography>
                    <Typography>Total Users: {stats.total_users}</Typography>
                    <Typography>Active Users: {stats.active_users}</Typography>
                    <Typography>Admin Users: {stats.admin_users}</Typography>
                  </Paper>
                  
                  <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6">Quiz Statistics</Typography>
                    <Typography>Total Quizzes: {stats.total_quizzes}</Typography>
                    <Typography>Total Questions: {stats.total_questions}</Typography>
                    <Typography>Total Categories: {stats.total_categories}</Typography>
                  </Paper>
                  
                  <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6">System Information</Typography>
                    <Typography>API Version: {stats.api_version}</Typography>
                    <Typography>Environment: {stats.environment}</Typography>
                    <Typography>Server Time: {stats.server_time}</Typography>
                  </Paper>
                </Box>
              ) : (
                <Typography>No statistics available</Typography>
              )}
            </TabPanel>
            
            {/* Users Tab */}
            <TabPanel value={value} index={3}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Users Management</Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={<PersonAddIcon />}
                  onClick={() => handleOpenUserDialog('add')}
                >
                  Add New User
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Points</TableCell>
                      <TableCell>Parents</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.id}</TableCell>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{user.role}</TableCell>
                        <TableCell>{user.is_active ? 'Active' : 'Inactive'}</TableCell>
                        <TableCell>{user.points !== null ? user.points : '-'}</TableCell>
                        <TableCell>
                          {user.parents && user.parents.length > 0 
                            ? user.parents.map(parent => `${parent.username} (${parent.id})`).join(', ')
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <IconButton 
                            color="info" 
                            onClick={() => handleViewUserDetail(user.id)}
                            title="View user details"
                          >
                            <i className="material-icons">visibility</i>
                          </IconButton>
                          <IconButton 
                            color="primary" 
                            onClick={() => handleOpenUserDialog('edit', user)}
                            title="Edit user"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="warning" 
                            onClick={() => handleToggleUserActive(user.id)}
                            title={user.is_active ? 'Deactivate user' : 'Activate user'}
                          >
                            <i className="material-icons">
                              {user.is_active ? 'toggle_on' : 'toggle_off'}
                            </i>
                          </IconButton>
                          {user.role === 'student' && (
                            <IconButton 
                              color="secondary" 
                              onClick={() => {
                                const newPoints = prompt("Enter new points value:", user.points || 0);
                                if (newPoints !== null && !isNaN(newPoints)) {
                                  handleUpdateStudentPoints(user.id, parseInt(newPoints));
                                }
                              }}
                              title="Update points"
                            >
                              <i className="material-icons">stars</i>
                            </IconButton>
                          )}
                          <IconButton 
                            color="error" 
                            onClick={() => handleDeleteUser(user.id)}
                            title="Delete user"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </TabPanel>
            
            {/* Import Quiz Tab */}
            <TabPanel value={value} index={4}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" gutterBottom>Import Quizzes from CSV</Typography>
                <Typography variant="body2" gutterBottom>
                  Upload a CSV file with quiz data. The CSV should have the following columns:
                  question, option1, option2, option3, option4, correct_answer, explanation, difficulty_level, category
                </Typography>
                
                <Box sx={{ mt: 2, mb: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<UploadFileIcon />}
                    onClick={handleOpenImportDialog}
                  >
                    Upload CSV File
                  </Button>
                </Box>
                
                {importResult && (
                  <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Import Results
                    </Typography>
                    <Typography>
                      Successfully imported: {importResult.imported_count} quizzes
                    </Typography>
                    
                    {importResult.errors && importResult.errors.length > 0 && (
                      <>
                        <Typography variant="subtitle1" sx={{ mt: 2, color: 'error.main' }}>
                          Errors ({importResult.errors.length}):
                        </Typography>
                        <Box sx={{ maxHeight: '200px', overflow: 'auto', mt: 1 }}>
                          {importResult.errors.map((error, index) => (
                            <Typography key={index} variant="body2" sx={{ color: 'error.main' }}>
                              • {error}
                            </Typography>
                          ))}
                        </Box>
                      </>
                    )}
                  </Paper>
                )}
              </Box>
            </TabPanel>

            {/* Quiz Management Tab */}
            <TabPanel value={value} index={5}>
              <QuizManagement token={token} />
            </TabPanel>
            
            {/* User Stats Tab */}
            <TabPanel value={value} index={6}>
              <UserStats token={token} />
            </TabPanel>

            {/* Quiz Categories Stats Tab */}
            <TabPanel value={value} index={7}>
              <QuizCategoryStats token={token} />
            </TabPanel>

            {/* Quiz Stats Tab */}
            <TabPanel value={value} index={8}>
              <QuizStats token={token} />
            </TabPanel>

            {/* Difficulty Stats Tab */}
            <TabPanel value={value} index={9}>
              <DifficultyStats token={token} />
            </TabPanel>
            
            {/* Rewards Tab */}
            <TabPanel value={value} index={10}>
              <RewardManagement token={token} />
            </TabPanel>
          </>
        )}
      </Paper>
      
      {/* Dialog per i livelli di difficoltà */}
      <Dialog open={openDifficultyDialog} onClose={handleCloseDifficultyDialog}>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Difficulty Level' : 'Edit Difficulty Level'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {dialogMode === 'add' 
              ? 'Create a new difficulty level for quizzes.' 
              : 'Edit the selected difficulty level.'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            type="text"
            fullWidth
            variant="outlined"
            value={currentDifficulty.name}
            onChange={(e) => setCurrentDifficulty({...currentDifficulty, name: e.target.value})}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Value"
            type="number"
            fullWidth
            variant="outlined"
            value={currentDifficulty.value}
            onChange={(e) => setCurrentDifficulty({...currentDifficulty, value: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDifficultyDialog}>Cancel</Button>
          <Button onClick={handleSaveDifficulty} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog per i percorsi */}
      <Dialog open={openPathDialog} onClose={handleClosePathDialog}>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Quiz Path' : 'Edit Quiz Path'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {dialogMode === 'add' 
              ? 'Create a new quiz path for organizing quizzes.' 
              : 'Edit the selected quiz path.'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            type="text"
            fullWidth
            variant="outlined"
            value={currentPath.name}
            onChange={(e) => setCurrentPath({...currentPath, name: e.target.value})}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={currentPath.description}
            onChange={(e) => setCurrentPath({...currentPath, description: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePathDialog}>Cancel</Button>
          <Button onClick={handleSavePath} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog per gli utenti */}
      <Dialog open={openUserDialog} onClose={handleCloseUserDialog}>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New User' : 'Edit User'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {dialogMode === 'add' 
              ? 'Create a new user with a specific role.' 
              : 'Edit the selected user.'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Username"
            type="text"
            fullWidth
            variant="outlined"
            value={currentUser.username}
            onChange={(e) => setCurrentUser({...currentUser, username: e.target.value})}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Email"
            type="email"
            fullWidth
            variant="outlined"
            value={currentUser.email}
            onChange={(e) => setCurrentUser({...currentUser, email: e.target.value})}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label={dialogMode === 'edit' ? 'New Password (leave empty to keep current)' : 'Password'}
            type="password"
            fullWidth
            variant="outlined"
            value={currentUser.password}
            onChange={(e) => setCurrentUser({...currentUser, password: e.target.value})}
            sx={{ mb: 2 }}
            required={dialogMode === 'add'}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={currentUser.role}
              label="Role"
              onChange={(e) => setCurrentUser({...currentUser, role: e.target.value})}
            >
              <MenuItem value="student">Student</MenuItem>
              <MenuItem value="parent">Parent</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
          {currentUser.role === 'student' && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Parent</InputLabel>
              <Select
                value={currentUser.parent_id || ''}
                label="Parent"
                onChange={(e) => setCurrentUser({...currentUser, parent_id: e.target.value ? parseInt(e.target.value) : null})}
              >
                <MenuItem value="">No Parent</MenuItem>
                {users
                  .filter(user => user.role === 'parent')
                  .map(parent => (
                    <MenuItem key={parent.id} value={parent.id}>
                      {parent.username} ({parent.email})
                    </MenuItem>
                  ))
                }
              </Select>
            </FormControl>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUserDialog}>Cancel</Button>
          <Button onClick={handleSaveUser} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog per l'importazione di quiz */}
      <Dialog open={openImportDialog} onClose={handleCloseImportDialog}>
        <DialogTitle>Import Quizzes from CSV</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Select a CSV file to import quizzes. The CSV should have the following columns:
            question, option1, option2, option3, option4, correct_answer, explanation, difficulty_level, category
          </DialogContentText>
          <Box sx={{ mt: 2 }}>
            <input
              type="file"
              accept=".csv"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={() => fileInputRef.current.click()}
              disabled={importing}
              sx={{ mr: 2 }}
            >
              {importing ? 'Uploading...' : 'Select File'}
            </Button>
            {importing && <CircularProgress size={24} sx={{ ml: 2 }} />}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseImportDialog}>Close</Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog per i dettagli dell'utente */}
      <Dialog 
        open={openUserDetailDialog} 
        onClose={handleCloseUserDetailDialog}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          User Details
          {userDetail && (
            <Typography variant="subtitle1" color="text.secondary">
              {userDetail.username} ({userDetail.role})
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {userDetail ? (
            <Box sx={{ mt: 2 }}>
              {/* Informazioni generali dell'utente */}
              <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6" gutterBottom>General Information</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                  <Typography><strong>ID:</strong> {userDetail.id}</Typography>
                  <Typography><strong>Username:</strong> {userDetail.username}</Typography>
                  <Typography><strong>Email:</strong> {userDetail.email}</Typography>
                  <Typography><strong>Role:</strong> {userDetail.role}</Typography>
                  <Typography><strong>Status:</strong> {userDetail.is_active ? 'Active' : 'Inactive'}</Typography>
                  <Typography><strong>Created:</strong> {new Date(userDetail.created_at).toLocaleString()}</Typography>
                  <Typography><strong>Points:</strong> {userDetail.points !== null ? userDetail.points : '-'}</Typography>
                  <Typography><strong>Last Login:</strong> {userDetail.last_login ? new Date(userDetail.last_login).toLocaleString() : 'Never'}</Typography>
                </Box>
              </Paper>
              
              {/* Se l'utente è uno studente, mostra i quiz completati */}
              {userDetail.role === 'student' && (
                <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>Quiz Progress</Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography><strong>Total Quizzes Attempted:</strong> {userDetail.quiz_count || 0}</Typography>
                    {userQuizzes && (
                      <>
                        <Typography><strong>Correct Answers:</strong> {userQuizzes.correct_answers} / {userQuizzes.total_attempts} ({userQuizzes.total_attempts > 0 ? Math.round((userQuizzes.correct_answers / userQuizzes.total_attempts) * 100) : 0}%)</Typography>
                        <Typography><strong>Total Points Earned:</strong> {userQuizzes.total_points}</Typography>
                      </>
                    )}
                  </Box>
                  
                  {userQuizzes && userQuizzes.attempts && userQuizzes.attempts.length > 0 ? (
                    <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                      <Table stickyHeader size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Question</TableCell>
                            <TableCell>Answer</TableCell>
                            <TableCell>Result</TableCell>
                            <TableCell>Points</TableCell>
                            <TableCell>Date</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {userQuizzes.attempts.map((attempt) => (
                            <TableRow key={attempt.id}>
                              <TableCell>{attempt.question.substring(0, 50)}...</TableCell>
                              <TableCell>{attempt.answer}</TableCell>
                              <TableCell>{attempt.correct ? 'Correct' : 'Incorrect'}</TableCell>
                              <TableCell>{attempt.points_earned}</TableCell>
                              <TableCell>{new Date(attempt.created_at).toLocaleString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Typography>No quiz attempts found.</Typography>
                  )}
                </Paper>
              )}
              
              {/* Se l'utente è uno studente, mostra i genitori associati */}
              {userDetail.role === 'student' && userDetail.parents && userDetail.parents.length > 0 && (
                <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>Parents</Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Username</TableCell>
                          <TableCell>Email</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {userDetail.parents.map((parent) => (
                          <TableRow key={parent.id}>
                            <TableCell>{parent.id}</TableCell>
                            <TableCell>{parent.username}</TableCell>
                            <TableCell>{parent.email}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              )}
              
              {/* Se l'utente è un genitore, mostra i figli associati */}
              {userDetail.role === 'parent' && userDetail.students && userDetail.students.length > 0 && (
                <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>Children</Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Username</TableCell>
                          <TableCell>Email</TableCell>
                          <TableCell>Points</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {userDetail.students.map((student) => (
                          <TableRow key={student.id}>
                            <TableCell>{student.id}</TableCell>
                            <TableCell>{student.username}</TableCell>
                            <TableCell>{student.email}</TableCell>
                            <TableCell>{student.points}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              )}
              
              {/* Se l'utente è un genitore, mostra i progressi dei figli */}
              {userDetail.role === 'parent' && childrenProgress && childrenProgress.children && childrenProgress.children.length > 0 && (
                <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>Children Progress</Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Username</TableCell>
                          <TableCell>Points</TableCell>
                          <TableCell>Quiz Attempts</TableCell>
                          <TableCell>Correct Answers</TableCell>
                          <TableCell>Accuracy</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {childrenProgress.children.map((child) => (
                          <TableRow key={child.id}>
                            <TableCell>{child.username}</TableCell>
                            <TableCell>{child.points}</TableCell>
                            <TableCell>{child.total_attempts}</TableCell>
                            <TableCell>{child.correct_answers}</TableCell>
                            <TableCell>{(child.accuracy * 100).toFixed(1)}%</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              )}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUserDetailDialog}>Close</Button>
          {userDetail && (
            <>
              <Button 
                onClick={() => handleOpenUserDialog('edit', userDetail)} 
                variant="contained" 
                color="primary"
                sx={{ mr: 1 }}
              >
                Edit User
              </Button>
              <Button 
                variant="contained" 
                color={userDetail.is_active ? "error" : "success"}
                onClick={() => handleToggleUserActive(userDetail.id)} 
                sx={{ mr: 1 }}
              >
                {userDetail.is_active ? "Deactivate" : "Activate"}
              </Button>
              {userDetail.role === 'student' && (
                <Button 
                  variant="contained" 
                  color="secondary"
                  onClick={() => {
                    const newPoints = prompt("Enter new points value:", userDetail.points || 0);
                    if (newPoints !== null && !isNaN(newPoints)) {
                      handleUpdateStudentPoints(userDetail.id, parseInt(newPoints));
                    }
                  }} 
                >
                  Update Points
                </Button>
              )}
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPanel;
