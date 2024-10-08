import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';  // Import useNavigate
import UserDropdown from '../components/UserDropDown'; // Import UserDropdown

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    re_password: ''
  });

  const [passwordError, setPasswordError] = useState(null);
  const [emailError, setEmailError] = useState(null);
  const [serverErrors, setServerErrors] = useState([]); // For server-side errors
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();  // Initialize useNavigate hook

  // Handle input changes and validation
  const handleChange = (e) => {
    const { name, value } = e.target;
    const updatedFormData = { ...formData, [name]: value };
    setFormData(updatedFormData);

    // Validate passwords with updated values
    if (name === 'password' || name === 're_password') {
      validatePassword(updatedFormData.password, updatedFormData.re_password);
    }

    // Validate email
    if (name === 'email') {
      validateEmail(value);
    }
  };

  // Email validation function
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    setEmailError(emailRegex.test(email) ? null : 'Please enter a valid email');
  };

  // Password validation function
  const validatePassword = (password, re_password) => {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$/;
    if (!passwordRegex.test(password)) {
      setPasswordError(
        'Password must be at least 8 characters, include uppercase, lowercase, number, and special character'
      );
    } else if (password !== re_password) {
      setPasswordError("Passwords don't match");
    } else {
      setPasswordError(null);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (passwordError || emailError) {
      alert('Please fix the errors in the form');
      return;
    }

    try {
      // Clear previous server errors
      setServerErrors([]);

      // Send the registration request to the server
      const response = await axios.post(
        'http://0.0.0.0:8000/auth/users/',
        formData,
        {
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      console.log('Success:', response.data);

      // If registration is successful, redirect to the login page
      navigate('/login');  // Programmatically navigate to login

    } catch (error) {
      if (error.response && error.response.data) {
        // Capture all server-side errors and store them in the state
        setServerErrors(Object.values(error.response.data));
      } else {
        console.error('Error:', error);
      }
    }
  };

  // Toggle password visibility
  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 relative">
      {/* UserDropdown at the top-right corner */}
      <div className="absolute top-4 right-4">
        <UserDropdown />
      </div>
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-lg shadow-md max-w-md w-full"
      >
        <h2 className="text-2xl font-semibold text-center mb-6 text-black">Register</h2>

        {/* Display server-side errors */}
        {serverErrors.length > 0 && (
          <ul className="bg-red-100 text-red-500 p-4 mb-4">
            {serverErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        )}

        <div className="mb-4">
          <label htmlFor="email" className="block text-gray-700">
            Email
          </label>
          <input
            name="email"
            type="email"
            id="email"
            value={formData.email}
            onChange={handleChange}
            className={`border text-gray-700 p-2 w-full ${emailError ? 'border-red-500' : ''}`}
            required
          />
          {emailError && (
            <p className="text-red-500 text-sm">{emailError}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="password" className="block text-gray-700">
            Password
          </label>
          <input
            name="password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={formData.password}
            onChange={handleChange}
            className={`border text-gray-700 p-2 w-full ${
              passwordError ? 'border-red-500' : ''
            }`}
            required
          />
          {passwordError && (
            <p className="text-red-500 text-sm">{passwordError}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="re_password" className="block text-gray-700">
            Confirm Password
          </label>
          <input
            name="re_password"
            type={showPassword ? 'text' : 'password'}
            id="re_password"
            value={formData.re_password}
            onChange={handleChange}
            className={`border text-gray-700 p-2 w-full ${
              passwordError ? 'border-red-500' : ''
            }`}
            required
          />
        </div>

        {/* Show Password Checkbox */}
        <div className="mb-4">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={showPassword}
              onChange={toggleShowPassword}
              className="form-checkbox"
            />
            <span className="ml-2 text-gray-700">Show Password</span>
          </label>
        </div>

        <button
          type="submit"
          className={`w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition-colors ${
            passwordError || emailError ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          disabled={passwordError || emailError}
        >
          Register
        </button>
      </form>
    </div>
  );
}

export default Register;