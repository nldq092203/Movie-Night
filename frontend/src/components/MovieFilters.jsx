import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';

function Filters({ filters, setFilters, ordering, setOrdering }) {
  const [genreOptions, setGenreOptions] = useState([]);
  const [visibleGenres, setVisibleGenres] = useState(6); // Number of visible genres initially
  const [isOpen, setIsOpen] = useState(false);
  const [imdbRating, setImdbRating] = useState([0, 10]); // IMDb Rating slider state
  const [isYearDropdownOpen, setIsYearDropdownOpen] = useState(false);

  // Fetch genres from the API to populate the genre filter options
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/genres/');
        setGenreOptions(response.data.results);
      } catch (err) {
        console.error('Failed to fetch genres.');
      }
    };
    fetchGenres();
  }, []);

  // Toggle selected genre in filters
  const handleGenreClick = (genre) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      genres: prevFilters.genres.includes(genre)
        ? prevFilters.genres.filter((g) => g !== genre)
        : [...prevFilters.genres, genre],
    }));
  };

  // Show more or less genres
  const toggleVisibleGenres = () => {
    setVisibleGenres((prev) => (prev === 6 ? genreOptions.length : 6));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => {
      const updatedFilters = { ...prevFilters, [name]: value };
      return updatedFilters;
    });
  };
  // Handle ordering changes
  const handleOrderingChange = (e) => {
    setOrdering(e.target.value);
  };

  // Debounced function to update filters only once when the user stops sliding
  const debouncedUpdateFilters = useCallback(
    debounce((newRating) => {
      setFilters((prevFilters) => ({
        ...prevFilters,
        imdb_rating_from: newRating,
      }));
    }, 300),
    [] // The empty dependency array ensures debounce is created only once
  );

  // Handle IMDb rating change and trigger debounced update
  const handleImdbRatingChange = (value) => {
    setImdbRating(value);
    debouncedUpdateFilters(value); // Update filters with debounce
  };

  return (
    <div className="space-y-4 p-6 bg-black text-white rounded-lg shadow-md max-w-lg mx-auto">
      <h3 className="text-xl font-semibold mb-4 text-center">Filters</h3>

      {/* Genres Section */}
      <div className="space-y-4">
        <h4 className="font-bold mb-2">Genres</h4>
        <div className="flex flex-wrap gap-2">
          {genreOptions.slice(0, visibleGenres).map((genre) => (
            <button
              key={genre.id}
              onClick={() => handleGenreClick(genre.name)}
              className={`flex items-center justify-center px-4 py-2 border rounded-full text-sm 
                ${filters.genres.includes(genre.name) ? 'bg-black text-white' : 'border-gray-300 text-white'}`}
            >
              {genre.name}
            </button>
          ))}
        </div>
        {genreOptions.length > 6 && (
          <button
            onClick={toggleVisibleGenres}
            className="mt-2 px-4 py-2 border rounded-full text-sm flex items-center justify-center"
          >
            {visibleGenres === 6 ? 'Show more' : 'Show less'}{' '}
            <span className="ml-2 transform transition-transform duration-200">
              {visibleGenres === 6 ? '▼' : '▲'}
            </span>
          </button>
        )}
      </div>

      {/* Runtime Dropdown */}
      <div className="relative space-y-2">
        <h3 className="font-bold mb-2">Runtime (minutes)</h3>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex justify-between items-center border rounded-md px-4 py-2 text-left text-white"
        >
          <span>Set Runtime</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 transition-transform ${isOpen ? 'rotate-180' : 'rotate-0'}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 9l6 6 6-6" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute w-full mt-2 p-4 rounded-md bg-black shadow-lg z-10">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-1">Minimum Runtime</label>
                <input
                  type="number"
                  name="runtime_minutes_from"
                  value={filters.runtime_minutes_from || ''}
                  onChange={handleInputChange}
                  className="w-full border p-2 rounded-md text-black"
                  placeholder="Min Runtime"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-1">Maximum Runtime</label>
                <input
                  type="number"
                  name="runtime_minutes_to"
                  value={filters.runtime_minutes_to || ''}
                  onChange={handleInputChange}
                  className="w-full border p-2 rounded-md text-black"
                  placeholder="Max Runtime"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* IMDb Rating Slider */}
      <div>
        <h4 className="font-bold mb-2">Minimum IMDb Rating</h4>
        <div className="flex items-center justify-between mb-4">
          <span>0</span>
          <span>10</span>
        </div>
        <input
          type="range"
          name="imdb_rating_from"
          min="0"
          max="10"
          step="0.1"
          value={imdbRating}
          onChange={(e) => handleImdbRatingChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-pink-500 rounded-lg appearance-none"
        />
        <div className="text-center mt-2 text-gray-500">
          Selected Rating: {imdbRating}
        </div>
      </div>
      {/* Year Range */}
      <div className="relative space-y-2">
      <h3 className="font-bold mb-2">Year Range</h3>
      <button
        onClick={() => setIsYearDropdownOpen(!isYearDropdownOpen)}
        className="w-full flex justify-between items-center border rounded-md px-4 py-2 text-left text-white"
      >
        <span>Set Year Range</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`h-5 w-5 transition-transform ${isYearDropdownOpen ? 'rotate-180' : 'rotate-0'}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {isYearDropdownOpen && (
        <div className="absolute w-full mt-2 p-4 rounded-md bg-black shadow-lg z-10">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-1">From</label>
              <input
                type="number"
                name="published_from"
                value={filters.published_from || ''}
                onChange={handleInputChange}
                className="w-full border p-2 rounded-md text-black"
                placeholder="Start Year"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">To</label>
              <input
                type="number"
                name="published_to"
                value={filters.published_to || ''}
                onChange={handleInputChange}
                className="w-full border p-2 rounded-md text-black"
                placeholder="End Year"
              />
            </div>
          </div>
        </div>
      )}
    </div>

      {/* Clear All and Apply Buttons */}
      <div className="flex justify-between items-center border-t pt-4">
        <button
          className="text-red-500 font-semibold"
          onClick={() => {
            // Reset all filters to their default values
            setFilters({
              genres: [],
              country: '',
              runtime_minutes_from: '',
              runtime_minutes_to: '',
              imdb_rating_from: '',
              published_from: '',
              published_to: '',
              // Add other filters as needed
            });
            setOrdering(''); // Reset ordering as well if necessary
            setImdbRating([0, 10]); // Reset IMDb rating slider
            setVisibleGenres(6); // Reset genres visibility if needed
            setBedrooms('Any'); // Reset bedroom filter if used
          }}
        >
          Clear all
        </button>
      </div>
    </div>
  );
}

export default Filters;