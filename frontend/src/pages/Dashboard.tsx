import React, { useState, useEffect } from 'react';
import ClassCard from '../components/ClassCard';
import Modal from '../components/Modal';
import UploadModal from '../components/UploadModal';
import { fetchSyllabi } from '../features/syllabi/syllabiApi';
import type { Syllabus } from '../features/syllabi/syllabiApi';

const DashboardPage: React.FC = () => {
  const [selectedClass, setSelectedClass] = useState<number | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const loadSyllabi = async () => {
    try {
      setLoading(true);
      const data = await fetchSyllabi();
      setSyllabi(data);
    } catch (err) {
      setError('Failed to load syllabi. Please try again later.');
      console.error('Error loading syllabi:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSyllabi();
  }, []);

  const handleUploadSuccess = () => {
    loadSyllabi(); // Reload syllabi after successful upload
  };

  const selectedSyllabus = syllabi.find(s => s.id === selectedClass);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Study Snap</h2>
          <nav className="space-y-2">
            <button className="w-full text-left px-4 py-2 bg-blue-50 text-blue-700 rounded-md font-medium">
              Dashboard
            </button>
            <button className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-md">
              Settings
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">My Classes</h1>
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center space-x-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                <span>Upload Syllabus</span>
              </button>
            </div>
            
            {/* Loading State */}
            {loading && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading your classes...</p>
              </div>
            )}

            {/* Error State */}
            {error && !loading && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 text-center">
                <p className="text-red-600">{error}</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="mt-2 text-red-600 hover:text-red-700 underline"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Class Cards Grid */}
            {!loading && !error && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {syllabi.length === 0 ? (
                  <div className="col-span-full text-center py-12">
                    <p className="text-gray-600">No classes found. Upload a syllabus to get started.</p>
                  </div>
                ) : (
                  syllabi.map((syllabus) => (
                    <ClassCard
                      key={syllabus.id}
                      syllabus={syllabus}
                      onClick={() => setSelectedClass(syllabus.id)}
                    />
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Syllabus Modal */}
      {selectedSyllabus && (
        <Modal
          isOpen={selectedClass !== null}
          onClose={() => setSelectedClass(null)}
          syllabus={selectedSyllabus}
        />
      )}

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
};

export default DashboardPage;