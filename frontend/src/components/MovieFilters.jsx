import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Filters({ filters, setFilters, ordering, setOrdering }) {
  const [genreOptions, setGenreOptions] = useState([]);
  const [isGenresDropdownOpen, setIsGenresDropdownOpen] = useState(false); // Toggle for genres dropdown
  const [isRuntimeDropdownOpen, setIsRuntimeDropdownOpen] = useState(false); // Toggle for runtime dropdown
  const [isYearDropdownOpen, setIsYearDropdownOpen] = useState(false); // Toggle for publish_from and publish_to dropdown

  // Fetch genres from the API to populate the genre filter options
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('http://0.0.0.0:8000/api/v1/genres/');
        setGenreOptions(response.data.results);
      } catch (err) {
        console.error('Failed to fetch genres.');
      }
    };

    fetchGenres();
  }, []);

  // Handle filter changes for genres
  const handleGenreChange = (e) => {
    const value = e.target.value;
    setFilters((prevFilters) => ({
      ...prevFilters,
      genres: prevFilters.genres.includes(value)
        ? prevFilters.genres.filter((genre) => genre !== value)
        : [...prevFilters.genres, value],
    }));
  };

  // Handle filter input changes for other fields
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  // Handle ordering changes
  const handleOrderingChange = (e) => {
    setOrdering(e.target.value);
  };

  return (
    <div className="space-y-6 p-4 bg-gray-800 text-white rounded-md">
      <h3 className="text-xl font-semibold mb-4">Filter Movies</h3>

      {/* Genres Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsGenresDropdownOpen(!isGenresDropdownOpen)}
          className="w-full text-left bg-gray-700 p-2 rounded-md flex justify-between items-center"
        >
          <span>Genres</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 transition-transform ${isGenresDropdownOpen ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {isGenresDropdownOpen && (
          <div className="absolute w-full bg-gray-700 rounded-md mt-2 p-4 z-10">
            <div className="max-h-48 overflow-y-auto">
              {genreOptions.map((genre) => (
                <label key={genre.id} className="flex items-center">
                  <input
                    type="checkbox"
                    value={genre.name}
                    checked={filters.genres.includes(genre.name)}
                    onChange={handleGenreChange}
                    className="mr-2"
                  />
                  {genre.name}
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Runtime Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsRuntimeDropdownOpen(!isRuntimeDropdownOpen)}
          className="w-full text-left bg-gray-700 p-2 rounded-md flex justify-between items-center"
        >
          <span>Runtime (minutes)</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 transition-transform ${isRuntimeDropdownOpen ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {isRuntimeDropdownOpen && (
          <div className="absolute w-full bg-gray-700 rounded-md mt-2 p-4 z-10">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold mb-2">Minimum Runtime</label>
                <input
                  type="number"
                  name="runtime_minutes_from"
                  value={filters.runtime_minutes_from}
                  onChange={handleInputChange}
                  className="w-full p-2 rounded-md text-black"
                  placeholder="Min Runtime"
                />
              </div>
              <div>
                <label className="block font-semibold mb-2">Maximum Runtime</label>
                <input
                  type="number"
                  name="runtime_minutes_to"
                  value={filters.runtime_minutes_to}
                  onChange={handleInputChange}
                  className="w-full p-2 rounded-md text-black"
                  placeholder="Max Runtime"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Year Range (published_from and published_to) Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsYearDropdownOpen(!isYearDropdownOpen)}
          className="w-full text-left bg-gray-700 p-2 rounded-md flex justify-between items-center"
        >
          <span>Year Range</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-5 w-5 transition-transform ${isYearDropdownOpen ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {isYearDropdownOpen && (
          <div className="absolute w-full bg-gray-700 rounded-md mt-2 p-4 z-10">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold mb-2">From</label>
                <input
                  type="number"
                  name="published_from"
                  value={filters.published_from}
                  onChange={handleInputChange}
                  className="w-full p-2 rounded-md text-black"
                />
              </div>
              <div>
                <label className="block font-semibold mb-2">To</label>
                <input
                  type="number"
                  name="published_to"
                  value={filters.published_to}
                  onChange={handleInputChange}
                  className="w-full p-2 rounded-md text-black"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Country Filter */}
      <div>
        <label className="block font-semibold mb-2">Country:</label>
        <input
          type="text"
          name="country"
          value={filters.country}
          onChange={handleInputChange}
          className="w-full p-2 rounded-md text-black"
        />
      </div>

      {/* IMDb Rating Filter */}
      <div>
        <label className="block font-semibold mb-2">Minimum IMDb Rating:</label>
        <input
          type="number"
          step="0.1"
          name="imdb_rating_from"
          value={filters.imdb_rating_from}
          onChange={handleInputChange}
          className="w-full p-2 rounded-md text-black"
          placeholder="IMDb Rating"
        />
      </div>

      {/* Ordering */}
      <div>
        <label className="block font-semibold mb-2">Order By:</label>
        <select
          value={ordering}
          onChange={handleOrderingChange}
          className="w-full p-2 rounded-md text-black"
        >
          <option value="">Select</option>
          <option value="year">Year (Asc)</option>
          <option value="-year">Year (Desc)</option>
          <option value="runtime_minutes">Runtime (Asc)</option>
          <option value="-runtime_minutes">Runtime (Desc)</option>
          <option value="title">Title (Asc)</option>
          <option value="-title">Title (Desc)</option>
        </select>
      </div>
    </div>
  );
}

export default Filters;