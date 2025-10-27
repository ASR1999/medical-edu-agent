import React, { useCallback } from 'react';
import { FaCloudUploadAlt, FaFilePdf, FaFileImage, FaTimes } from 'react-icons/fa';

export default function FileUploadZone({ onFileSelect, selectedFile, onFileClear }) {
  const [isDragging, setIsDragging] = React.useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      // Accept images and PDFs
      if (file.type.startsWith('image/') || file.type === 'application/pdf') {
        onFileSelect(file);
      } else {
        alert('Please upload an image or PDF file');
      }
    }
  }, [onFileSelect]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e) => {
    const files = e.target.files;
    if (files && files[0]) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept="image/*,.pdf"
            onChange={handleFileInput}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <FaCloudUploadAlt className="mx-auto text-4xl text-gray-400 mb-2" />
            <p className="text-sm text-gray-600 mb-1">
              <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">
              Medical images (PNG, JPG) or reports (PDF)
            </p>
          </label>
        </div>
      ) : (
        <div className="border-2 border-green-300 bg-green-50 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {selectedFile.type === 'application/pdf' ? (
              <FaFilePdf className="text-3xl text-red-500" />
            ) : (
              <FaFileImage className="text-3xl text-blue-500" />
            )}
            <div className="text-sm">
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          <button
            onClick={onFileClear}
            className="p-2 hover:bg-red-100 rounded-full transition-colors"
            title="Remove file"
          >
            <FaTimes className="text-red-500" />
          </button>
        </div>
      )}
    </div>
  );
}

