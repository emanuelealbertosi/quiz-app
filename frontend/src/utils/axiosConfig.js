import axios from 'axios';

// Configurazione degli interceptor di axios per aggiungere automaticamente il token di autenticazione
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor per gestire gli errori di autenticazione (401)
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.log('Token non valido o scaduto, logout in corso...');
      // Opzionale: reindirizza alla pagina di login se c'è un errore 401
      // localStorage.removeItem('token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axios;
