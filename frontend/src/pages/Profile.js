import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';

function Profile() {
  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profile
        </Typography>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Your Information
          </Typography>
          {/* Add profile content here */}
        </Paper>
      </Box>
    </Container>
  );
}

export default Profile;
