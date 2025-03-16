
import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert 
} from '@mui/material';
import { UploadFile } from '@mui/icons-material';
import { uploadPaper, updateTitle } from '../services/api';
import { useNavigate } from 'react-router-dom';

const PaperUpload = () => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please select a valid PDF file');
    }
  };

  const handleTitleChange = (event) => {
    setTitle(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    if (!title.trim()) {
      setError('Please enter a title for the paper');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // First upload the PDF to extract text
      const uploadResponse = await uploadPaper(file);
      const paper_id = uploadResponse.paper_id;

      const response = await updateTitle(paper_id, title);
      
      setSuccess('Paper uploaded successfully!');
      
      // Navigate to the paper details page after a short delay
      setTimeout(() => {
        navigate(`/papers/${response.data.id}`);
      }, 1500);
      
    } catch (err) {
      console.error('Error uploading paper:', err);
      setError(err.response?.data?.message || 'Error uploading paper. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Upload Research Paper
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Paper Title"
            value={title}
            onChange={handleTitleChange}
            margin="normal"
            required
          />
          
          <Box sx={{ mt: 2, mb: 3 }}>
            <input
              accept="application/pdf"
              id="upload-pdf-file"
              type="file"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <label htmlFor="upload-pdf-file">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadFile />}
                sx={{ mr: 2 }}
              >
                Select PDF
              </Button>
              {file && file.name}
            </label>
          </Box>
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Upload Paper'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default PaperUpload;
