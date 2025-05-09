import React, { useState } from 'react';
import { DocumentTextIcon, LinkIcon } from '@heroicons/react/24/outline';

const ContentInput = ({ inputData, setInputData }) => {
  const [activeTab, setActiveTab] = useState('url');
  const [error, setError] = useState('');

  const handleUrlChange = (e) => {
    setInputData({
      ...inputData,
      url: e.target.value
    });
    setError('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      if (file.type === 'application/pdf' || file.type === 'text/plain') {
        setInputData({
          ...inputData,
          file: file
        });
        setError('');
      } else {
        setError('Please upload a PDF or text file');
      }
    }
  };

  return (
    <div>
      <div className="flex border-b border-gray-200 mb-6">
        <button
          className={`flex items-center px-4 py-3 border-b-2 font-medium text-sm ${
            activeTab === 'url'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('url')}
        >
          <LinkIcon className="h-5 w-5 mr-2" />
          URL Input
        </button>
        <button
          className={`flex items-center px-4 py-3 border-b-2 font-medium text-sm ${
            activeTab === 'file'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('file')}
        >
          <DocumentTextIcon className="h-5 w-5 mr-2" />
          File Upload
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {activeTab === 'url' ? (
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            Enter URL (YouTube video, research paper, article)
          </label>
          <input
            type="text"
            id="url"
            value={inputData.url}
            onChange={handleUrlChange}
            placeholder="https://example.com/research-paper"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          />
          <p className="mt-2 text-sm text-gray-500">
            Paste a link to any content you want to convert into a video
          </p>
        </div>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload a document
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                >
                  <span>Upload a file</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".pdf,.txt"
                    onChange={handleFileChange}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF or TXT up to 10MB</p>
            </div>
          </div>
          {inputData.file && (
            <p className="mt-2 text-sm text-green-600">
              Selected file: {inputData.file.name}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ContentInput; 