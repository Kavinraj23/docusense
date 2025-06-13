import React, { useState } from 'react';
import { uploadDocument } from '../features/upload/uploadApi';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onUploadSuccess }) => {
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
  };  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await uploadDocument(formData);
      console.log('Upload successful:', response);
      onUploadSuccess();
      onClose();
    } catch (error) {
      const err = error as { response?: { data?: { message?: string } } };
      const errorMessage = err.response?.data?.message || 'Failed to upload file. Please try again.';
      setError(errorMessage);
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Upload Syllabus</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <span className="text-2xl">×</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">          <div 
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 block"
            >
              {file ? (
                <div className="text-gray-900">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-gray-500">Click to change file</p>
                </div>
              ) : (
                <div>
                  <svg 
                    className="mx-auto h-12 w-12 text-gray-400 mb-4" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                    />
                  </svg>
                  <p className="text-gray-600">Drop your file here or click to browse</p>
                  <p className="text-sm text-gray-500 mt-1">Accepts PDF and DOCX files</p>
                </div>
              )}
            </label>
          </div>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}          <button
            type="submit"
            disabled={!file || uploading}
            className={`w-full py-2 px-4 rounded-md text-white font-medium flex items-center justify-center ${
              !file || uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading && (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {uploading ? 'Uploading...' : 'Upload Syllabus'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadModal;
