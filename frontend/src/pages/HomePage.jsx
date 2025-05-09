import React, { useState } from 'react';
import { ArrowRightIcon } from '@heroicons/react/24/solid';
import { LinkIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

const HomePage = () => {
  const [activeTab, setActiveTab] = useState('url');
  const [inputData, setInputData] = useState({
    url: '',
    file: null
  });
  const [isProcessing, setIsProcessing] = useState(false);
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

  const handleSubmit = async () => {
    if (activeTab === 'url' && !inputData.url) {
      setError('Please enter a URL');
      return;
    }
    
    if (activeTab === 'upload' && !inputData.file) {
      setError('Please upload a file');
      return;
    }
    
    setIsProcessing(true);
    
    try {
      // API call would go here
      const formData = new FormData();
      if (activeTab === 'url') {
        formData.append('url', inputData.url);
      } else {
        formData.append('file', inputData.file);
      }
      
      // Replace with your actual API endpoint
      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to process content');
      }
      
      const data = await response.json();
      console.log('Processing result:', data);
      // Handle successful response
      
    } catch (error) {
      console.error('Error processing content:', error);
      setError('An error occurred while processing your request');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Browser-like header */}
        <div className="bg-gray-800 px-4 py-2 flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <div className="flex-1 flex justify-center">
            <div className="bg-gray-700 rounded-full px-4 py-1 text-gray-300 text-sm flex items-center">
            
            </div>
          </div>
        </div>
        
        {/* Tab navigation */}
        <div className="flex bg-gray-200">
          <button
            className={`px-4 py-2 text-sm font-medium flex items-center ${
              activeTab === 'url'
                ? 'bg-white text-gray-800'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
            onClick={() => setActiveTab('url')}
          >
            <LinkIcon className="h-4 w-4 mr-2" />
            URL
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium flex items-center ${
              activeTab === 'upload'
                ? 'bg-white text-gray-800'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
            onClick={() => setActiveTab('upload')}
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Upload
          </button>
          <div className="flex-1 bg-gray-200"></div>
        </div>
        
        {/* Content area */}
        <div className="p-6">
          <div className="text-center mb-6">
            {/* <h1 className="text-2xl font-bold text-gray-900">
              Transform Content to Video
            </h1>
            <p className="text-gray-600 mt-1">
              Convert research papers, articles, and more into engaging videos
            </p> */}
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
                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none transition"
              />
            
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
                  <div className="flex text-sm text-gray-600 justify-center">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-gray-700 hover:text-gray-900 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-gray-500"
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
          
          <div className="mt-8">
            <button
              onClick={handleSubmit}
              disabled={isProcessing || (activeTab === 'url' && !inputData.url) || (activeTab === 'upload' && !inputData.file)}
              className="w-full flex items-center justify-center space-x-3 bg-gray-800 hover:bg-black text-white font-medium py-3 px-6 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Generate Video</span>
                  <ArrowRightIcon className="h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 