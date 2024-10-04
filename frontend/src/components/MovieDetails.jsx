import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import UserDropdown from '../components/UserDropDown'; // Import UserDropdown
import CreateMovieNightBtn from './CreateMovieNightBtn';

function MovieDetails() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          console.error('No access token found');
          return;
        }

        const response = await axios.get(`http://0.0.0.0:8000/api/v1/movies/${id}/`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        setMovie(response.data);
      } catch (error) {
        console.error('Error fetching movie details:', error);
      }
    };

    fetchDetails();
  }, [id]);

  if (!movie) return <p className="text-center">Loading...</p>;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      {/* UserDropdown at the top-right corner */}
      <div className="absolute top-4 right-4">
        <UserDropdown />
      </div>

      <div className="max-w-6xl w-full p-4 bg-gray-900 bg-opacity-90 text-white rounded-lg shadow-lg">
        <div className="flex flex-col lg:flex-row items-center lg:items-start">
          {/* Movie Poster */}
          {movie.url_poster !== 'N/A' && (
            <img
              src={movie.url_poster}
              alt={movie.title}
              className="lg:w-1/3 w-full h-auto object-cover rounded-lg shadow-lg"
            />
          )}

          {/* Movie Info */}
          <div className="lg:ml-10 flex flex-col justify-between lg:w-2/3 w-full mt-6 lg:mt-0">
            <div>
              {/* Title */}
              {movie.title && <h1 className="text-4xl font-bold mb-4 text-center lg:text-left">{movie.title}</h1>}

              {/* IMDb Rating */}
              {movie.imdb_rating > 0 && (
                <p className="mb-4 flex items-center text-yellow-400">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 .587l3.668 7.571L24 9.743l-6 5.847 1.414 8.243L12 18.902l-7.414 4.93L6 15.59 0 9.743l8.332-1.585L12 .587z" />
                  </svg>
                  {movie.imdb_rating}/10
                </p>
              )}

              {/* Plot */}
              {movie.plot && movie.plot !== 'N/A' && (
                <p className="mb-6 text-lg leading-relaxed text-center lg:text-left">{movie.plot}</p>
              )}

              {/* Genres */}
              {movie.genres && movie.genres.length > 0 && (
                <div className="mb-4 text-center lg:text-left">
                  <strong>Genres:</strong>
                  <div className="flex flex-wrap gap-2 mt-2 justify-center lg:justify-start">
                    {movie.genres.map((genre, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 border border-gray-300 rounded-full text-sm font-medium text-gray-300"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Year and Runtime */}
              <div className="mb-4 flex flex-col space-y-2 text-center lg:text-left">
                {movie.year && (
                  <div>
                    <strong>Year:</strong> {movie.year}
                  </div>
                )}
                {movie.runtime_minutes && movie.runtime_minutes !== 'N/A' && (
                  <div>
                    <strong>Runtime:</strong> {movie.runtime_minutes} minutes
                  </div>
                )}
              </div>

              {/* Country */}
              {movie.country && movie.country !== 'N/A' && (
                <p className="mb-4 text-center lg:text-left">
                  <strong>Country:</strong> {movie.country}
                </p>
              )}
            </div>

            {/* Create Movie Night Button */}
            <div className="mt-6 text-center lg:text-left">
              <CreateMovieNightBtn movieId={id} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MovieDetails;