import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('ProtectedRoute checking token:', token ? `${token.substring(0, 10)}...` : 'null or empty');
    
    if (token) {
      console.log('Token found, user is authenticated');
      setIsAuthenticated(true);
    } else {
      console.log('No token found, user is not authenticated');
      setIsAuthenticated(false);
    }
  }, []);
  
  // Mostra un messaggio di caricamento mentre controlliamo il token
  if (isAuthenticated === null) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>
          <h2>Verifica autenticazione...</h2>
          <p>Controllo del token in corso</p>
        </div>
      </div>
    );
  }
  
  // Reindirizza alla pagina di login se non c'è token
  if (!isAuthenticated) {
    console.log('No token found, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  // Se c'è un token, mostra il contenuto protetto
  return children;
};

export default ProtectedRoute;
