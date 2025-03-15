
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
import { uploadPaper, createPaper } from '../services/api';
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
      const { text, paper_id } = uploadResponse;
      
      // TODO: generate summary and keywords with onnx runtime
      const hard_coded_key_words = ["machine learning", "Transformer", "Google"];
      const hard_coded_summary = "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.";
      const response = await createPaper(paper_id, title, hard_coded_summary, hard_coded_key_words);
      
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
