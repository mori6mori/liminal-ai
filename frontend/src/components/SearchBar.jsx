import React from 'react';

const SearchBar = ({ value, onChange, onFocus }) => {
  return (
    <div className="relative mb-4">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
        </svg>
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
        placeholder="Search for content to convert to video..."
        value={value}
        onChange={onChange}
        onFocus={onFocus}
      />
    </div>
  );
};

export default SearchBar; 