import api from './api';
import API_CONFIG from '../config/api';

export const createSatellites = async (numSatellites) => {
    try {
        const response = await api.post(API_CONFIG.endpoints.createSatellites, {
            num_satellites: numSatellites,
            num_tasks: 0 // Not used for satellite creation
        });
        return response.data.satellites;
    } catch (error) {
        console.error('Error creating satellites:', error);
        throw error;
    }
};

export const createTasks = async (numTasks) => {
    try {
        const response = await api.post(API_CONFIG.endpoints.createTasks, {
            num_satellites: 0, // Not used for task creation
            num_tasks: numTasks
        });
        return response.data.tasks;
    } catch (error) {
        console.error('Error creating tasks:', error);
        throw error;
    }
};

export const startNegotiation = async (numSatellites, numTasks, initiator) => {
    try {
        const response = await api.post(API_CONFIG.endpoints.startNegotiation, {
            num_satellites: numSatellites,
            num_tasks: numTasks,
            negotiator_version: 'v031',
            initiator: initiator === 'all' ? '' : initiator  // Send empty string for multi-initiator
        });
        return response.data;
    } catch (error) {
        console.error('Error starting negotiation:', error);
        throw error;
    }
};

export const getNegotiationResults = async () => {
    try {
        const response = await api.get(API_CONFIG.endpoints.getResults);
        return response.data;
    } catch (error) {
        console.error('Error fetching negotiation results:', error);
        throw error;
    }
};

export const saveData = async (filename) => {
    try {
        console.log("=========================== API_CONFIG.endpoints.saveData: ", API_CONFIG.endpoints.saveData);
        const response = await api.post(API_CONFIG.endpoints.saveData, { filename });
        console.log("=========================== DONE ========================================");
        return response.data;
    } catch (error) {
        console.error('Error saving data:', error);
        throw error;
    }
};

export const loadData = async (filename) => {
    try {
        const response = await api.post(API_CONFIG.endpoints.loadData, { filename });
        return response.data;
    } catch (error) {
        console.error('Error loading data:', error);
        throw error;
    }
}; 