import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { format } from 'date-fns';
import Clock from './Clock';
import UserDropdown from '../components/UserDropDown';
import { useMovieNightContext } from '../context/MovieNightContext';

function MovieNightDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [movieNight, setMovieNight] = useState(null);
  const [movieDetails, setMovieDetails] = useState(null);
  const [userEmail, setUserEmail] = useState(null); // Store the fetched user email
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(null);
  const [fetchMovieError, setFetchMovieError] = useState(null);
  const [updateTimeError, setUpdateTimeError] = useState(null);
  const [inviteError, setInviteError] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const [newStartTime, setNewStartTime] = useState('');
  const [inviteeEmail, setInviteeEmail] = useState('');
  const accessToken = localStorage.getItem('access_token');
  const [isUpdatingTime, setIsUpdatingTime] = useState(false);
  const [isInviting, setIsInviting] = useState(false);
  const [isResponding, setIsResponding] = useState(false); // State for responding to invite
  const [showParticipants, setShowParticipants] = useState(false);
  const [showPendingInvitees, setShowPendingInvitees] = useState(false);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const { invitationData } = useMovieNightContext(); // Access the data from context
  const { attendanceConfirmed, isAttending, movienight_invitation_id } = invitationData || {}; // Destructure with fallback

  // Fetch current user's email once when the component mounts
  const fetchUserEmail = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/auth/users/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUserEmail(response.data.results[0].email);
    } catch (error) {
      console.error('Failed to fetch user email:', error);
    }
  };

  useEffect(() => {
    fetchUserEmail(); // Fetch user email on mount
  }, []); // Empty dependency array ensures this runs once

  const pendingInvite = (attendanceConfirmed !== undefined && isAttending !== undefined) 
    ? (!attendanceConfirmed && !isAttending) 
    : false;

  // Fetch movie night details
  useEffect(() => {
    const fetchMovieNightDetails = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/movie-nights/${id}/`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        setMovieNight(response.data);
        setNewStartTime(response.data.start_time);
      } catch (error) {
        setFetchError('Failed to fetch movie night details');
      } finally {
        setLoading(false);
      }
    };

    fetchMovieNightDetails();
  }, [id, accessToken]);

  // Fetch movie details based on movie
  useEffect(() => {
    if (movieNight?.movie) {
      const fetchMovieDetails = async () => {
        try {
          const response = await axios.get(`http://localhost:8000/api/v1/movies/${movieNight.movie}/`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });
          setMovieDetails(response.data);
        } catch (error) {
          console.error(error);
          setFetchMovieError('Failed to fetch movie details');
        }
      };

      fetchMovieDetails();
    }
  }, [movieNight?.movie]);

  // Handle Start Time Update
  const handleStartTimeUpdate = async () => {
    setUpdateTimeError(null);
    try {
      const response = await axios.patch(
        `http://localhost:8000/api/v1/movie-nights/${id}/`,
        { start_time: newStartTime },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      setMovieNight((prev) => ({ ...prev, start_time: response.data.start_time }));
      setIsUpdatingTime(false);
    } catch (error) {
      const errorMessage =
        error.response?.data?.start_time?.[0] || error.response?.data?.detail || 'Failed to update start time';
      setUpdateTimeError(errorMessage);
    }
  };

  // Handle movie night deletion
  const handleDelete = async () => {
    setDeleteError(null);
    try {
      await axios.delete(`http://localhost:8000/api/v1/movie-nights/${id}/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      navigate(`/movies/${movieNight.movie}/`); // Redirect to the movie detail page
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete movie night';
      setDeleteError(errorMessage);
    }
  };

  // Handle inviting a new participant
  const handleInvite = async () => {
    setInviteError(null);
    try {
      await axios.post(
        `http://localhost:8000/api/v1/movie-nights/${id}/invite/`,
        { invitee: inviteeEmail, movie_night: id },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      setMovieNight((prev) => ({
        ...prev,
        pending_invitees: [...(prev.pending_invitees || []), inviteeEmail],
      }));
      setInviteeEmail('');
      setIsInviting(false);
    } catch (error) {
      const errorMessage = error.response?.data?.non_field_errors?.[0] || 'Failed to send the invitation';
      setInviteError(errorMessage);
    }
  };

// Handle the user's response to the invitation
const handleInvitationResponse = async (isAttending) => {
  try {
    // Send PATCH request to update invitation status
    await axios.patch(
      `http://localhost:8000/api/v1/movienight-invitations/${movienight_invitation_id}/`,
      {
        is_attending: isAttending, // Accept or decline
        attendance_confirmed: true // Confirm attendance
      },
      {
        headers: { Authorization: `Bearer ${accessToken}` } // Use accessToken for auth
      }
    );

    // Update local state to reflect the user's response
    setMovieNight((prevMovieNight) => {
      let updatedParticipants = [...prevMovieNight.participants];
      let updatedPendingInvitees = [...prevMovieNight.pending_invitees];

      // If user accepted, add them to participants and remove from pending invitees
      if (isAttending) {
        if (!updatedParticipants.includes(userEmail)) {
          updatedParticipants.push(userEmail);
        }
        updatedPendingInvitees = updatedPendingInvitees.filter(
          (invitee) => invitee !== userEmail
        );
      } else {
        // If user declined, ensure they're not in the participants list
        updatedParticipants = updatedParticipants.filter(
          (participant) => participant !== userEmail
        );
      }

      // Return the updated state
      return {
        ...prevMovieNight,
        participants: updatedParticipants,
        pending_invitees: updatedPendingInvitees
      };
    });

    // Set isResponding to true to hide the banner
    setIsResponding(true);
  } catch (error) {
    console.error("Failed to respond to the invitation:", error);
    setInviteError('Failed to respond to the invitation');
  }
};

  if (loading) return <p>Loading...</p>;
  if (!movieNight) return null;

  // Check if the user has a pending invitation

  // Format start time to separate date and time
  const formattedDate = format(new Date(movieNight.start_time), 'EEEE, d MMMM yyyy');
  const formattedTime = format(new Date(movieNight.start_time), 'HH:mm');

  // Display fetch errors
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white text-xl p-10 leading-loose">
      <div className="absolute top-4 right-4">
        <UserDropdown />
      </div>
    {/* Display invitation banner if the user hasn't responded yet */}
    {pendingInvite && !isResponding && (
      <div className="bg-gray-100 text-gray-700 border border-gray-300 px-6 py-4 rounded-lg w-full max-w-4xl text-left mb-6 shadow-md">
        <p>You have been invited to this movie night. Would you like to attend?</p>
        <div className="flex justify-center space-x-4 mt-2">
          <button
            onClick={() => handleInvitationResponse(true)}
            className="bg-green-500 px-4 py-2 rounded-lg shadow-md"
          >
            Accept
          </button>
          <button
            onClick={() => handleInvitationResponse(false)}
            className="bg-red-500 px-4 py-2 rounded-lg shadow-md"
          >
            Decline
          </button>
        </div>
        {inviteError && <p className="text-red-500 mt-2">{inviteError}</p>}
      </div>
    )}

      {fetchError && <p className="text-red-500 text-center mb-4">{fetchError}</p>}
      {fetchMovieError && <p className="text-red-500 text-center mb-4">{fetchMovieError}</p>}
      <Clock startTime={movieNight.start_time} />

      <div className="mt-10 w-full max-w-4xl">
        {movieDetails && movieDetails.title && (
          <h1 className="text-3xl font-bold mb-6 text-center">
            Movie Night: {movieDetails.title}
          </h1>
        )}
        <div className="flex flex-col md:flex-row md:space-x-10">
          {/* Left Section - Movie Poster */}
          <div className="md:w-1/2 flex justify-center">
            {/* Display movie poster */}
            {movieDetails && movieDetails.url_poster ? (
              <img
                src={movieDetails.url_poster}
                alt={movieDetails.title}
                className="w-full h-auto rounded-lg shadow-md"
              />
            ) : (
              <div className="w-full h-64 bg-gray-800 rounded-lg shadow-md flex items-center justify-center">
                No poster available
              </div>
            )}
          </div>

          {/* Right Section - Movie Night Details */}
          <div className="md:w-1/2 mt-6 md:mt-0">
            <div>
              <h2 className="text-3xl font-bold ">{formattedDate}</h2>
              <h2 className="text-3xl font-bold mt-5">{formattedTime}</h2>
            </div>
            <p className="mt-4">
              <strong>Creator:</strong>{' '}
              <span className="font-semibold">{movieNight.creator}</span>
            </p>

            {/* Participants and Pending Invitees */}
            <div className="mt-6">
              {/* Participants Dropdown */}
              <div className="mb-4">
                <button
                  onClick={() => setShowParticipants(!showParticipants)}
                  className="flex items-center justify-between w-full bg-gray-700 px-4 py-2 rounded-lg"
                >
                  <span className="font-semibold">Participants</span>
                  <svg
                    className={`w-5 h-5 transition-transform ${
                      showParticipants ? 'transform rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {showParticipants && (
                  <div className="mt-2 bg-gray-800 p-4 rounded-lg">
                    {movieNight.participants.length > 0 ? (
                      <ul>
                        {movieNight.participants.map((participant) => (
                          <li key={participant}>{participant}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>No participants</p>
                    )}
                  </div>
                )}
              </div>

              {/* Pending Invitees Dropdown */}
              {movieNight.is_creator && (
                <div>
                  <button
                    onClick={() => setShowPendingInvitees(!showPendingInvitees)}
                    className="flex items-center justify-between w-full bg-gray-700 px-4 py-2 rounded-lg"
                  >
                    <span className="font-semibold">Pending Invitees</span>
                    <svg
                      className={`w-5 h-5 transition-transform ${
                        showPendingInvitees ? 'transform rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </button>
                  {showPendingInvitees && (
                    <div className="mt-2 bg-gray-800 p-4 rounded-lg">
                      {movieNight.pending_invitees.length > 0 ? (
                        <ul>
                          {movieNight.pending_invitees.map((invitee) => (
                            <li key={invitee}>{invitee}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No pending invitees</p>
                      )}
                    </div>
                  )}
                </div>)
              }
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {movieNight.is_creator && (
        <div className="flex space-x-4 mt-10">
          {/* Update Start Time */}
          <button
            onClick={() => setIsUpdatingTime(true)}
            className="bg-blue-500 px-4 py-2 rounded-lg shadow-md"
          >
            Update Start Time
          </button>

          {/* Invite Friends */}
          <button
            onClick={() => setIsInviting(true)}
            className="bg-green-500 px-4 py-2 rounded-lg shadow-md"
          >
            Invite Friends
          </button>

          {/* Delete Movie Night */}
          <button
            onClick={() => setIsConfirmingDelete(true)} // Open confirmation modal
            className="bg-red-500 px-4 py-2 rounded-lg shadow-md"
          >
            Delete Movie Night
          </button>
        </div>
      )}

      {/* Modal for Updating Start Time */}
      {isUpdatingTime && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg">
            <h2 className="text-lg text-gray-700 font-semibold">Update Start Time</h2>
            
            {/* Display the error message */}
            {updateTimeError && <p className="text-red-500 mb-2">{updateTimeError}</p>}
            
            <input
              type="datetime-local"
              value={newStartTime}
              onChange={(e) => setNewStartTime(e.target.value)}
              className="border p-2 rounded text-gray-500 w-full mb-4"
            />
            <div className="flex justify-end">
              <button
                onClick={() => {
                  setIsUpdatingTime(false);
                  setUpdateTimeError(null); // Clear error when closing modal
                }}
                className="bg-gray-500 px-4 py-2 text-white rounded-lg mr-2"
              >
                Cancel
              </button>
              <button
                onClick={handleStartTimeUpdate}
                className="bg-blue-500 px-4 py-2 text-white rounded-lg"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Inviting Friends */}
      {isInviting && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg">
            <h2 className="text-lg text-gray-700 font-semibold">Invite a Friend</h2>
            
            {/* Display the error message */}
            {inviteError && <p className="text-red-500 mb-2">{inviteError}</p>}
            
            <input
              type="email"
              value={inviteeEmail}
              onChange={(e) => setInviteeEmail(e.target.value)}
              placeholder="Enter email"
              className="border p-2 rounded text-black w-full mb-4"
            />
            <div className="flex justify-end">
              <button
                onClick={() => {
                  setIsInviting(false);
                  setInviteError(null); // Clear error when closing modal
                }}
                className="bg-gray-500 px-4 py-2 text-white rounded-lg mr-2"
              >
                Cancel
              </button>
              <button
                onClick={handleInvite}
                className="bg-green-500 px-4 py-2 text-white rounded-lg"
              >
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Confirming Deletion */}
      {isConfirmingDelete && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg">
            <h2 className="text-lg text-gray-700 font-semibold">Confirm Deletion</h2>
            
            {/* Display the error message */}
            {deleteError && <p className="text-red-500 mb-2">{deleteError}</p>}
            
            <p className="text-gray-700 mt-2">Are you sure you want to delete this movie night?</p>
            <div className="flex justify-end mt-4">
              <button
                onClick={() => {
                  setIsConfirmingDelete(false);
                  setDeleteError(null); // Clear error when closing modal
                }}
                className="bg-gray-500 px-4 py-2 text-white rounded-lg mr-2"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="bg-red-500 px-4 py-2 text-white rounded-lg"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


export default MovieNightDetails;

