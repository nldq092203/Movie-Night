import React from 'react';
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from './context/AuthContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <GoogleOAuthProvider clientId="157056602147-fl9u1m1v18av95rk0fabhbm09418sab7.apps.googleusercontent.com"> 
    <AuthProvider>
      <App />
    </AuthProvider>
  </GoogleOAuthProvider>
);


