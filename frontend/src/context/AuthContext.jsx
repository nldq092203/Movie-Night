import { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token') || null);
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token') || null);

  // Function to decode the JWT token manually
  const decodeToken = (token) => {
    try {
      const base64Url = token.split('.')[1]; // Get the payload part of the JWT
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/'); // Replace URL-safe characters
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join('')
      );
      const decoded = JSON.parse(jsonPayload);
      setUser({ email: decoded.email, id: decoded.user_id });
    } catch (e) {
      console.error('Error decoding token:', e);
    }
  };

  // Login function - stores tokens and user data
  const loginUser = async (credentials) => {
    try {
      const response = await axios.post('http://0.0.0.0:8000/auth/token/', credentials);
      const { access, refresh } = response.data;
      setAccessToken(access);
      setRefreshToken(refresh);
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      decodeToken(access); // Decode and set user info from the access token
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  // Google Login Function - handles Google login and sets tokens
  const googleLogin = (tokens) => {
    const { access, refresh } = tokens; // Corrected token names
    setAccessToken(access);
    setRefreshToken(refresh);
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    decodeToken(access); // Decode and set user info from the access token
  };

  // Logout function
  const logoutUser = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  // Function to refresh access token
  const refreshAccessToken = async () => {
    try {
      const response = await axios.post('http://0.0.0.0:8000/auth/token/refresh/', {
        refresh: refreshToken,
      });
      const newAccessToken = response.data.access;
      setAccessToken(newAccessToken);
      localStorage.setItem('access_token', newAccessToken);
      decodeToken(newAccessToken); // Decode and set user info from the new access token
    } catch (err) {
      console.error('Error refreshing access token:', err);
      logoutUser(); // Logout the user if refreshing fails
    }
  };

  // Attach access token to every API request if logged in
  useEffect(() => {
    if (accessToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      decodeToken(accessToken); // Ensure user is set on initial load if accessToken exists
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [accessToken]);

  const isAuthenticated = !!accessToken; // Check if accessToken exists

  return (
    <AuthContext.Provider
      value={{
        user,
        loginUser,
        googleLogin,
        logoutUser,
        refreshAccessToken,
        isAuthenticated, // Pass the authentication status
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};