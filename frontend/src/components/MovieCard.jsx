import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import placeholderImage from '../assets/Image_not_available.png';  
import { AuthContext } from '../context/AuthContext'; // Import AuthContext to access authentication state

function MovieCard({ movie }) {
  const { isAuthenticated } = useContext(AuthContext); // Get isAuthenticated from context
  const navigate = useNavigate(); // Get navigate to programmatically redirect

  // Function to handle click on the movie card
  const handleCardClick = (e) => {
    // If the user is not authenticated, redirect them to the login page
    if (!isAuthenticated) {
      e.preventDefault(); // Prevent default navigation
      navigate('/login'); // Redirect to login
    }
  };

  return (
    <div className="bg-gray-900 text-white rounded-lg shadow-lg overflow-hidden hover:scale-105 transform transition-all duration-300">
      {/* Add onClick handler to the Link */}
      <Link to={`/movies/${movie.id}`} className="block" onClick={handleCardClick}>
        <img
          src={movie.url_poster !== 'N/A' ? movie.url_poster : placeholderImage}
          alt={movie.title}
          className="w-full h-96 object-cover rounded-t-lg"
        />
        <div className="p-4">
          <h3 className="text-lg font-semibold">{movie.title}</h3>
          <p className="text-sm text-gray-400">Movie • {movie.year}</p>
        </div>
      </Link>
    </div>
  );
}

export default MovieCard;