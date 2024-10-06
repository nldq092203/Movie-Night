import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function CreateMovieNightBtn({ movieId }) {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [startTime, setStartTime] = useState('');
  const [notificationTime, setNotificationTime] = useState('PT5M');  // Default to 5 minutes
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [movieNights, setMovieNights] = useState([]);

  const dropdownRef = useRef(null);

  // Function to convert ISO 8601 duration to seconds
  const convertDurationToSeconds = (duration) => {
    if (duration.includes('H')) {
      const hours = parseInt(duration.replace('PT', '').replace('H', ''), 10);
      return hours * 3600;  // Convert hours to seconds
    }
    if (duration.includes('M')) {
      const minutes = parseInt(duration.replace('PT', '').replace('M', ''), 10);
      return minutes * 60;  // Convert minutes to seconds
    }
    return 0;  // Default case, if no match
  };

  const handleOpenForm = () => {
    setIsFormOpen((prev) => !prev);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setError(null);
    setSuccess(false);
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const accessToken = localStorage.getItem('access_token');
      const notificationInSeconds = convertDurationToSeconds(notificationTime);  // Convert to seconds
      const response = await axios.post(
        'http://0.0.0.0:8000/api/v1/my-movie-nights/',
        {
          movie: movieId,
          start_time: startTime,
          start_notification_before: notificationInSeconds,  // Send seconds to the API
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.status === 201) {
        setSuccess('Movie night created successfully!');
        fetchMovieNights();  // Fetch updated movie nights
        setIsFormOpen(false);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.start_time?.[0] || 'An unexpected error occurred.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const fetchMovieNights = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const now = new Date().toISOString();
      const response = await axios.get(
        'http://0.0.0.0:8000/api/v1/my-movie-nights/',
        {
          params: { 
            ordering: 'movieId',
            start_from: now,
          },
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );
      setMovieNights(response.data.results);
    } catch (err) {
      console.error('Error creating movie night:', err.response?.data?.detail);
      setError('Failed to fetch movie nights. Please try again later.');
    }
  };

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
    if (!isDropdownOpen) fetchMovieNights();  // Fetch movie nights when opening dropdown
  };

  return (
    <div className="relative create-movie-night">
      <div className="flex items-center">
        <button
          onClick={handleOpenForm}
          className="bg-yellow-500 text-black px-4 py-2 rounded-l-lg flex items-center justify-between w-50 hover:bg-yellow-600"
        >
          <span className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Movie Night
          </span>
        </button>

        <button
          onClick={toggleDropdown}
          className="bg-yellow-500 text-black px-2 py-2.5 rounded-r-lg hover:bg-yellow-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {isDropdownOpen && (
        <div ref={dropdownRef} className="absolute left-0 mt-2 bg-white text-black shadow-lg rounded-lg p-4 w-72 z-20">
          <h3 className="font-semibold mb-2">Your Movie Nights:</h3>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          {movieNights.length > 0 ? (
            <ul className="space-y-2">
              {movieNights.map((night) => (
                <li key={night.id} className="flex justify-between items-center">
                  <span>{new Date(night.start_time).toLocaleString()}</span>
                  <a
                    href={`/movie-nights/${night.id}`}
                    className="text-blue-500 underline hover:text-blue-700"
                  >
                    View
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p>No movie nights found for this movie.</p>
          )}
        </div>
      )}

      {isFormOpen && (
        <div className="form-modal fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-30">
          <div className="bg-white rounded-lg p-8 relative max-w-md w-full">
            <h2 className="text-xl text-gray-700 font-semibold mb-4">Create Movie Night</h2>

            {error && <p className="text-red-500 mb-4">{error}</p>}
            {success && <p className="text-green-500 mb-4">{success}</p>}

            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div>
                <label htmlFor="startTime" className="block text-gray-700 font-semibold mb-2">
                  Start Time:
                </label>
                <input
                  type="datetime-local"
                  id="startTime"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full text-gray-500 p-2 border rounded"
                  required
                />
              </div>

              <div>
                <label htmlFor="notificationTime" className="block text-gray-700 font-semibold mb-2">
                  Notify me before:
                </label>
                <select
                  id="notificationTime"
                  value={notificationTime}
                  onChange={(e) => setNotificationTime(e.target.value)}
                  className="w-full text-gray-500 p-2 border rounded"
                >
                  <option value="PT5M">5 minutes before</option>
                  <option value="PT15M">15 minutes before</option>
                  <option value="PT30M">30 minutes before</option>
                  <option value="PT1H">1 hour before</option>
                  <option value="PT2H">2 hours before</option>
                  <option value="PT3H">3 hours before</option>
                  <option value="PT6H">6 hours before</option>
                  <option value="PT12H">12 hours before</option>
                  <option value="PT24H">24 hours before</option>
                </select>
              </div>

              <div className="flex justify-between">
                <button
                  type="submit"
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                  onClick={handleCloseForm}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CreateMovieNightBtn;