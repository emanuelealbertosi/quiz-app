import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Button,
  Grid,
  Divider,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Alert,
  Snackbar,
  CircularProgress,
  Chip,
  Paper,
  useTheme
} from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import HistoryIcon from '@mui/icons-material/History';
import CardGiftcardIcon from '@mui/icons-material/CardGiftcard';
import { ENDPOINTS } from '../config';

const RewardShop = ({ token, userPoints, onPointsUpdated }) => {
  const theme = useTheme();
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [openPurchaseDialog, setOpenPurchaseDialog] = useState(false);
  const [selectedReward, setSelectedReward] = useState(null);
  const [purchases, setPurchases] = useState([]);
  const [showPurchaseHistory, setShowPurchaseHistory] = useState(false);

  // Fetch rewards in student's shop
  const fetchRewards = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(ENDPOINTS.STUDENT.SHOP, {
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
      setRewards(data);
    } catch (error) {
      console.error('Error fetching rewards:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch purchase history
  const fetchPurchaseHistory = useCallback(async () => {
    try {
      const response = await fetch(ENDPOINTS.STUDENT.PURCHASES, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`Error fetching purchase history: ${response.status}`);
      }

      const data = await response.json();
      setPurchases(data);
    } catch (error) {
      console.error('Error fetching purchase history:', error);
      setError(error.message);
    }
  }, [token]);

  // Load data on component mount
  useEffect(() => {
    fetchRewards();
    fetchPurchaseHistory();
  }, [fetchRewards, fetchPurchaseHistory]);

  // Handle opening purchase dialog
  const handleOpenPurchaseDialog = (reward) => {
    setSelectedReward(reward);
    setOpenPurchaseDialog(true);
  };

  // Handle closing purchase dialog
  const handleClosePurchaseDialog = () => {
    setOpenPurchaseDialog(false);
  };

  // Handle reward purchase
  const handlePurchaseReward = async () => {
    try {
      const response = await fetch(ENDPOINTS.STUDENT.PURCHASE, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          reward_id: selectedReward.id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to purchase reward: ${response.status}`);
      }

      // Close dialog
      handleClosePurchaseDialog();
      
      // Update rewards and purchase history
      fetchRewards();
      fetchPurchaseHistory();
      
      // Update points if callback is provided
      if (onPointsUpdated) {
        onPointsUpdated(userPoints - selectedReward.point_cost);
      }
      
      setSuccess(`You have successfully purchased "${selectedReward.name}"!`);
    } catch (error) {
      console.error('Error purchasing reward:', error);
      setError(error.message);
      handleClosePurchaseDialog();
    }
  };

  // Toggle between shop and purchase history
  const togglePurchaseHistory = () => {
    setShowPurchaseHistory(!showPurchaseHistory);
  };

  // Get reward details for a purchase
  const getRewardDetails = (purchaseItem) => {
    const reward = rewards.find(r => r.id === purchaseItem.reward_id);
    return reward || { name: 'Unknown Reward', description: 'Details not available' };
  };

  // Placeholder image for rewards without an image URL
  const getImageUrl = (reward) => {
    return reward.image_url || 'https://via.placeholder.com/300x200?text=Reward';
  };

  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Shop Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 2
      }}>
        <Typography variant="h5" component="h2" sx={{ 
          fontWeight: 'bold',
          color: theme.palette.primary.main,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          {showPurchaseHistory ? (
            <>
              <HistoryIcon /> Purchase History
            </>
          ) : (
            <>
              <CardGiftcardIcon /> Rewards Shop
            </>
          )}
        </Typography>
        
        <Box>
          <Chip 
            label={`${userPoints} Points`} 
            color="primary" 
            sx={{ mr: 2, fontWeight: 'bold' }}
          />
          <Button
            variant="outlined"
            color={showPurchaseHistory ? "primary" : "secondary"}
            startIcon={showPurchaseHistory ? <ShoppingCartIcon /> : <HistoryIcon />}
            onClick={togglePurchaseHistory}
          >
            {showPurchaseHistory ? 'Back to Shop' : 'View Purchase History'}
          </Button>
        </Box>
      </Box>

      {/* Error and Success Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Show either Shop or Purchase History */}
      {!loading && (
        <>
          {/* Shop View */}
          {!showPurchaseHistory && (
            <>
              {rewards.length === 0 ? (
                <Paper sx={{ p: 3, textAlign: 'center', borderRadius: 2 }}>
                  <Typography variant="h6" color="text.secondary">
                    Your shop is empty
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                    No rewards are available for purchase at the moment. Check back later!
                  </Typography>
                </Paper>
              ) : (
                <Grid container spacing={3}>
                  {rewards.map((reward) => (
                    <Grid item xs={12} sm={6} md={4} key={`${reward.id}-${reward.quantity}`}>
                      <Card 
                        sx={{ 
                          height: '100%', 
                          display: 'flex', 
                          flexDirection: 'column',
                          transition: 'transform 0.2s, box-shadow 0.2s',
                          '&:hover': {
                            transform: 'translateY(-5px)',
                            boxShadow: 6
                          }
                        }}
                      >
                        <CardMedia
                          component="img"
                          height="140"
                          image={getImageUrl(reward)}
                          alt={reward.name}
                        />
                        <CardContent sx={{ flexGrow: 1 }}>
                          <Box sx={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'start',
                            mb: 1
                          }}>
                            <Typography gutterBottom variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                              {reward.name}
                            </Typography>
                            <Chip 
                              label={`${reward.point_cost} pts`} 
                              color={userPoints >= reward.point_cost ? "primary" : "default"}
                              size="small"
                            />
                          </Box>
                          
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {reward.description || 'No description available.'}
                          </Typography>
                          
                          <Box sx={{ 
                            display: 'flex', 
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            mt: 'auto'
                          }}>
                            <Chip 
                              label={`Quantity: ${reward.quantity}`} 
                              size="small" 
                              variant="outlined"
                            />
                            <Button
                              variant="contained"
                              color="primary"
                              size="small"
                              onClick={() => handleOpenPurchaseDialog(reward)}
                              disabled={userPoints < reward.point_cost}
                            >
                              Get Reward
                            </Button>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </>
          )}

          {/* Purchase History View */}
          {showPurchaseHistory && (
            <>
              {purchases.length === 0 ? (
                <Paper sx={{ p: 3, textAlign: 'center', borderRadius: 2 }}>
                  <Typography variant="h6" color="text.secondary">
                    No purchase history
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                    You haven't purchased any rewards yet. Visit the shop to get some!
                  </Typography>
                </Paper>
              ) : (
                <Paper sx={{ p: 2, borderRadius: 2 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Your Purchase History
                  </Typography>
                  {purchases.map((purchase) => {
                    const purchaseDate = formatDate(purchase.created_at);
                    return (
                      <Card key={purchase.id} sx={{ mb: 2, borderRadius: 2 }}>
                        <Box sx={{ p: 2, display: 'flex', flexDirection: { xs: 'column', sm: 'row' } }}>
                          <Box sx={{ 
                            flex: 1, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            justifyContent: 'space-between'
                          }}>
                            <Typography variant="h6" component="div">
                              {rewards.find(r => r.id === purchase.reward_id)?.name || 'Reward'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              {rewards.find(r => r.id === purchase.reward_id)?.description || 'No description available'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Purchased: {purchaseDate}
                            </Typography>
                          </Box>
                          <Box sx={{ 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: { xs: 'flex-start', sm: 'flex-end' },
                            justifyContent: 'space-between',
                            mt: { xs: 2, sm: 0 }
                          }}>
                            <Chip 
                              label={`${purchase.point_cost} points`} 
                              color="primary" 
                              size="small" 
                              sx={{ mb: 1 }}
                            />
                            <Chip 
                              label={purchase.is_delivered ? 'Delivered' : 'Pending'} 
                              color={purchase.is_delivered ? 'success' : 'warning'} 
                              size="small" 
                            />
                          </Box>
                        </Box>
                      </Card>
                    );
                  })}
                </Paper>
              )}
            </>
          )}
        </>
      )}

      {/* Purchase Confirmation Dialog */}
      <Dialog
        open={openPurchaseDialog}
        onClose={handleClosePurchaseDialog}
        aria-labelledby="purchase-dialog-title"
      >
        <DialogTitle id="purchase-dialog-title">Confirm Purchase</DialogTitle>
        <DialogContent>
          {selectedReward && (
            <>
              <DialogContentText>
                Are you sure you want to purchase "{selectedReward.name}" for {selectedReward.point_cost} points?
              </DialogContentText>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">
                  Your current points: {userPoints}
                </Typography>
                <Typography variant="subtitle2">
                  Points after purchase: {userPoints - selectedReward.point_cost}
                </Typography>
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePurchaseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handlePurchaseReward} color="primary" variant="contained">
            Purchase
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RewardShop;
