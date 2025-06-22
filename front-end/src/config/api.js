const API_CONFIG = {
    baseURL: 'http://localhost:8000', // Backend URL
    endpoints: {
        createSatellites: '/create-satellites',
        createTasks: '/create-tasks',
        startNegotiation: '/start-negotiation',
        getResults: '/negotiation-results',
        saveData: '/save-data',
        loadData: '/load-data'
    }
};

export default API_CONFIG; 