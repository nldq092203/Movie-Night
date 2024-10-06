import React, { createContext, useState, useContext } from 'react';

// Create context
const MovieNightContext = createContext();

// Provider component
export const MovieNightProvider = ({ children }) => {
  const [invitationData, setInvitationData] = useState(null); // Store invitation details here

  // Set the invitation data when you need to
  const saveInvitationData = (data) => {
    setInvitationData(data);
  };

  return (
    <MovieNightContext.Provider value={{ invitationData, saveInvitationData }}>
      {children}
    </MovieNightContext.Provider>
  );
};

// Custom hook for accessing the context
export const useMovieNightContext = () => useContext(MovieNightContext);