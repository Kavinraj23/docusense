import React, { useState } from 'react';
import { uploadDocument } from '../features/upload/uploadApi';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
  isDarkMode?: boolean;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onUploadSuccess, isDarkMode }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const validateFile = (file: File): boolean => {
    const fileType = file.type;
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    const isValidType = fileType === 'application/pdf' || 
                       fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                       fileExtension === 'pdf' ||
                       fileExtension === 'docx';

    if (!isValidType) {
      setError('Please upload only PDF or DOCX files');
      setFile(null);
      return false;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      setFile(null);
      return false;
    }

    setFile(file);
    setError(null);
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    validateFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (!droppedFile) return;
    validateFile(droppedFile);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      await uploadDocument(formData);
      console.log('Upload successful for file:', file.name);
      await onUploadSuccess();    } catch (err) {
      console.error('Upload error:', err);
      const error = err as { 
        response?: { 
          data?: { 
            detail?: string; 
            message?: string; 
          }; 
        }; 
        message?: string; 
      };
      const errorMessage = error?.response?.data?.detail || 
                          error?.response?.data?.message || 
                          error?.message ||
                          'Failed to upload file. Please try again.';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg max-w-md w-full p-6 shadow-xl`}>
        <div className="flex justify-between items-start mb-4">
          <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Upload Syllabus</h2>
          <button
            onClick={onClose}
            className={`${isDarkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-500'}`}
            disabled={uploading}
          >
            <span className="text-2xl">×</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div 
            className={`border-2 border-dashed rounded-lg p-6 text-center ${
              error 
                ? 'border-red-300 bg-red-50' 
                : isDarkMode
                  ? 'border-gray-600 hover:border-blue-400 hover:bg-gray-700'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            } transition-colors`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
              disabled={uploading}
            />
            <label 
              htmlFor="file-upload"
              className="cursor-pointer block"
            >
              {file ? (
                <div className={isDarkMode ? 'text-white' : 'text-gray-900'}>
                  <p className="font-medium">{file.name}</p>
                  <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <svg className={`mx-auto h-12 w-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-400'}`} stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path 
                      d="M24 8V32M32 24L24 32L16 24M8 36V40C8 41.1046 8.89543 42 10 42H38C39.1046 42 40 41.1046 40 40V36" 
                      strokeWidth="2" 
                      strokeLinecap="round" 
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className={`mt-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className={`mt-1 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    PDF or DOCX (max 10MB)
                  </p>
                </div>
              )}
            </label>
          </div>

          {error && (
            <div className="p-3 bg-red-100 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className={`px-4 py-2 rounded-md border ${
                isDarkMode 
                  ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              } transition-colors`}
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors
                ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={uploading || !file}
            >
              {uploading ? (
                <span className="flex items-center space-x-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Uploading...</span>
                </span>
              ) : (
                'Upload'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadModal;
