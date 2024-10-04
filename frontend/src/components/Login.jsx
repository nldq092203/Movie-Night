import { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import UserDropdown from '../components/UserDropDown'; // Import UserDropdown

function Login() {
  const { loginUser, googleLogin } = useContext(AuthContext); // Include googleLogin
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [error, setError] = useState(null); // State to store error messages
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility
  const navigate = useNavigate(); // useNavigate for redirecting

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError(null); // Clear any previous errors

      // Attempt login
      const response = await loginUser(credentials);

      // If login is successful, redirect to the home page
      if (response?.access) {
        navigate('/'); // Redirect to home page after login
      }
    } catch (error) {
      if (error.response && error.response.data) {
        // Capture all server-side errors and store them in the state
        setError(Object.values(error.response.data).flat().join(', '));
      } else {
        console.error('Error:', error);
      }
    }
  };

  // Handle Google login success
  const handleGoogleSuccess = async (response) => {
    try {
      setError(null); // Clear previous errors

      // Send the Google ID token to the backend
      const res = await axios.post('http://0.0.0.0:8000/auth/google/', {
        id_token: response.credential,
      });

      // If login is successful, update AuthContext and redirect
      if (res.data?.access) {
        googleLogin(res.data); // Update the AuthContext
        navigate('/'); // Redirect to the home page
      }
    } catch (error) {
      setError('Google authentication failed');
      console.error('Google Auth Error:', error);
    }
  };

  // Handle Google login failure
  const handleGoogleFailure = (error) => {
    setError('Google authentication failed');
    console.error('Google Sign-In error:', error);
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
        <h2 className="text-2xl font-semibold text-center mb-6 text-gray-700">Login</h2>

        {/* Show error message */}
        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        <div className="mb-4">
          <label htmlFor="email" className="block text-gray-700">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={credentials.email}
            onChange={(e) =>
              setCredentials({ ...credentials, email: e.target.value })
            }
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 text-gray-700"
            required
          />
        </div>

        <div className="mb-6">
          <label htmlFor="password" className="block text-gray-700">
            Password
          </label>
          <input
            type={showPassword ? 'text' : 'password'} // Toggle between 'text' and 'password'
            id="password"
            name="password"
            value={credentials.password}
            onChange={(e) =>
              setCredentials({ ...credentials, password: e.target.value })
            }
            className="w-full px-4 py-2 text-gray-700 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
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
          className="w-full bg-indigo-500 text-white py-2 rounded-md hover:bg-indigo-600 transition-colors"
        >
          Login
        </button>

        <div className="text-center mt-6">
          <p>Or sign in with</p>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleFailure}
          />
        </div>
      </form>
    </div>
  );
}

export default Login;