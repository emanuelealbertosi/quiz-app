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
  Alert,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CardGiftcardIcon from '@mui/icons-material/CardGiftcard';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { ENDPOINTS } from '../config';

// TabPanel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`parent-rewards-tabpanel-${index}`}
      aria-labelledby={`parent-rewards-tab-${index}`}
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
    id: `parent-rewards-tab-${index}`,
    'aria-controls': `parent-rewards-tabpanel-${index}`,
  };
}

const ParentRewardManagement = ({ token }) => {
  const [tabValue, setTabValue] = useState(0);
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentRewards, setStudentRewards] = useState([]);
  const [studentPurchases, setStudentPurchases] = useState([]);
  const [openAssignDialog, setOpenAssignDialog] = useState(false);
  const [rewardAssignment, setRewardAssignment] = useState({
    student_id: '',
    reward_id: '',
    quantity: 1
  });

  // Fetch all available rewards
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

  // Fetch children of the parent
  const fetchStudents = useCallback(async () => {
    try {
      const response = await fetch(ENDPOINTS.ME, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching user info: ${response.status}`);
      }

      const userData = await response.json();
      
      if (userData.students && Array.isArray(userData.students)) {
        setStudents(userData.students);
        
        // If we have students, select the first one by default
        if (userData.students.length > 0 && !selectedStudent) {
          setSelectedStudent(userData.students[0].id);
          fetchStudentRewards(userData.students[0].id);
          fetchStudentPurchases(userData.students[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching students:', error);
      setError(error.message);
    }
  }, [token, selectedStudent]);

  // Fetch rewards in a student's shop
  const fetchStudentRewards = useCallback(async (studentId) => {
    if (!studentId) return;
    
    try {
      setLoading(true);
      
      // Use the dedicated parent endpoint to view a student's shop
      const response = await fetch(ENDPOINTS.PARENT.STUDENT_SHOP(studentId), {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching student rewards: ${response.status}`);
      }

      const data = await response.json();
      setStudentRewards(data);
    } catch (error) {
      console.error('Error fetching student rewards:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch a student's purchase history
  const fetchStudentPurchases = useCallback(async (studentId) => {
    if (!studentId) return;
    
    try {
      const response = await fetch(`${ENDPOINTS.ADMIN.PURCHASES}/${studentId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching student purchases: ${response.status}`);
      }

      const data = await response.json();
      setStudentPurchases(data);
    } catch (error) {
      console.error('Error fetching student purchases:', error);
      setError(error.message);
    }
  }, [token]);

  // Load data on component mount
  useEffect(() => {
    fetchRewards();
    fetchStudents();
  }, [fetchRewards, fetchStudents]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle student change
  const handleStudentChange = (event) => {
    const studentId = event.target.value;
    setSelectedStudent(studentId);
    fetchStudentRewards(studentId);
    fetchStudentPurchases(studentId);
  };

  // Dialog handlers
  const handleOpenAssignDialog = () => {
    setRewardAssignment({
      student_id: selectedStudent,
      reward_id: '',
      quantity: 1
    });
    setOpenAssignDialog(true);
  };

  const handleCloseAssignDialog = () => {
    setOpenAssignDialog(false);
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

      // Refresh student rewards
      fetchStudentRewards(selectedStudent);
      handleCloseAssignDialog();
      setSuccessMessage('Reward assigned to student successfully!');
    } catch (error) {
      console.error('Error assigning reward:', error);
      setError(error.message);
    }
  };

  // Remove reward from student's shop
  const handleRemoveReward = async (rewardId) => {
    if (window.confirm('Are you sure you want to remove this reward from the student\'s shop?')) {
      try {
        const response = await fetch(`${ENDPOINTS.REWARDS}/remove-from-shop/${selectedStudent}/${rewardId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`Failed to remove reward: ${response.status}`);
        }

        // Refresh student rewards
        fetchStudentRewards(selectedStudent);
        setSuccessMessage('Reward removed from student\'s shop successfully!');
      } catch (error) {
        console.error('Error removing reward:', error);
        setError(error.message);
      }
    }
  };

  // Update purchase delivery status
  const handleUpdatePurchaseStatus = async (purchaseId, isDelivered) => {
    try {
      const response = await fetch(`${ENDPOINTS.ADMIN.PURCHASES}/${purchaseId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          is_delivered: isDelivered
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to update purchase status: ${response.status}`);
      }

      // Refresh student purchases
      fetchStudentPurchases(selectedStudent);
      setSuccessMessage('Purchase status updated successfully!');
    } catch (error) {
      console.error('Error updating purchase status:', error);
      setError(error.message);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Get reward name by ID
  const getRewardName = (rewardId) => {
    const reward = rewards.find(r => r.id === rewardId);
    return reward ? reward.name : 'Unknown Reward';
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Manage Your Child's Rewards
      </Typography>

      {/* Student Selection */}
      {students.length > 0 && (
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="student-select-label">Select Child</InputLabel>
          <Select
            labelId="student-select-label"
            value={selectedStudent || ''}
            label="Select Child"
            onChange={handleStudentChange}
          >
            {students.map(student => (
              <MenuItem key={student.id} value={student.id}>
                {student.username}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Error and Success Messages */}
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

      {/* No Students Message */}
      {students.length === 0 && !loading && (
        <Alert severity="info" sx={{ mb: 2 }}>
          You don't have any children registered. Please contact an administrator.
        </Alert>
      )}

      {selectedStudent && (
        <>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="reward management tabs">
              <Tab label="Student's Shop" {...a11yProps(0)} />
              <Tab label="Purchase History" {...a11yProps(1)} />
            </Tabs>
          </Box>

          {/* Student's Shop Tab */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleOpenAssignDialog}
              >
                Add Reward to Shop
              </Button>
            </Box>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {studentRewards.length === 0 ? (
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1">
                      This student's shop is empty. Add some rewards for them!
                    </Typography>
                  </Paper>
                ) : (
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Description</TableCell>
                          <TableCell>Point Cost</TableCell>
                          <TableCell>Quantity</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {studentRewards.map(reward => (
                          <TableRow key={reward.id}>
                            <TableCell>{reward.name}</TableCell>
                            <TableCell>{reward.description || 'No description'}</TableCell>
                            <TableCell>{reward.point_cost}</TableCell>
                            <TableCell>{reward.quantity}</TableCell>
                            <TableCell>
                              <IconButton
                                color="error"
                                onClick={() => handleRemoveReward(reward.id)}
                                title="Remove from shop"
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
              </>
            )}
          </TabPanel>

          {/* Purchase History Tab */}
          <TabPanel value={tabValue} index={1}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {studentPurchases.length === 0 ? (
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1">
                      This student hasn't purchased any rewards yet.
                    </Typography>
                  </Paper>
                ) : (
                  <Grid container spacing={2}>
                    {studentPurchases.map(purchase => (
                      <Grid item xs={12} key={purchase.id}>
                        <Card sx={{ mb: 1 }}>
                          <CardContent>
                            <Grid container spacing={2}>
                              <Grid item xs={12} md={9}>
                                <Typography variant="h6">
                                  {getRewardName(purchase.reward_id)}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Purchased on {formatDate(purchase.created_at)}
                                </Typography>
                                <Typography variant="body2" sx={{ mt: 1 }}>
                                  Cost: <Chip size="small" label={`${purchase.point_cost} points`} color="primary" />
                                </Typography>
                              </Grid>
                              <Grid item xs={12} md={3} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                <Chip
                                  label={purchase.is_delivered ? 'Delivered' : 'Pending'}
                                  color={purchase.is_delivered ? 'success' : 'warning'}
                                  sx={{ mb: 1 }}
                                />
                                <Button
                                  variant="outlined"
                                  size="small"
                                  color={purchase.is_delivered ? 'error' : 'success'}
                                  startIcon={purchase.is_delivered ? <DeleteIcon /> : <CheckCircleIcon />}
                                  onClick={() => handleUpdatePurchaseStatus(purchase.id, !purchase.is_delivered)}
                                >
                                  {purchase.is_delivered ? 'Mark Not Delivered' : 'Mark Delivered'}
                                </Button>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </>
            )}
          </TabPanel>
        </>
      )}

      {/* Assign Reward Dialog */}
      <Dialog open={openAssignDialog} onClose={handleCloseAssignDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Add Reward to Student's Shop</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Select a reward to add to this student's shop.
          </DialogContentText>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth margin="dense">
                <InputLabel id="reward-select-label">Reward</InputLabel>
                <Select
                  labelId="reward-select-label"
                  value={rewardAssignment.reward_id}
                  label="Reward"
                  onChange={(e) => setRewardAssignment({...rewardAssignment, reward_id: e.target.value})}
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
            disabled={!rewardAssignment.reward_id || rewardAssignment.quantity < 1}
          >
            Add to Shop
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ParentRewardManagement;
