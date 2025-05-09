import React from 'react';

const SuggestionList = ({ suggestions }) => {
  return (
    <div className="space-y-3">
      {suggestions.map((suggestion) => (
        <div 
          key={suggestion.id} 
          className="flex items-start p-2 hover:bg-gray-50 rounded-lg cursor-pointer"
        >
          <div className="flex-shrink-0 text-gray-400 mt-0.5 mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
            </svg>
          </div>
          <span className="text-gray-800">{suggestion.text}</span>
        </div>
      ))}
    </div>
  );
};

export default SuggestionList; 