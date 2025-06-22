import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Box, Typography, Paper, Button, CircularProgress, Alert, Accordion, AccordionSummary, AccordionDetails, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { getNegotiationResults } from '../services/negotiationService';

function NegotiationDetailPage() {
    const { taskId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [negotiationDetails, setNegotiationDetails] = useState(null);

    useEffect(() => {
        const fetchNegotiationDetails = async () => {
            try {
                setLoading(true);
                const results = await getNegotiationResults();
                const negotiationData = results?.results || results;

                if (!negotiationData || !negotiationData.negotiation_results) {
                    throw new Error('No negotiation results available');
                }

                // Check if we're dealing with multi-initiator results
                const isMultiInitiator = Array.isArray(negotiationData.negotiation_results) && 
                                       Array.isArray(negotiationData.negotiation_results[0]);
                
                let taskResult;
                if (isMultiInitiator) {
                    // Search through all initiators' results
                    for (const initiatorResults of negotiationData.negotiation_results) {
                        taskResult = initiatorResults.find(
                            result => result.task_id === parseInt(taskId)
                        );
                        if (taskResult) break;
                    }
                } else {
                    // Single initiator format
                    taskResult = negotiationData.negotiation_results.find(
                        result => result.task_id === parseInt(taskId)
                    );
                }
                
                if (taskResult) {
                    setNegotiationDetails(taskResult);
                } else {
                    setError('Negotiation details not found');
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchNegotiationDetails();
    }, [taskId]);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ mt: 4 }}>
                {error}
            </Alert>
        );
    }

    if (!negotiationDetails) {
        return (
            <Alert severity="info" sx={{ mt: 4 }}>
                No negotiation details available
            </Alert>
        );
    }

    return (
        <Box sx={{ p: 2 }}>
            <Paper elevation={3} sx={{ p: 3, maxWidth: '100%', mx: 'auto' }}>
                <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h4">Task {negotiationDetails.task_id} - Location {negotiationDetails.location_index}</Typography>
                    <Button component={Link} to="/" variant="contained" color="primary">
                        Back to Results
                    </Button>
                </Box>
                {negotiationDetails.negotiations && negotiationDetails.negotiations.map((negotiation, index) => (
                    <Accordion key={index} sx={{ mb: 2 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="subtitle1">
                                    Coalition: {negotiation.coalition.join(', ')}
                                </Typography>
                                <Typography 
                                    variant="body2" 
                                    color={negotiation.agreement ? 'success.main' : 'error.main'}
                                >
                                    {negotiation.agreement ? 'Agreement Reached' : 'No Agreement'}
                                </Typography>
                            </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Box sx={{ p: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Negotiation Result
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    {negotiation.result}
                                </Typography>

                                {negotiation.agreement_details && (
                                    <>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Agreement Details
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {negotiation.agreement_details}
                                        </Typography>
                                    </>
                                )}

                                {negotiation.negotiation_details && (
                                    <>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Memory Checks
                                        </Typography>
                                        <TableContainer sx={{ mb: 2 }}>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Time</TableCell>
                                                        <TableCell>Available Memory</TableCell>
                                                        <TableCell>Required Memory</TableCell>
                                                        <TableCell>Has Enough Memory</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {negotiation.negotiation_details.memory_checks.map((check, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell>{check.time.toFixed(2)}</TableCell>
                                                            <TableCell>{check.available_memory}</TableCell>
                                                            <TableCell>{check.required_memory}</TableCell>
                                                            <TableCell>{check.has_enough_memory ? 'Yes' : 'No'}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>

                                        <Typography variant="subtitle2" gutterBottom>
                                            Utility Calculations
                                        </Typography>
                                        <TableContainer sx={{ mb: 2 }}>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Time</TableCell>
                                                        <TableCell>Base Utility</TableCell>
                                                        <TableCell>Reward Factor</TableCell>
                                                        <TableCell>Memory Factor</TableCell>
                                                        <TableCell>Memory Availability</TableCell>
                                                        <TableCell>Adjusted Utility</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {negotiation.negotiation_details.utility_calculations.map((calc, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell>{calc.time.toFixed(2)}</TableCell>
                                                            <TableCell>{calc.base_utility.toFixed(4)}</TableCell>
                                                            <TableCell>{calc.reward_factor.toFixed(4)}</TableCell>
                                                            <TableCell>{calc.memory_factor.toFixed(4)}</TableCell>
                                                            <TableCell>{calc.memory_availability_factor.toFixed(4)}</TableCell>
                                                            <TableCell>{calc.adjusted_utility.toFixed(4)}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>

                                        <Typography variant="subtitle2" gutterBottom>
                                            Proposals
                                        </Typography>
                                        <TableContainer sx={{ mb: 2 }}>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Time</TableCell>
                                                        <TableCell>Satellite</TableCell>
                                                        <TableCell>Phase</TableCell>
                                                        <TableCell>Outcome</TableCell>
                                                        <TableCell>Base Utility</TableCell>
                                                        <TableCell>Adjusted Utility</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {negotiation.negotiation_details.proposals.map((proposal, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell>{proposal.time.toFixed(2)}</TableCell>
                                                            <TableCell>{proposal.satellite}</TableCell>
                                                            <TableCell>{proposal.phase}</TableCell>
                                                            <TableCell>{proposal.outcome}</TableCell>
                                                            <TableCell>{proposal.base_utility.toFixed(4)}</TableCell>
                                                            <TableCell>{proposal.adjusted_utility.toFixed(4)}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>

                                        <Typography variant="subtitle2" gutterBottom>
                                            Responses
                                        </Typography>
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Time</TableCell>
                                                        <TableCell>Satellite</TableCell>
                                                        <TableCell>Phase</TableCell>
                                                        <TableCell>Offer</TableCell>
                                                        <TableCell>Base Utility</TableCell>
                                                        <TableCell>Adjusted Utility</TableCell>
                                                        <TableCell>Base Threshold</TableCell>
                                                        <TableCell>Adjusted Threshold</TableCell>
                                                        <TableCell>Response</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {negotiation.negotiation_details.responses.map((response, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell>{response.time.toFixed(2)}</TableCell>
                                                            <TableCell>{response.satellite}</TableCell>
                                                            <TableCell>{response.phase}</TableCell>
                                                            <TableCell sx={{ whiteSpace: 'nowrap' }}>{response.offer}</TableCell>
                                                            <TableCell>{response.base_utility.toFixed(4)}</TableCell>
                                                            <TableCell>{response.adjusted_utility.toFixed(4)}</TableCell>
                                                            <TableCell>{response.base_threshold.toFixed(4)}</TableCell>
                                                            <TableCell>{response.adjusted_threshold.toFixed(4)}</TableCell>
                                                            <TableCell>{response.response}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </>
                                )}
                            </Box>
                        </AccordionDetails>
                    </Accordion>
                ))}
            </Paper>
        </Box>
    );
}

export default NegotiationDetailPage; 