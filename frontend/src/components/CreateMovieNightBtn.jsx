import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Button, Modal, TextInput, Select, ActionIcon, Tooltip, Divider } from '@mantine/core';
import { IconPlus, IconChevronDown, IconX } from '@tabler/icons-react';

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

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const accessToken = localStorage.getItem('access_token');
      const notificationInSeconds = convertDurationToSeconds(notificationTime);
      const response = await axios.post(
        'http://0.0.0.0:8000/api/v1/my-movie-nights/',
        {
          movie: movieId,
          start_time: startTime,
          start_notification_before: notificationInSeconds,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.status === 201) {
        setSuccess('Movie night created successfully!');
        fetchMovieNights();
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
    if (!isDropdownOpen) fetchMovieNights();
  };

  return (
    <div className="relative create-movie-night">
      <div className="flex items-center">
        <Button
          onClick={() => setIsFormOpen(true)}
          color="yellow"
          leftIcon={<IconPlus />}
          radius="md"
          style={{ borderRadius: '0.5rem 0 0 0.5rem' }}
          styles={{
            label: { color: 'black' }
          }}
        >
          Create Movie Night
        </Button>

        <Button
          onClick={toggleDropdown}
          color="yellow"
          radius="md"
          style={{ borderRadius: '0 0.5rem 0.5rem 0' }}
        >
          <IconChevronDown />
        </Button>
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
                  <a href={`/movie-nights/${night.id}`} className="text-blue-500 underline hover:text-blue-700">View</a>
                </li>
              ))}
            </ul>
          ) : (
            <p>No movie nights found for this movie.</p>
          )}
        </div>
      )}

      <Modal
        opened={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title="Create Movie Night"
        centered
      >
        {error && <p className="text-red-500 mb-4">{error}</p>}
        {success && <p className="text-green-500 mb-4">{success}</p>}

        <form onSubmit={handleFormSubmit}>
          <TextInput
            type="datetime-local"
            label="Start Time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
            fullWidth
          />
          
          <Select
            label="Notify me before"
            value={notificationTime}
            onChange={(value) => setNotificationTime(value)}
            data={[
              { value: 'PT5M', label: '5 minutes before' },
              { value: 'PT15M', label: '15 minutes before' },
              { value: 'PT30M', label: '30 minutes before' },
              { value: 'PT1H', label: '1 hour before' },
              { value: 'PT2H', label: '2 hours before' },
              { value: 'PT3H', label: '3 hours before' },
              { value: 'PT6H', label: '6 hours before' },
              { value: 'PT12H', label: '12 hours before' },
              { value: 'PT24H', label: '24 hours before' },
            ]}
            fullWidth
          />

          <Divider my="sm" />

          <div className="flex justify-end">
            <Button type="submit" color="green" loading={loading} mr="sm">
              Create
            </Button>
            <Button color="gray" onClick={() => setIsFormOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default CreateMovieNightBtn;