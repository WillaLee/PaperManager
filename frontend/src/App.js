
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container } from '@mui/material';
import Navigation from './components/Navigation';
import PaperUpload from './components/PaperUpload';
import PaperList from './components/PaperList';
import PaperDetails from './components/PaperDetails';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navigation />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<PaperList />} />
            <Route path="/upload" element={<PaperUpload />} />
            <Route path="/papers/:paperId" element={<PaperDetails />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;
