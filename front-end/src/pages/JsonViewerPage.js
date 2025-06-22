import React, { useState } from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import JsonViewer from '../components/JsonViewer';

const JsonViewerPage = () => {
    const [jsonData, setJsonData] = useState(null);
    const [error, setError] = useState(null);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    setJsonData(data);
                    setError(null);
                } catch (err) {
                    setError('Invalid JSON file');
                    setJsonData(null);
                }
            };
            reader.readAsText(file);
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="h5" gutterBottom>
                    Load Negotiation Results
                </Typography>
                <Button
                    variant="contained"
                    component="label"
                    sx={{ mb: 2 }}
                >
                    Load JSON File
                    <input
                        type="file"
                        hidden
                        accept=".json"
                        onChange={handleFileUpload}
                    />
                </Button>
                {error && (
                    <Typography color="error" sx={{ mt: 2 }}>
                        {error}
                    </Typography>
                )}
            </Paper>
            <JsonViewer data={jsonData} />
        </Box>
    );
};

export default JsonViewerPage; 