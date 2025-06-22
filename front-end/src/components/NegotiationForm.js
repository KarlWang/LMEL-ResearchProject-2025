import React, { useState, useEffect } from 'react';
import { 
    Box, 
    Button, 
    TextField, 
    Typography, 
    Paper,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Divider,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import { createSatellites, createTasks, startNegotiation } from '../services/negotiationService';

const NegotiationForm = ({ onNegotiationStarted, onTasksCreated, onSatellitesCreated, onReset, createdTasks, createdSatellites }) => {
    const [numSatellites, setNumSatellites] = useState(3);
    const [numTasks, setNumTasks] = useState(5);
    const [initiator, setInitiator] = useState('all');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (createdSatellites) {
            setInitiator('all');
        }
    }, [createdSatellites]);

    const handleCreateTasks = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await createTasks(numTasks);
            onTasksCreated(result);
        } catch (err) {
            setError('Failed to create tasks. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateSatellites = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await createSatellites(numSatellites);
            onSatellitesCreated(result);
        } catch (err) {
            setError('Failed to create satellites. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleStartNegotiation = async () => {
        setLoading(true);
        setError(null);
        try {
            const results = await startNegotiation(numSatellites, numTasks, initiator);
            onNegotiationStarted(results);
        } catch (err) {
            setError('Failed to start negotiation. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        onTasksCreated(null);
        onSatellitesCreated(null);
        onNegotiationStarted(null);
        onReset();
        setError(null);
        setInitiator('all');
    };

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                    Negotiation Setup
                </Typography>
                <Button 
                    variant="outlined" 
                    color="error"
                    onClick={handleReset}
                    disabled={!createdTasks && !createdSatellites}
                >
                    Reset
                </Button>
            </Box>
            
            <Box component="form" noValidate>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <TextField
                        required
                        type="number"
                        label="Number of Tasks"
                        value={numTasks}
                        onChange={(e) => setNumTasks(parseInt(e.target.value))}
                        inputProps={{ min: 1 }}
                        disabled={loading || createdTasks !== null}
                        sx={{ flex: 1 }}
                    />
                    <Button
                        variant="contained"
                        disabled={loading || createdTasks !== null}
                        onClick={handleCreateTasks}
                        sx={{ height: 56 }}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Create Tasks'}
                    </Button>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <TextField
                        required
                        type="number"
                        label="Number of Satellites"
                        value={numSatellites}
                        onChange={(e) => setNumSatellites(parseInt(e.target.value))}
                        inputProps={{ min: 1 }}
                        disabled={loading || createdSatellites !== null}
                        sx={{ flex: 1 }}
                    />
                    <Button
                        variant="contained"
                        disabled={loading || createdSatellites !== null}
                        onClick={handleCreateSatellites}
                        sx={{ height: 56 }}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Create Satellites'}
                    </Button>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <FormControl fullWidth disabled={loading || !createdSatellites}>
                        <InputLabel>Initiator</InputLabel>
                        <Select
                            value={initiator}
                            label="Initiator"
                            onChange={(e) => setInitiator(e.target.value)}
                        >
                            <MenuItem value="all">
                                <Typography>
                                    All Satellites (Multi-initiator)
                                </Typography>
                            </MenuItem>
                            <Divider />
                            {createdSatellites?.map((satellite) => (
                                <MenuItem key={satellite.name} value={satellite.name}>
                                    {satellite.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    disabled={loading || !createdTasks || !createdSatellites}
                    onClick={handleStartNegotiation}
                >
                    {loading ? <CircularProgress size={24} /> : 'Start Negotiation'}
                </Button>

                {error && (
                    <Typography color="error" sx={{ mt: 2 }}>
                        {error}
                    </Typography>
                )}
            </Box>
        </Paper>
    );
};

export default NegotiationForm; 