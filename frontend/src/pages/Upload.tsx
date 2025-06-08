import React from 'react';
import UploadForm from '../features/upload/UploadForm';

const UploadPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">Upload a Document</h1>
      <UploadForm />
    </div>
  );
};

export default UploadPage;