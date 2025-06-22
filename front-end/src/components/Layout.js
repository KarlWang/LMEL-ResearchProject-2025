import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import SaveLoadForm from './SaveLoadForm';

function Layout({ children, tasks, satellites, onTasksCreated, onSatellitesCreated }) {
    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Satellite Negotiation System
                    </Typography>
                    <SaveLoadForm
                        tasks={tasks}
                        satellites={satellites}
                        onTasksCreated={onTasksCreated}
                        onSatellitesCreated={onSatellitesCreated}
                    />
                </Toolbar>
            </AppBar>
            <Box sx={{ p: 2 }}>
                {children}
            </Box>
        </Box>
    );
}

export default Layout; 