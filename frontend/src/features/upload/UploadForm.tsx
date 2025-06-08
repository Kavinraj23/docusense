import React, { useState } from 'react';
import { uploadDocument } from './uploadApi';
import type { UploadResponse } from '../../types/types';

const UploadForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const data = await uploadDocument(file);
      setResult(data);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4 border">
        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center border-2 border-dashed border-blue-400 rounded-lg p-6 cursor-pointer hover:border-blue-600 transition-colors"
        >
          <span className="text-blue-500 font-medium mb-2">
            {file ? file.name : 'Click to select a .pdf, .docx, or .txt file'}
          </span>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
          />
        </label>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition ${
            uploading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {uploading ? 'Processing...' : 'Upload & Extract Metadata'}
        </button>

        {result && (
          <div className="mt-4 bg-gray-50 border rounded p-4 text-sm max-h-96 overflow-auto">
            <h3 className="font-bold text-blue-700 mb-2">Extracted Metadata</h3>
            <pre className="whitespace-pre-wrap">{JSON.stringify(result.metadata, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;
