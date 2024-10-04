import React, { useState } from 'react';

function SearchBar({ onSearch }) {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      onSearch(searchTerm.trim());
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    onSearch('');
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-96">
      <div className="relative">
        <span className="absolute inset-y-0 left-0 flex items-center pl-3">
          <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M10 2a8 8 0 1 1-5.293 13.293l-4.364 4.364a1 1 0 0 1-1.414-1.414l4.364-4.364A8 8 0 0 1 10 2zM4 10a6 6 0 1 0 6-6 6.006 6.006 0 0 0-6 6z" />
          </svg>
        </span>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search movies..."
          className="w-full pl-10 pr-10 py-2 bg-gray-700 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-red-500"
        />
        {searchTerm && (
          <span
            onClick={handleClear}
            className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer"
          >
            <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6.707 6.707a1 1 0 0 1 1.414 0L12 10.586l3.879-3.879a1 1 0 0 1 1.414 1.414L13.414 12l3.879 3.879a1 1 0 1 1-1.414 1.414L12 13.414l-3.879 3.879a1 1 0 0 1-1.414-1.414L10.586 12 6.707 8.121a1 1 0 0 1 0-1.414z" />
            </svg>
          </span>
        )}
      </div>
    </form>
  );
}

export default SearchBar;