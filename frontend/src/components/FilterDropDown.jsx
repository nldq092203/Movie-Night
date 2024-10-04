import React from 'react';
import Filters from './MovieFilters';

function FilterDropdown({ filters, setFilters, ordering, setOrdering, isFilterOpen, setIsFilterOpen }) {
  return (
    <>
      {/* Filter Button always at top-left */}
      <button
        className="fixed top-4 left-4 text-white p-2 rounded-full bg-gray-700 hover:bg-gray-600 z-20"
        onClick={() => setIsFilterOpen(!isFilterOpen)}
      >
        <span className="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 012 0v2a1 1 0 01-2 0V4zm3 0a1 1 0 011 1v1a1 1 0 01-1 1H4V4h2zm1 3h12v2H7V7zm5 4v8a1 1 0 001 1h1a1 1 0 001-1v-8a1 1 0 00-1-1h-1a1 1 0 00-1 1zm-5 0h1a1 1 0 011 1v8a1 1 0 01-1 1H7a1 1 0 01-1-1v-8a1 1 0 011-1zm8 0h1a1 1 0 011 1v8a1 1 0 01-1 1h-1a1 1 0 01-1-1v-8a1 1 0 011-1z" />
          </svg>
          <span className="ml-2">Filters</span>
        </span>
      </button>

      {/* Filter Dropdown */}
      {isFilterOpen && (
        <div className="fixed top-0 left-0 z-40 w-full h-full bg-black bg-opacity-50">
          <div className="absolute top-16 left-4 bg-gray-800 w-64 h-full p-4">
            <button
              className="text-white mb-4"
              onClick={() => setIsFilterOpen(false)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <Filters filters={filters} setFilters={setFilters} ordering={ordering} setOrdering={setOrdering} />
          </div>
        </div>
      )}
    </>
  );
}

export default FilterDropdown;