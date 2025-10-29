import React from 'react';

export default function LoadingIndicator({ message = 'Thinking...', show3D = false }) {
  if (show3D) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-blue-200 rounded-full animate-ping"></div>
          <div className="absolute inset-0 border-4 border-t-blue-600 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
        </div>
        <p className="mt-4 text-sm text-gray-600 animate-pulse">{message}</p>
      </div>
    );
  }

  return (
    <div className="flex items-start space-x-2">
      <div className="bg-white text-gray-800 p-4 rounded-lg shadow-md flex items-center space-x-3">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        <span className="text-sm font-medium">{message}</span>
      </div>
    </div>
  );
}



