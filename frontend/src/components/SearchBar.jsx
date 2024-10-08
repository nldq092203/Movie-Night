import React, { useState, useEffect } from 'react';
import { IconSearch, IconX } from '@tabler/icons-react';
import { rem } from '@mantine/core';

function SearchBar({ onSearch }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Retrieve search terms from localStorage
  useEffect(() => {
    const storedTerms = JSON.parse(localStorage.getItem('searchTerms')) || [];
    setSuggestions(storedTerms);
  }, []);

  // Update suggestions as the user types
  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchTerm(query);

    // Filter stored terms based on input
    const storedTerms = JSON.parse(localStorage.getItem('searchTerms')) || [];
    const filteredSuggestions = storedTerms.filter((term) =>
      term.toLowerCase().startsWith(query.toLowerCase())
    );
    setSuggestions(filteredSuggestions);
  };

  // Handle search submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      onSearch(searchTerm.trim());

      // Save the new term to localStorage
      const storedTerms = JSON.parse(localStorage.getItem('searchTerms')) || [];
      if (!storedTerms.includes(searchTerm.trim().toLowerCase())) {
        const updatedTerms = [searchTerm.trim().toLowerCase(), ...storedTerms];
        localStorage.setItem('searchTerms', JSON.stringify(updatedTerms));
      }

      setSearchTerm(''); // Clear input
      setSuggestions([]); // Clear suggestions
      setShowSuggestions(false); // Hide suggestions
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (term) => {
    setSearchTerm(term);
    onSearch(term);
    setShowSuggestions(false); // Hide suggestions after clicking
  };

  // Show suggestions on input focus
  const handleFocus = () => {
    setShowSuggestions(true);
  };

  // Hide suggestions when clicking outside
  const handleBlur = () => {
    setTimeout(() => setShowSuggestions(false), 100); // Delay to allow click on suggestion
  };

  // Clear search input
  const handleClear = () => {
    setSearchTerm('');
    setSuggestions([]);
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-80">
      <div className="relative">
        {/* Search Icon */}
        <span className="absolute inset-y-0 left-3 flex items-center">
          <IconSearch style={{ width: rem(16), height: rem(16) }} stroke={1.5} className="text-gray-400" />
        </span>
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder="Search"
          className="w-full pl-10 pr-10 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-gray-500"
        />
        {/* Clear Search Icon */}
        {searchTerm && (
          <span
            onClick={handleClear}
            className="absolute inset-y-0 right-3 flex items-center cursor-pointer text-gray-400"
          >
            <IconX style={{ width: rem(16), height: rem(16) }} stroke={1.5} />
          </span>
        )}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute w-full mt-1 bg-gray-900 text-white rounded-lg shadow-lg max-h-40 overflow-y-auto border border-gray-700">
            {suggestions.map((term, index) => (
              <div
                key={index}
                onClick={() => handleSuggestionClick(term)}
                className="p-2 cursor-pointer hover:bg-gray-700"
              >
                {term}
              </div>
            ))}
          </div>
        )}
      </div>
    </form>
  );
}

export default SearchBar;