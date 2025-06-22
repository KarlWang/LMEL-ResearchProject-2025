import React, { useEffect, useState } from 'react';
import {
    Box,
    Typography,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    CircularProgress,
    Alert,
    Link
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { getNegotiationResults } from '../services/negotiationService';
import { useNavigate } from 'react-router-dom';

const NegotiationResults = ({ refreshTrigger, directResults }) => {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const fetchResults = async () => {
        setLoading(true);
        try {
            const data = await getNegotiationResults();
            setResults(data);
        } catch (err) {
            setError('Failed to fetch negotiation results');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (directResults) {
            setResults(directResults);
            setLoading(false);
            setError(null);
        } else if (refreshTrigger > 0) {
            fetchResults();
        } else {
            setResults(null);
            setLoading(false);
            setError(null);
        }
    }, [refreshTrigger, directResults]);

    // Helper function to process negotiation results
    const processNegotiationResults = (results) => {
        console.log('Raw results:', results);
        
        // Handle the nested results structure
        const negotiationData = results?.results || results;
        console.log('Negotiation data:', negotiationData);

        if (!negotiationData || !negotiationData.negotiation_results) {
            console.log('No negotiation data or negotiation_results');
            return [];
        }

        console.log('Negotiation results:', negotiationData.negotiation_results);
        
        // Check if we're dealing with multi-initiator results
        const isMultiInitiator = Array.isArray(negotiationData.negotiation_results) && 
                                Array.isArray(negotiationData.negotiation_results[0]);
        
        console.log('Is multi-initiator?', isMultiInitiator);

        if (!isMultiInitiator) {
            // Single initiator format
            console.log('Processing single initiator results');
            return negotiationData.negotiation_results;
        } else {
            // Multi-initiator format - combine all results
            console.log('Processing multi-initiator results');
            return negotiationData.negotiation_results.reduce((acc, initiatorResults) => {
                return acc.concat(initiatorResults.map(result => ({
                    ...result,
                    initiator: result.initiator || initiatorResults[0]?.initiator
                })));
            }, []);
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ m: 2 }}>
                {error}
            </Alert>
        );
    }

    if (!results) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography variant="h4" gutterBottom>
                    Satellite Negotiation Results
                </Typography>
                <Typography align="center" color="text.secondary">
                    No negotiation results available
                </Typography>
            </Box>
        );
    }

    const processedResults = processNegotiationResults(results);
    console.log('Processed results:', processedResults);

    return (
        <Box sx={{ p: 3 }}>
            <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                    Negotiation Results
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    Timestamp: {results.timestamp}
                </Typography>

                <TableContainer>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell sx={{ whiteSpace: 'nowrap' }}>Initiator</TableCell>
                                <TableCell sx={{ whiteSpace: 'nowrap' }}>Partner</TableCell>
                                <TableCell sx={{ whiteSpace: 'nowrap' }}>Task ID</TableCell>
                                <TableCell sx={{ whiteSpace: 'nowrap' }}>Location Index</TableCell>
                                <TableCell sx={{ whiteSpace: 'nowrap' }}>Status</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {processedResults.map((taskResult, index) => {
                                console.log('Processing task result:', taskResult);
                                const successfulNegotiation = taskResult.negotiations.find(n => n.agreement);
                                const initiator = taskResult.initiator || 
                                                (results.results?.coalition_tables && results.results.coalition_tables[index]?.satellite) || 
                                                (results.coalition_tables && results.coalition_tables[index]?.satellite) ||
                                                'N/A';
                                const partner = successfulNegotiation?.coalition?.join(', ') || 'N/A';
                                
                                return (
                                    <TableRow 
                                        key={`${taskResult.task_id}-${index}`}
                                        onClick={() => navigate(`/negotiation/${taskResult.task_id}`)}
                                        sx={{ 
                                            cursor: 'pointer',
                                            '&:hover': {
                                                backgroundColor: 'action.hover'
                                            }
                                        }}
                                    >
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{initiator}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{partner}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{taskResult.task_id}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{taskResult.location_index}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>
                                            {successfulNegotiation ? (
                                                <Typography color="success.main">
                                                    Agreement Reached
                                                </Typography>
                                            ) : (
                                                <Typography color="error.main">
                                                    No Agreement
                                                </Typography>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
};

export default NegotiationResults; 