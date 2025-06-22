import React, { useState } from 'react';
import {
    TextField,
    Button,
    Alert,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Paper,
    Snackbar,
    Typography,
    Divider,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import HomeIcon from '@mui/icons-material/Home';
import { saveData, loadData } from '../services/negotiationService';
import { useNavigate, useLocation } from 'react-router-dom';

function SaveLoadForm({ tasks, satellites, onTasksCreated, onSatellitesCreated }) {
    const [filename, setFilename] = useState('');
    const [currentFile, setCurrentFile] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);
    const navigate = useNavigate();
    const location = useLocation();

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleCloseSnackbar = () => {
        setMessage({ type: '', text: '' });
    };

    const handleSave = async () => {
        try {
            if (!filename) {
                setMessage({ type: 'error', text: 'Please enter a filename' });
                return;
            }
            if (!tasks || !satellites) {
                setMessage({ type: 'error', text: 'No data to save. Please create tasks and satellites first.' });
                return;
            }
            await saveData(filename);
            setCurrentFile(filename);
            setMessage({ type: 'success', text: 'Data saved successfully' });
            handleClose();
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Error saving data' });
        }
    };

    const handleLoad = async () => {
        try {
            if (!filename) {
                setMessage({ type: 'error', text: 'Please enter a filename' });
                return;
            }
            const data = await loadData(filename);
            onTasksCreated(data.tasks);
            onSatellitesCreated(data.satellites);
            setCurrentFile(filename);
            setMessage({ type: 'success', text: 'Data loaded successfully' });
            handleClose();
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Error loading data' });
        }
    };

    return (
        <>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {currentFile && (
                    <Typography 
                        variant="body2" 
                        sx={{ 
                            mr: 2,
                            color: 'text.primary',
                            fontStyle: 'italic'
                        }}
                    >
                        Current Setup: {currentFile}
                    </Typography>
                )}
                <IconButton
                    onClick={handleClick}
                    size="small"
                    sx={{ ml: 2 }}
                    aria-controls={open ? 'save-load-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={open ? 'true' : undefined}
                >
                    <MoreVertIcon />
                </IconButton>
                <Menu
                    anchorEl={anchorEl}
                    id="save-load-menu"
                    open={open}
                    onClose={handleClose}
                    onClick={handleClose}
                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                >
                    {location.pathname !== '/' && (
                        <MenuItem onClick={() => navigate('/')}>
                            <HomeIcon sx={{ mr: 1 }} />
                            Back to Main
                        </MenuItem>
                    )}
                    <Divider />
                    <MenuItem onClick={() => navigate('/json-viewer')}>
                        View Negotiation Results
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={handleClose}>
                        <TextField
                            size="small"
                            placeholder="Configuration file name"
                            value={filename}
                            onChange={(e) => setFilename(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                        />
                    </MenuItem>
                    <MenuItem onClick={handleSave}>
                        <SaveIcon sx={{ mr: 1 }} />
                        Save
                    </MenuItem>
                    <MenuItem onClick={handleLoad}>
                        <FolderOpenIcon sx={{ mr: 1 }} />
                        Load
                    </MenuItem>
                </Menu>
            </Box>
            <Snackbar
                open={message.type !== ''}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={message.type}
                    sx={{ width: '100%' }}
                >
                    {message.text}
                </Alert>
            </Snackbar>
        </>
    );
}

export default SaveLoadForm; 