import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Snackbar,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Grid,
  InputAdornment
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CardGiftcardIcon from '@mui/icons-material/CardGiftcard';
import GroupAddIcon from '@mui/icons-material/GroupAdd';
import { ENDPOINTS } from '../config';

const RewardManagement = ({ token }) => {
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [openBulkAssignDialog, setOpenBulkAssignDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add' or 'edit'
  const [currentReward, setCurrentReward] = useState({
    name: '',
    description: '',
    image_url: '',
    point_cost: 50,
    is_active: true
  });
  const [rewardAssignment, setRewardAssignment] = useState({
    student_id: '',
    reward_id: '',
    quantity: 1
  });
  const [bulkAssignment, setBulkAssignment] = useState({
    student_ids: [],
    reward_id: '',
    quantity: 1
  });
  const [students, setStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);

  // Fetch rewards
  const fetchRewards = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(ENDPOINTS.REWARDS, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching rewards: ${response.status}`);
      }

      const data = await response.json();
      // Handle different response formats (array or {rewards: [...], total: number})
      if (Array.isArray(data)) {
        setRewards(data);
      } else if (data.rewards && Array.isArray(data.rewards)) {
        setRewards(data.rewards);
      } else {
        console.error('Unexpected rewards data format:', data);
        setRewards([]);
      }
    } catch (error) {
      console.error('Error fetching rewards:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch students (for assignment)
  const fetchStudents = useCallback(async () => {
    try {
      const response = await fetch(ENDPOINTS.ADMIN.USERS, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching students: ${response.status}`);
      }

      const data = await response.json();
      // The API response is in the format { users: [...], total: number }
      const usersArray = data.users || data;
      
      // Filter only student users
      const studentUsers = usersArray.filter(user => user.role === 'student');
      setStudents(studentUsers);
    } catch (error) {
      console.error('Error fetching students:', error);
      setError(error.message);
    }
  }, [token]);

  // Load data on component mount
  useEffect(() => {
    fetchRewards();
    fetchStudents();
  }, [fetchRewards, fetchStudents]);

  // Dialog handlers
  const handleOpenDialog = (mode, reward = null) => {
    setDialogMode(mode);
    setCurrentReward(
      mode === 'add'
        ? {
            name: '',
            description: '',
            image_url: '',
            point_cost: 50,
            is_active: true
          }
        : { ...reward }
    );
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleOpenAssignDialog = (rewardId = null) => {
    setRewardAssignment({
      student_id: '',
      reward_id: rewardId || '',
      quantity: 1
    });
    setOpenAssignDialog(true);
  };

  const handleCloseAssignDialog = () => {
    setOpenAssignDialog(false);
  };

  const handleOpenBulkAssignDialog = (rewardId = null) => {
    setBulkAssignment({
      student_ids: [],
      reward_id: rewardId || '',
      quantity: 1
    });
    setSelectedStudents([]);
    setOpenBulkAssignDialog(true);
  };

  const handleCloseBulkAssignDialog = () => {
    setOpenBulkAssignDialog(false);
  };

  // Save reward
  const handleSaveReward = async () => {
    try {
      const url = dialogMode === 'add'
        ? ENDPOINTS.REWARDS
        : `${ENDPOINTS.REWARDS}/${currentReward.id}`;

      const method = dialogMode === 'add' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify(currentReward)
      });

      if (!response.ok) {
        throw new Error(`Failed to ${dialogMode} reward: ${response.status}`);
      }

      fetchRewards();
      handleCloseDialog();
      setSuccessMessage(`Reward ${dialogMode === 'add' ? 'created' : 'updated'} successfully!`);
    } catch (error) {
      console.error(`Error ${dialogMode === 'add' ? 'creating' : 'updating'} reward:`, error);
      setError(error.message);
    }
  };

  // Delete reward
  const handleDeleteReward = async (id) => {
    if (window.confirm('Are you sure you want to delete this reward?')) {
      try {
        const response = await fetch(`${ENDPOINTS.REWARDS}/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        });

        if (!response.ok) {
          throw new Error(`Failed to delete reward: ${response.status}`);
        }

        fetchRewards();
        setSuccessMessage('Reward deleted successfully!');
      } catch (error) {
        console.error('Error deleting reward:', error);
        setError(error.message);
      }
    }
  };

  // Assign reward to student
  const handleAssignReward = async () => {
    try {
      const response = await fetch(`${ENDPOINTS.REWARDS}/assign/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify(rewardAssignment)
      });

      if (!response.ok) {
        throw new Error(`Failed to assign reward: ${response.status}`);
      }

      handleCloseAssignDialog();
      setSuccessMessage('Reward assigned to student successfully!');
    } catch (error) {
      console.error('Error assigning reward:', error);
      setError(error.message);
    }
  };

  // Bulk assign reward to students
  const handleBulkAssignReward = async () => {
    try {
      const payload = {
        ...bulkAssignment,
        student_ids: selectedStudents
      };

      const response = await fetch(`${ENDPOINTS.REWARDS}/assign/bulk/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Failed to bulk assign reward: ${response.status}`);
      }

      handleCloseBulkAssignDialog();
      setSuccessMessage(`Reward assigned to ${selectedStudents.length} students successfully!`);
    } catch (error) {
      console.error('Error bulk assigning reward:', error);
      setError(error.message);
    }
  };

  // Handle student selection for bulk assignment
  const handleStudentSelection = (event) => {
    setSelectedStudents(event.target.value);
  };

  return (
    <div>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Manage Rewards</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('add')}
        >
          Add New Reward
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
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Point Cost</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rewards.map(reward => (
                <TableRow key={reward.id}>
                  <TableCell>{reward.id}</TableCell>
                  <TableCell>{reward.name}</TableCell>
                  <TableCell>{reward.description}</TableCell>
                  <TableCell>{reward.point_cost}</TableCell>
                  <TableCell>{reward.is_active ? 'Yes' : 'No'}</TableCell>
                  <TableCell>
                    <IconButton
                      color="primary"
                      onClick={() => handleOpenDialog('edit', reward)}
                      title="Edit reward"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      color="secondary"
                      onClick={() => handleOpenAssignDialog(reward.id)}
                      title="Assign to student"
                    >
                      <CardGiftcardIcon />
                    </IconButton>
                    <IconButton
                      color="info"
                      onClick={() => handleOpenBulkAssignDialog(reward.id)}
                      title="Bulk assign to multiple students"
                    >
                      <GroupAddIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteReward(reward.id)}
                      title="Delete reward"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add/Edit Reward Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Reward' : 'Edit Reward'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {dialogMode === 'add'
              ? 'Create a new reward for students to purchase with their points.'
              : 'Edit the selected reward.'}
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                margin="dense"
                label="Name"
                type="text"
                fullWidth
                variant="outlined"
                value={currentReward.name}
                onChange={(e) => setCurrentReward({...currentReward, name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Description"
                type="text"
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                value={currentReward.description || ''}
                onChange={(e) => setCurrentReward({...currentReward, description: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Image URL"
                type="text"
                fullWidth
                variant="outlined"
                value={currentReward.image_url || ''}
                onChange={(e) => setCurrentReward({...currentReward, image_url: e.target.value})}
                helperText="URL to an image for this reward (optional)"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                margin="dense"
                label="Point Cost"
                type="number"
                fullWidth
                variant="outlined"
                value={currentReward.point_cost}
                onChange={(e) => setCurrentReward({...currentReward, point_cost: parseInt(e.target.value, 10) || 0})}
                InputProps={{
                  startAdornment: <InputAdornment position="start">🔶</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="reward-status-label">Status</InputLabel>
                <Select
                  labelId="reward-status-label"
                  value={currentReward.is_active}
                  label="Status"
                  onChange={(e) => setCurrentReward({...currentReward, is_active: e.target.value})}
                >
                  <MenuItem value={true}>Active</MenuItem>
                  <MenuItem value={false}>Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveReward} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Assign Reward Dialog */}
      <Dialog open={openAssignDialog} onClose={handleCloseAssignDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Reward to Student</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Select a student and specify the quantity to add to their shop.
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="student-select-label">Student</InputLabel>
                <Select
                  labelId="student-select-label"
                  value={rewardAssignment.student_id}
                  label="Student"
                  onChange={(e) => setRewardAssignment({...rewardAssignment, student_id: e.target.value})}
                >
                  {students.map(student => (
                    <MenuItem key={student.id} value={student.id}>
                      {student.username} ({student.email})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="reward-select-label">Reward</InputLabel>
                <Select
                  labelId="reward-select-label"
                  value={rewardAssignment.reward_id}
                  label="Reward"
                  onChange={(e) => setRewardAssignment({...rewardAssignment, reward_id: e.target.value})}
                  disabled={!!rewardAssignment.reward_id}
                >
                  {rewards.map(reward => (
                    <MenuItem key={reward.id} value={reward.id}>
                      {reward.name} ({reward.point_cost} points)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Quantity"
                type="number"
                fullWidth
                variant="outlined"
                value={rewardAssignment.quantity}
                onChange={(e) => setRewardAssignment({...rewardAssignment, quantity: parseInt(e.target.value, 10) || 1})}
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAssignDialog}>Cancel</Button>
          <Button 
            onClick={handleAssignReward} 
            variant="contained" 
            color="primary"
            disabled={!rewardAssignment.student_id || !rewardAssignment.reward_id || rewardAssignment.quantity < 1}
          >
            Assign
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Assign Reward Dialog */}
      <Dialog open={openBulkAssignDialog} onClose={handleCloseBulkAssignDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Bulk Assign Reward to Students</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Select multiple students to assign this reward to their shops.
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="multiple-student-select-label">Students</InputLabel>
                <Select
                  labelId="multiple-student-select-label"
                  multiple
                  value={selectedStudents}
                  label="Students"
                  onChange={handleStudentSelection}
                >
                  {students.map(student => (
                    <MenuItem key={student.id} value={student.id}>
                      {student.username} ({student.email})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="bulk-reward-select-label">Reward</InputLabel>
                <Select
                  labelId="bulk-reward-select-label"
                  value={bulkAssignment.reward_id}
                  label="Reward"
                  onChange={(e) => setBulkAssignment({...bulkAssignment, reward_id: e.target.value})}
                  disabled={!!bulkAssignment.reward_id}
                >
                  {rewards.map(reward => (
                    <MenuItem key={reward.id} value={reward.id}>
                      {reward.name} ({reward.point_cost} points)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Quantity per Student"
                type="number"
                fullWidth
                variant="outlined"
                value={bulkAssignment.quantity}
                onChange={(e) => setBulkAssignment({...bulkAssignment, quantity: parseInt(e.target.value, 10) || 1})}
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseBulkAssignDialog}>Cancel</Button>
          <Button 
            onClick={handleBulkAssignReward} 
            variant="contained" 
            color="primary"
            disabled={selectedStudents.length === 0 || !bulkAssignment.reward_id || bulkAssignment.quantity < 1}
          >
            Assign to {selectedStudents.length} Students
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default RewardManagement;
