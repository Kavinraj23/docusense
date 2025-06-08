import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI base URL
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export default api;