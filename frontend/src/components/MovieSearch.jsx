import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MovieCard from './MovieCard';  // Assuming you already have this component
import Filters from './MovieFilters';  // Assuming you already have the Filters component
import { useLocation } from 'react-router-dom'; // To read query parameters
import UserDropdown from './UserDropDown'; // Import the UserDropdown component

function MovieSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nextPage, setNextPage] = useState(null);  // To handle next page in pagination
  const [prevPage, setPrevPage] = useState(null);  // To handle previous page in pagination
  const [isFilterOpen, setIsFilterOpen] = useState(false); // Filter dropdown visibility

  // Get the search term from the URL query parameters
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const searchTermFromURL = queryParams.get('term');

  // Load search results from URL or sessionStorage on initial load
  useEffect(() => {
    const cachedResults = sessionStorage.getItem('results');
    const cachedNextPage = sessionStorage.getItem('nextPage');
    const cachedPrevPage = sessionStorage.getItem('prevPage');

    // Use the search term from the URL if available
    if (searchTermFromURL) {
      setSearchTerm(searchTermFromURL); // Set search term from the URL
      performSearch(searchTermFromURL); // Perform the search using URL term
    } else if (cachedResults) {
      // Load cached results if no search term is in the URL
      setResults(JSON.parse(cachedResults));
      setNextPage(cachedNextPage);
      setPrevPage(cachedPrevPage);
    }
  }, [searchTermFromURL]);

  // Perform search request (use this for both new search and pagination)
  const performSearch = async (term) => {
    setLoading(true);
    setError(null);

    try {
      // Perform the search request
      const response = await axios.post('http://0.0.0.0:8000/api/v1/movies/search/', {
        term: term,
      });

      if (response.status === 302) {
        window.location.href = response.headers.location;  // Handle redirection if needed
      } else {
        const data = response.data;
        setResults(data.results);
        setNextPage(data.next);  // Save next page URL
        setPrevPage(data.previous);  // Save previous page URL

        // Cache the search term, results, and pagination in sessionStorage
        sessionStorage.setItem('results', JSON.stringify(data.results));
        sessionStorage.setItem('nextPage', data.next || '');
        sessionStorage.setItem('prevPage', data.previous || '');
      }
    } catch (error) {
      setError('An error occurred while fetching results');
    } finally {
      setLoading(false);
    }
  };

  // Handle pagination (fetch next or previous page)
  const fetchPage = async (url) => {
    if (!url) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(url);
      const data = response.data;

      setResults(data.results);
      setNextPage(data.next);  // Update next page URL
      setPrevPage(data.previous);  // Update previous page URL

      // Cache updated results and pagination in sessionStorage
      sessionStorage.setItem('results', JSON.stringify(data.results));
      sessionStorage.setItem('nextPage', data.next || '');
      sessionStorage.setItem('prevPage', data.previous || '');
    } catch (error) {
      setError('An error occurred while fetching paginated results');
    } finally {
      setLoading(false);
    }
  };

  // Handle search form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTerm) {
      performSearch(searchTerm);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white relative">
      {/* Sticky Header (Search Bar, Filter Button, and User Dropdown) */}
      <div className="sticky top-0 z-10 bg-gray-900 shadow-lg p-4 flex justify-between items-center">
        <div className="flex space-x-4">
          <h1 className="text-2xl font-bold">Movie Night</h1>
          {/* Search Bar */}
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search movies"
              className="p-2 bg-gray-700 text-white rounded-l-md w-64"
              required
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded-r-md"
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
        </div>

        {/* User Dropdown */}
        <UserDropdown />
      </div>

      {/* Filter Button
      <button
        className="text-white p-2 rounded-full bg-gray-700 hover:bg-gray-600"
        onClick={() => setIsFilterOpen(!isFilterOpen)}
      >
        <span className="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 012 0v2a1 1 0 01-2 0V4zm3 0a1 1 0 011 1v1a1 1 0 01-1 1H4V4h2zm1 3h12v2H7V7zm5 4v8a1 1 0 001 1h1a1 1 0 001-1v-8a1 1 0 00-1-1h-1a1 1 0 00-1 1zM6 12h1a1 1 0 011 1v8a1 1 0 01-1 1H7a1 1 0 01-1-1v-8a1 1 0 011-1zM12 12h1a1 1 0 011 1v8a1 1 0 01-1 1h-1a1 1 0 01-1-1v-8a1 1 0 011-1z" />
          </svg>
        </span>
      </button>
    
      Filter Dropdown
      {isFilterOpen && (
        <div className="fixed top-16 right-4 z-20 bg-gray-800 w-64 p-4 rounded-md shadow-lg">
          <Filters filters={filters} setFilters={setFilters} ordering={ordering} setOrdering={setOrdering} />
        </div>
      )} */}

      {/* Search Results */}
      <div className="container mx-auto px-4 py-10">
        <h2 className="text-3xl font-bold mb-5">Search Results</h2>

        {loading && <p className="text-center">Loading...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {results.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            {results.map((movie) => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        <div className="pagination-controls mt-5 flex justify-center space-x-4">
          {prevPage && (
            <button
              className="bg-gray-500 text-white px-4 py-2 rounded"
              onClick={() => fetchPage(prevPage)}
            >
              Previous
            </button>
          )}
          {nextPage && (
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded"
              onClick={() => fetchPage(nextPage)}
            >
              Next
            </button>
          )}
        </div>

        {/* No Results */}
        {results.length === 0 && !loading && (
          <p className="text-center">No results found.</p>
        )}
      </div>
    </div>
  );
}

export default MovieSearch;