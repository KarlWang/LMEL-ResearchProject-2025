import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

function JsonViewer({ data }) {
    if (!data) {
        return (
            <Box sx={{ p: 2 }}>
                <Typography>No data available</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ 
            width: '100%',
            p: 2,
            overflowX: 'auto'
        }}>
            {/* Timestamp */}
            <Typography variant="h6" gutterBottom>
                Timestamp: {data.timestamp}
            </Typography>

            {/* Satellites */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>Satellites</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Memory Capacity</TableCell>
                                <TableCell>Available Memory</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.satellites.map((satellite, index) => (
                                <TableRow key={index}>
                                    <TableCell>{satellite.name}</TableCell>
                                    <TableCell>{satellite.memory_capacity}</TableCell>
                                    <TableCell>{satellite.available_memory}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Tasks */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>Tasks</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Location Index</TableCell>
                                <TableCell>Time Windows</TableCell>
                                <TableCell>Reward Points</TableCell>
                                <TableCell>Memory Required</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.tasks.map((task, index) => (
                                <TableRow key={index}>
                                    <TableCell>{task.id}</TableCell>
                                    <TableCell>{task.location_index}</TableCell>
                                    <TableCell>
                                        {task.time_window.map((window, idx) => (
                                            <div key={idx}>
                                                {window.start_time}:00 - {window.end_time}:00
                                            </div>
                                        ))}
                                    </TableCell>
                                    <TableCell>{task.reward_points}</TableCell>
                                    <TableCell>{task.memory_required}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Coalition Tables */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>Coalition Tables</Typography>
                {data.coalition_tables.map((table, index) => (
                    <Accordion key={index}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Satellite: {table.satellite}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Task ID</TableCell>
                                            <TableCell>Preferred Satellites</TableCell>
                                            <TableCell>Priority</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {table.preferences.map((pref, idx) => (
                                            <TableRow key={idx}>
                                                <TableCell>{pref.task_id}</TableCell>
                                                <TableCell>{pref.preferred_satellites.join(', ')}</TableCell>
                                                <TableCell>{pref.priority}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </AccordionDetails>
                    </Accordion>
                ))}
            </Paper>

            {/* Negotiation Results */}
            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Negotiation Results</Typography>
                {data.negotiation_results.map((initiatorResults, initiatorIndex) => (
                    <Accordion key={initiatorIndex}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Initiator: {data.coalition_tables[initiatorIndex].satellite}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {initiatorResults.map((taskResult, taskIndex) => (
                                <Accordion key={taskIndex}>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography>Task {taskResult.task_id} - {taskResult.location}</Typography>
                                            <Chip
                                                icon={taskResult.negotiations.some(n => n.agreement) ? 
                                                    <CheckCircleIcon /> : <CancelIcon />}
                                                label={taskResult.negotiations.some(n => n.agreement) ? 
                                                    "Agreement Reached" : "No Agreement"}
                                                color={taskResult.negotiations.some(n => n.agreement) ? 
                                                    "success" : "error"}
                                                size="small"
                                            />
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        {taskResult.negotiations.map((negotiation, negIndex) => (
                                            <Accordion key={negIndex}>
                                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Typography>
                                                            Coalition: {negotiation.coalition.join(', ')}
                                                        </Typography>
                                                        <Chip
                                                            icon={negotiation.agreement ? 
                                                                <CheckCircleIcon /> : <CancelIcon />}
                                                            label={negotiation.agreement ? 
                                                                "Agreement" : "No Agreement"}
                                                            color={negotiation.agreement ? 
                                                                "success" : "error"}
                                                            size="small"
                                                        />
                                                    </Box>
                                                </AccordionSummary>
                                                <AccordionDetails>
                                                    <Box sx={{ mb: 2 }}>
                                                        <Typography variant="subtitle2">Result</Typography>
                                                        <Box sx={{ 
                                                            overflowX: 'auto',
                                                            whiteSpace: 'nowrap',
                                                            backgroundColor: 'background.paper',
                                                            p: 1,
                                                            borderRadius: 1,
                                                            border: '1px solid',
                                                            borderColor: 'divider'
                                                        }}>
                                                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                                                {negotiation.result}
                                                            </Typography>
                                                        </Box>
                                                    </Box>

                                                    <Box sx={{ mb: 2 }}>
                                                        <Typography variant="subtitle2">Agreement Details</Typography>
                                                        <Typography variant="body2">
                                                            {negotiation.agreement_details}
                                                        </Typography>
                                                    </Box>

                                                    <Box sx={{ mb: 2 }}>
                                                        <Typography variant="subtitle2">Memory Checks</Typography>
                                                        <TableContainer>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow>
                                                                        <TableCell>Time</TableCell>
                                                                        <TableCell>Available Memory</TableCell>
                                                                        <TableCell>Required Memory</TableCell>
                                                                        <TableCell>Result</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {negotiation.negotiation_details.memory_checks?.map((check, idx) => (
                                                                        <TableRow key={idx}>
                                                                            <TableCell>{check.time?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{check.available_memory || 'N/A'}</TableCell>
                                                                            <TableCell>{check.required_memory || 'N/A'}</TableCell>
                                                                            <TableCell>
                                                                                <Chip
                                                                                    icon={check.has_enough_memory ? 
                                                                                        <CheckCircleIcon /> : <CancelIcon />}
                                                                                    label={check.has_enough_memory ? 
                                                                                        "Pass" : "Fail"}
                                                                                    color={check.has_enough_memory ? 
                                                                                        "success" : "error"}
                                                                                    size="small"
                                                                                />
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    )) || (
                                                                        <TableRow>
                                                                            <TableCell colSpan={4} align="center">
                                                                                No memory checks available
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    )}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    </Box>

                                                    <Box sx={{ mb: 2 }}>
                                                        <Typography variant="subtitle2">Utility Calculations</Typography>
                                                        <TableContainer>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow>
                                                                        <TableCell>Time</TableCell>
                                                                        <TableCell>Outcome/Offer</TableCell>
                                                                        <TableCell>Base Utility</TableCell>
                                                                        <TableCell>Reward Factor</TableCell>
                                                                        <TableCell>Memory Factor</TableCell>
                                                                        <TableCell>Memory Availability</TableCell>
                                                                        <TableCell>Adjusted Utility</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {negotiation.negotiation_details.utility_calculations?.map((calc, idx) => (
                                                                        <TableRow key={idx}>
                                                                            <TableCell>{calc.time?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.outcome || calc.offer || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.base_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.reward_factor?.toFixed(3) || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.memory_factor?.toFixed(3) || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.memory_availability_factor?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{calc.adjusted_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                        </TableRow>
                                                                    )) || (
                                                                        <TableRow>
                                                                            <TableCell colSpan={7} align="center">
                                                                                No utility calculations available
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    )}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    </Box>

                                                    <Box sx={{ mb: 2 }}>
                                                        <Typography variant="subtitle2">Proposals</Typography>
                                                        <TableContainer>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow>
                                                                        <TableCell>Time</TableCell>
                                                                        <TableCell>Satellite</TableCell>
                                                                        <TableCell>Phase</TableCell>
                                                                        <TableCell>Outcome</TableCell>
                                                                        <TableCell>Base Utility</TableCell>
                                                                        <TableCell>Adjusted Utility</TableCell>
                                                                        <TableCell>Selected Index</TableCell>
                                                                        <TableCell>Total Outcomes</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {negotiation.negotiation_details.proposals?.map((prop, idx) => (
                                                                        <TableRow key={idx}>
                                                                            <TableCell>{prop.time?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.satellite || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.phase || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.outcome || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.base_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.adjusted_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.selected_index || 'N/A'}</TableCell>
                                                                            <TableCell>{prop.total_outcomes || 'N/A'}</TableCell>
                                                                        </TableRow>
                                                                    )) || (
                                                                        <TableRow>
                                                                            <TableCell colSpan={8} align="center">
                                                                                No proposals available
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    )}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    </Box>

                                                    <Box>
                                                        <Typography variant="subtitle2">Responses</Typography>
                                                        <TableContainer>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow>
                                                                        <TableCell>Time</TableCell>
                                                                        <TableCell>Satellite</TableCell>
                                                                        <TableCell>Phase</TableCell>
                                                                        <TableCell sx={{ 
                                                                            whiteSpace: 'nowrap',
                                                                            overflowX: 'auto',
                                                                            maxWidth: '300px'
                                                                        }}>Offer</TableCell>
                                                                        <TableCell>Base Utility</TableCell>
                                                                        <TableCell>Adjusted Utility</TableCell>
                                                                        <TableCell>Base Threshold</TableCell>
                                                                        <TableCell>Adjusted Threshold</TableCell>
                                                                        <TableCell>Response</TableCell>
                                                                        <TableCell>Step</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {negotiation.negotiation_details.responses?.map((resp, idx) => (
                                                                        <TableRow key={idx}>
                                                                            <TableCell>{resp.time?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.satellite || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.phase || 'N/A'}</TableCell>
                                                                            <TableCell sx={{ 
                                                                                whiteSpace: 'nowrap',
                                                                                overflowX: 'auto',
                                                                                maxWidth: '300px'
                                                                            }}>{resp.offer || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.base_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.adjusted_utility?.toFixed(2) || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.base_threshold?.toFixed(3) || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.adjusted_threshold?.toFixed(3) || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.response || 'N/A'}</TableCell>
                                                                            <TableCell>{resp.current_step}/{resp.total_steps}</TableCell>
                                                                        </TableRow>
                                                                    )) || (
                                                                        <TableRow>
                                                                            <TableCell colSpan={10} align="center">
                                                                                No responses available
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    )}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    </Box>
                                                </AccordionDetails>
                                            </Accordion>
                                        ))}
                                    </AccordionDetails>
                                </Accordion>
                            ))}
                        </AccordionDetails>
                    </Accordion>
                ))}
            </Paper>
        </Box>
    );
}

export default JsonViewer; 