import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom'; // Use useNavigate instead of useHistory

function UserDropdown() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { isAuthenticated, logoutUser } = useContext(AuthContext);
  const navigate = useNavigate(); // Use navigate for redirection

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  // Handle logout and redirect to homepage
  const handleLogout = () => {
    logoutUser();           // Perform logout
    setIsDropdownOpen(false); // Close dropdown
    navigate('/');           // Redirect to homepage using navigate
  };

  return (
    <div className="fixed top-4 right-4 z-20">
      <button
        className="text-white p-2 rounded-full bg-gray-700 hover:bg-gray-600"
        onClick={toggleDropdown}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
      </button>
      {isDropdownOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg py-2">
          <a href="/" className="block px-4 py-2 text-white hover:bg-gray-700">Home</a>
          {isAuthenticated ? (
            <>
              <a href="/profile" className="block px-4 py-2 text-white hover:bg-gray-700">Profile</a>
              <button
                onClick={handleLogout}
                className="block w-full text-left px-4 py-2 text-white hover:bg-gray-700"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <a href="/login" className="block px-4 py-2 text-white hover:bg-gray-700">Login</a>
              <a href="/register" className="block px-4 py-2 text-white hover:bg-gray-700">Register</a>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default UserDropdown;