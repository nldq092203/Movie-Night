import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MovieCard from './MovieCard'; // Component to display individual movies
import FilterDropdown from './FilterDropDown'; // Filter Dropdown Component
import UserDropdown from './UserDropDown'; // User Dropdown Component
import SearchBar from './SearchBar';

function HomePage() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Pagination states
  const [nextPageUrl, setNextPageUrl] = useState('http://0.0.0.0:8000/api/v1/movies/'); // Start at the first page
  const [hasMore, setHasMore] = useState(true); // Whether there are more pages
  const [showHeader, setShowHeader] = useState(true); // For the header visibility

  // Filters and sorting state
  const [filters, setFilters] = useState({
    genres: [],
    country: '',
    year: '',
    runtime: '',
  });
  const [ordering, setOrdering] = useState('');

  // Fetch movies from the API
  const fetchMovies = async (url) => {
    if (!url || loading) return; // Prevent multiple simultaneous requests
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(url, {
        params: {
          genres: filters.genres.length > 0 ? filters.genres.join(',') : undefined,
          country: filters.country ? filters.country : undefined,
          year: filters.year ? filters.year : undefined,
          runtime_minutes: filters.runtime ? filters.runtime : undefined,
          ordering: ordering ? ordering : undefined,
        },
      });

      // Append new movies to the existing list
      setMovies((prevMovies) => [...prevMovies, ...response.data.results]);

      // Check if there's more data to fetch
      if (response.data.next) {
        setNextPageUrl(response.data.next);
        setHasMore(true);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      setError('Failed to fetch movies.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch movies on initial load and when filters or ordering change
  useEffect(() => {
    // Reset movie list and page when filters or ordering change
    setMovies([]);
    setNextPageUrl('http://0.0.0.0:8000/api/v1/movies/');
    setHasMore(true);
    fetchMovies('http://0.0.0.0:8000/api/v1/movies/');
  }, [filters, ordering]);

  // Function to get the greeting based on the current time
  const getGreeting = () => {
    const currentHour = new Date().getHours();
    if (currentHour < 12) {
      return "this morning";
    } else if (currentHour < 18) {
      return "this afternoon";
    } else {
      return "tonight";
    }
  };

  // Infinite scroll handler
  const handleScroll = () => {
    if (window.innerHeight + document.documentElement.scrollTop >= document.documentElement.offsetHeight - 100) {
      if (!loading && hasMore) {
        fetchMovies(nextPageUrl);
      }
    }

    // Handle header visibility
    if (document.documentElement.scrollTop > 150) {
      setShowHeader(false);
    } else {
      setShowHeader(true);
    }
  };

  // Attach scroll event listener
  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll); // Cleanup on unmount
  }, [nextPageUrl, hasMore, loading]);

  // Handle search submission
  const handleSearch = (searchTerm) => {
    // Redirect to /search with the search term
    window.location.href = `/search?term=${encodeURIComponent(searchTerm)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white relative">
      {/* Filter Dropdown always at top-left */}
      <FilterDropdown
        filters={filters}
        setFilters={setFilters}
        ordering={ordering}
        setOrdering={setOrdering}
        isFilterOpen={isFilterOpen}
        setIsFilterOpen={setIsFilterOpen}
      />

      {/* User Dropdown at top-right */}
      <UserDropdown />

      {/* Search Bar (fixed at the top-center of the screen with matching background) */}
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-gradient-to-b from-gray-900 to-gray-800 p-4 rounded-lg shadow-lg">
        <SearchBar onSearch={handleSearch} />
      </div>

      {/* Search Bar and Header Section */}
      <div className="flex flex-col items-center justify-center h-96">
        {showHeader && <h1 className="text-4xl font-bold mb-8">What would you like to watch {getGreeting()}?</h1>}
      </div>

      {/* Movie List Section */}
      <div className="container mx-auto px-10 py-10 ">
        <h2 className="text-xl font-semibold mb-4">Movies</h2>
        {loading && !movies.length ? (
          <p className="text-center">Loading...</p>
        ) : error ? (
          <p className="text-center text-red-500">{error}</p>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
            {loading && hasMore && <p className="text-center mt-4">Loading more...</p>}
          </>
        )}
      </div>
    </div>
  );
}

export default HomePage;