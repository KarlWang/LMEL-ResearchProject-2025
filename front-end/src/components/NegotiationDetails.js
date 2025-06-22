import React, { useState } from 'react';
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
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

function NegotiationDetails({ tasks, satellites }) {
    const [selectedSatellite, setSelectedSatellite] = useState(null);

    const handleSatelliteClick = (satellite) => {
        setSelectedSatellite(satellite);
    };

    const handleClose = () => {
        setSelectedSatellite(null);
    };

    return (
        <Box sx={{ p: 2 }}>
            {satellites && (
                <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Created Satellites
                    </Typography>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Name</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Memory Capacity</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Available Memory</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {satellites.map((satellite) => (
                                    <TableRow 
                                        key={satellite.name}
                                        onClick={() => handleSatelliteClick(satellite)}
                                        sx={{ 
                                            cursor: 'pointer',
                                            '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                                        }}
                                    >
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{satellite.name}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{satellite.memory_capacity}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{satellite.available_memory}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            )}

            <Dialog 
                open={selectedSatellite !== null} 
                onClose={handleClose}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    Coalition Table for {selectedSatellite?.name}
                    <IconButton
                        aria-label="close"
                        onClick={handleClose}
                        sx={{
                            position: 'absolute',
                            right: 8,
                            top: 8,
                            color: (theme) => theme.palette.grey[500],
                        }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent>
                    {selectedSatellite?.coalition_table && (
                        <TableContainer>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>Task ID</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>Preferred Satellites</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>Priority</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {selectedSatellite.coalition_table.preferences.map((pref, index) => (
                                        <TableRow key={index}>
                                            <TableCell sx={{ whiteSpace: 'nowrap' }}>{pref.task_id}</TableCell>
                                            <TableCell sx={{ whiteSpace: 'nowrap' }}>{pref.preferred_satellites.join(', ')}</TableCell>
                                            <TableCell sx={{ whiteSpace: 'nowrap' }}>{pref.priority}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </DialogContent>
            </Dialog>

            {tasks && (
                <Paper elevation={3} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Created Tasks
                    </Typography>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>ID</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Location Index</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Time Windows</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Reward</TableCell>
                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>Memory Required</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {tasks.map((task) => (
                                    <TableRow key={task.id}>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{task.id}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{task.location_index}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>
                                            {task.time_window.map((window, idx) => (
                                                <div key={idx}>
                                                    {window.start_time}:00 - {window.end_time}:00
                                                </div>
                                            ))}
                                        </TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{task.reward_points}</TableCell>
                                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{task.memory_required}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            )}
        </Box>
    );
}

export default NegotiationDetails; 