import axios from 'axios';

export const chatApi = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,  // Matches backend timeout
});
