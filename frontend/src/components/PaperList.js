
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemButton,
  Divider,
  CircularProgress,
  Alert 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getPapers } from '../services/api';

const PaperList = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPapers = async () => {
      try {
        const data = await getPapers();
        setPapers(data);
      } catch (err) {
        console.error('Error fetching papers:', err);
        setError('Failed to load papers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPapers();
  }, []);

  const handlePaperClick = (paperId) => {
    navigate(`/papers/${paperId}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Research Papers
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      {papers.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No papers found. Upload your first paper to get started!
          </Typography>
        </Paper>
      ) : (
        <Paper>
          <List>
            {papers.map((paper, index) => (
              <React.Fragment key={paper.id}>
                <ListItem disablePadding>
                  <ListItemButton onClick={() => handlePaperClick(paper.id)}>
                    <ListItemText 
                      primary={paper.title}
                      secondary={
                        paper.labels && paper.labels.length > 0 
                          ? `Labels: ${paper.labels.map(label => label.name).join(', ')}` 
                          : 'No labels'
                      }
                    />
                  </ListItemButton>
                </ListItem>
                {index < papers.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default PaperList;
