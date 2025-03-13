
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  TextField,
  Grid,
  Autocomplete,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  getPaperSummary,
  getPaperSummaryLatex,
  searchLabels,
  getKeywords,
  addLabel,
  removeLabel,
  getAllLabels,
  createLabel
} from '../services/api';

const PaperDetails = () => {
  const { paperId } = useParams();
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [suggestedLabels, setSuggestedLabels] = useState([]);
  const [allLabels, setAllLabels] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState(null);
  const [newLabelName, setNewLabelName] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [paperLabels, setPaperLabels] = useState([]);

  useEffect(() => {
    const fetchPaperDetails = async () => {
      setLoading(true);
      try {
        // Fetch summary
        const summaryData = await getPaperSummary(paperId);
        setSummary(summaryData.summary);
        
        // Fetch keywords
        try {
          const keywordsData = await getKeywords(paperId);
          setKeywords(keywordsData.keywords || []);
        } catch (err) {
          console.error('Error fetching keywords:', err);
        }
        
        // Fetch suggested labels
        try {
          const labelsData = await searchLabels(paperId);
          setSuggestedLabels(labelsData || []);
          if (labelsData && labelsData.length > 0) {
            // Assuming the paper labels are included in the response
            setPaperLabels(labelsData.filter(label => label.is_attached) || []);
          }
        } catch (err) {
          console.error('Error fetching suggested labels:', err);
        }
        
        // Fetch all labels
        try {
          const allLabelsData = await getAllLabels();
          setAllLabels(allLabelsData || []);
        } catch (err) {
          console.error('Error fetching all labels:', err);
        }
      } catch (err) {
        console.error('Error fetching paper details:', err);
        setError('Failed to load paper details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPaperDetails();
  }, [paperId]);

  const handleDownloadLatex = async () => {
    try {
      const blob = await getPaperSummaryLatex(paperId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `summary_${paperId}.tex`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('Error downloading LaTeX summary:', err);
      setError('Failed to download LaTeX summary. Please try again later.');
    }
  };

  const handleAddLabel = async () => {
    if (!selectedLabel) return;
    
    try {
      await addLabel(paperId, selectedLabel.id);
      // Update paper labels
      setPaperLabels([...paperLabels, selectedLabel]);
      setSelectedLabel(null);
    } catch (err) {
      console.error('Error adding label:', err);
      setError('Failed to add label. Please try again.');
    }
  };

  const handleRemoveLabel = async (labelId) => {
    try {
      await removeLabel(paperId, labelId);
      // Update paper labels
      setPaperLabels(paperLabels.filter(label => label.id !== labelId));
    } catch (err) {
      console.error('Error removing label:', err);
      setError('Failed to remove label. Please try again.');
    }
  };

  const handleCreateNewLabel = async () => {
    if (!newLabelName.trim()) return;
    
    try {
      const newLabel = await createLabel(newLabelName);
      setAllLabels([...allLabels, newLabel]);
      setSelectedLabel(newLabel);
      setNewLabelName('');
      setOpenDialog(false);
    } catch (err) {
      console.error('Error creating new label:', err);
      setError('Failed to create new label. Please try again.');
    }
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
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Paper Summary
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {summary}
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleDownloadLatex}
          >
            Download as LaTeX
          </Button>
        </Box>
      </Paper>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Paper Labels
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Current Labels:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {paperLabels.length > 0 ? (
              paperLabels.map((label) => (
                <Chip 
                  key={label.id} 
                  label={label.name} 
                  onDelete={() => handleRemoveLabel(label.id)} 
                  color="primary" 
                  variant="outlined"
                />
              ))
            ) : (
              <Typography color="text.secondary">No labels attached to this paper</Typography>
            )}
          </Box>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Add Label:
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={8}>
              <Autocomplete
                value={selectedLabel}
                onChange={(event, newValue) => setSelectedLabel(newValue)}
                options={allLabels}
                getOptionLabel={(option) => option.name}
                renderInput={(params) => <TextField {...params} label="Select a label" />}
                isOptionEqualToValue={(option, value) => option.id === value.id}
              />
            </Grid>
            <Grid item xs={4} sx={{ display: 'flex', alignItems: 'center' }}>
              <Button 
                variant="contained" 
                onClick={handleAddLabel}
                disabled={!selectedLabel}
                sx={{ mr: 1 }}
              >
                Add
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => setOpenDialog(true)}
              >
                New
              </Button>
            </Grid>
          </Grid>
        </Box>
        
        {keywords.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Paper Keywords:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {keywords.map((keyword, index) => (
                <Chip key={index} label={keyword} color="secondary" variant="outlined" />
              ))}
            </Box>
          </Box>
        )}
        
        {suggestedLabels.length > 0 && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Suggested Labels:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestedLabels.filter(label => !paperLabels.some(pl => pl.id === label.id)).map((label) => (
                <Chip 
                  key={label.id} 
                  label={label.name} 
                  onClick={() => {
                    setSelectedLabel(label);
                    handleAddLabel();
                  }} 
                  color="info" 
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>
      
      {/* Dialog for creating a new label */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Create New Label</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Label Name"
            type="text"
            fullWidth
            value={newLabelName}
            onChange={(e) => setNewLabelName(e.target.value)}
          />
          {keywords.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Consider using one of these keywords:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {keywords.map((keyword, index) => (
                  <Chip 
                    key={index} 
                    label={keyword} 
                    onClick={() => setNewLabelName(keyword)} 
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateNewLabel} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PaperDetails;
