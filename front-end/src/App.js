import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container, Paper, Typography, TableContainer, Table, TableHead, TableBody, TableRow, TableCell } from '@mui/material';
import Layout from './components/Layout';
import NegotiationForm from './components/NegotiationForm';
import NegotiationResults from './components/NegotiationResults';
import NegotiationDetails from './components/NegotiationDetails';
import NegotiationDetailPage from './components/NegotiationDetailPage';
import JsonViewerPage from './pages/JsonViewerPage';
import { getNegotiationResults } from './services/negotiationService';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [negotiationResults, setNegotiationResults] = useState(null);
  const [directResults, setDirectResults] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [createdTasks, setCreatedTasks] = useState(null);
  const [createdSatellites, setCreatedSatellites] = useState(null);

  // Clear results when app starts
  useEffect(() => {
    setNegotiationResults(null);
    setDirectResults(null);
  }, []);

  const handleNegotiationStarted = (results) => {
    setDirectResults(results);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleReset = () => {
    setCreatedTasks(null);
    setCreatedSatellites(null);
    setDirectResults(null);
    setNegotiationResults(null);
    setRefreshTrigger(0);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout
          tasks={createdTasks}
          satellites={createdSatellites}
          onTasksCreated={setCreatedTasks}
          onSatellitesCreated={setCreatedSatellites}
        >
          <Container maxWidth="lg">
            <Routes>
              <Route
                path="/"
                element={
                  <>
                    <Box sx={{ mb: 4, maxWidth: '98%', mx: 'auto' }}>
                      <NegotiationForm 
                        onNegotiationStarted={handleNegotiationStarted}
                        onTasksCreated={setCreatedTasks}
                        onSatellitesCreated={setCreatedSatellites}
                        onReset={handleReset}
                        createdTasks={createdTasks}
                        createdSatellites={createdSatellites}
                      />
                    </Box>

                    <Box sx={{ mb: 4, maxWidth: '98%', mx: 'auto' }}>
                      <NegotiationDetails
                        tasks={createdTasks}
                        satellites={createdSatellites}
                      />
                    </Box>

                    <Box sx={{ maxWidth: '98%', mx: 'auto' }}>
                      <NegotiationResults
                        refreshTrigger={refreshTrigger}
                        directResults={directResults}
                      />
                    </Box>
                  </>
                }
              />
              <Route
                path="/negotiation/:taskId"
                element={<NegotiationDetailPage />}
              />
              <Route
                path="/json-viewer"
                element={<JsonViewerPage />}
              />
            </Routes>
          </Container>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
