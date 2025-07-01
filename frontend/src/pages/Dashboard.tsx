import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ClassCard from '../components/ClassCard';
import type { AccentColor } from '../components/ClassCard';
import UploadModal from '../components/UploadModal';
import { fetchSyllabi, deleteSyllabus, updateSyllabusColor } from '../features/syllabi/syllabiApi';
import type { Syllabus } from '../features/syllabi/syllabiApi';
import SyllabusModal from '../components/SyllabusModal';
import { getCalendarStatus } from '../services/api';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { logout } = useAuth();
  const [selectedClass, setSelectedClass] = useState<number | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [calendarStatus, setCalendarStatus] = useState<{ connected: boolean; reason?: string; user_email?: string } | null>(null);

  useEffect(() => {
    // Apply dark mode to body
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  // Check calendar status on load
  const checkCalendarStatus = async () => {
    try {
      const status = await getCalendarStatus();
      setCalendarStatus(status);
    } catch (error) {
      console.error('Error checking calendar status:', error);
      setCalendarStatus({ connected: false, reason: 'Failed to check status' });
    }
  };

  // Handle OAuth callback parameters
  useEffect(() => {
    const calendarStatus = searchParams.get('calendar');
    const reason = searchParams.get('reason');
    
    if (calendarStatus === 'connected') {
      setSuccess('Google Calendar connected successfully!');
      // Clear the URL parameter
      navigate('/dashboard', { replace: true });
      // Refresh calendar status
      checkCalendarStatus();
    } else if (calendarStatus === 'error') {
      const errorMessage = reason === 'invalid_state' 
        ? 'OAuth session expired. Please try again.'
        : 'Failed to connect Google Calendar. Please try again.';
      setError(errorMessage);
      // Clear the URL parameter
      navigate('/dashboard', { replace: true });
    }
  }, [searchParams, navigate]);

  // Check calendar status on component mount
  useEffect(() => {
    checkCalendarStatus();
  }, []);

  // Clear success message after 5 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const loadSyllabi = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchSyllabi();
      setSyllabi(data);
    } catch (error: any) {
      console.error('Error loading syllabi:', error);
      
      // Handle different types of errors
      if (error.response?.status === 401) {
        setError('Authentication required. Please log in again.');
        // Redirect to login after a short delay
        setTimeout(() => {
          logout();
          navigate('/login');
        }, 2000);
      } else if (error.response?.status === 404) {
        // No syllabi found - this is normal for new users
        setSyllabi([]);
      } else if (error.response?.status >= 500) {
        setError('Server error. Please try again later.');
      } else {
        setError('Failed to load syllabi. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSyllabi();
  }, []);

  const handleUploadSuccess = async () => {
    try {
      await loadSyllabi();
      setIsUploadModalOpen(false);
    } catch (error) {
      console.error('Error reloading syllabi after upload:', error);
      setError('Upload successful, but failed to refresh the list. Please reload the page.');
    }
  };

  const handleDeleteSyllabus = async (id: number) => {
    try {
      setError(null); // Clear any existing errors
      await deleteSyllabus(id);
      await loadSyllabi(); // Refresh the list
    } catch (error) {
      const err = error as { response?: { status: number } };
      console.error('Failed to delete syllabus:', err);
      const errorMessage = err.response?.status === 404
        ? 'Syllabus not found. It may have been already deleted.'
        : 'Failed to delete syllabus. Please try again.';
      setError(errorMessage);
      // Clear error after 5 seconds
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleColorChange = async (syllabusId: number, color: AccentColor) => {
    try {
      setError(null);
      await updateSyllabusColor(syllabusId, color);
      // Update the local state to reflect the color change
      setSyllabi(prevSyllabi => prevSyllabi.map(syllabus => 
        syllabus.id === syllabusId 
          ? { ...syllabus, accent_color: color }
          : syllabus
      ));
    } catch (error) {
      console.error('Failed to update syllabus color:', error);
      setError('Failed to update color. Please try again.');
      // Clear error after 5 seconds
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleDeleteAllSyllabi = async () => {
    try {
      setError(null);
      // Delete each syllabus
      await Promise.all(syllabi.map(syllabus => deleteSyllabus(syllabus.id)));
      await loadSyllabi();
      setShowDeleteConfirmation(false);
      setShowSettingsPanel(false);
    } catch (error) {
      console.error('Error deleting all syllabi:', error);
      setError('Failed to delete all syllabi. Please try again.');
    }
  };

  const handleLogout = () => {
    logout(); // This will clear the token from localStorage
    navigate('/login');
  };

  const selectedSyllabus = syllabi.find(s => s.id === selectedClass);



  return (
    <div className={`flex h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <div className={`w-64 ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow-md flex flex-col`}>
        <div className="p-6 flex-1">
          <h2 className={`text-xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
            Study Snap
          </h2>
          <nav className="space-y-2">
            <button 
              className={`w-full text-left px-4 py-2 rounded-md font-medium 
                ${!showSettingsPanel ? 'bg-blue-50 text-blue-700' : isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-50'}`}
              onClick={() => setShowSettingsPanel(false)}
            >
              Dashboard
            </button>
            <button 
              className={`w-full text-left px-4 py-2 rounded-md font-medium
                ${showSettingsPanel ? 'bg-blue-50 text-blue-700' : isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-50'}`}
              onClick={() => setShowSettingsPanel(true)}
            >
              Settings
            </button>
          </nav>
        </div>
        
        {/* Logout button at bottom of sidebar */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleLogout}
            className={`w-full px-4 py-2 text-left rounded-md font-medium transition-colors ${
              isDarkMode 
                ? 'text-gray-300 hover:bg-gray-700 hover:text-white' 
                : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Logout</span>
            </div>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="max-w-7xl mx-auto">
            {showSettingsPanel ? (
              <div className={`rounded-lg p-6 ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}>
                <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Settings</h2>
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <span className={isDarkMode ? 'text-white' : 'text-gray-900'}>Dark Mode</span>
                    <button
                      onClick={() => setIsDarkMode(!isDarkMode)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                        ${isDarkMode ? 'bg-blue-600' : 'bg-gray-200'}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                          ${isDarkMode ? 'translate-x-6' : 'translate-x-1'}`}
                      />
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={isDarkMode ? 'text-white' : 'text-gray-900'}>Delete All Classes</span>
                    <button
                      onClick={() => setShowDeleteConfirmation(true)}
                      className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                    >
                      Delete All
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className="flex justify-between items-center mb-6">
                  <h1 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>My Classes</h1>
                  <div className="flex items-center space-x-4">
                    {/* Calendar Status Indicator - Only show if connected */}
                    {calendarStatus?.connected && (
                      <div className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                        <span>Connected ({calendarStatus.user_email})</span>
                    </div>
                    )}
                    <button
                      onClick={() => setIsUploadModalOpen(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M12 4v16m8-8H4"></path>
                      </svg>
                      <span>Upload Syllabus</span>
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-lg">
                    {success}
                  </div>
                )}

                {loading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className={`mt-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Loading syllabi...</p>
                  </div>
                ) : syllabi.length === 0 ? (
                  <div className="text-center py-12">
                    <p className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
                      No syllabi uploaded yet. Click the Upload button to get started!
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {syllabi.map((syllabus) => (
                      <ClassCard
                        key={syllabus.id}
                        syllabus={syllabus}
                        onClick={() => setSelectedClass(syllabus.id)}
                        onDelete={() => handleDeleteSyllabus(syllabus.id)}
                        accentColor={(syllabus.accent_color as AccentColor) || 'blue'}
                        onColorChange={(color) => handleColorChange(syllabus.id, color)}
                        isDarkMode={isDarkMode}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Delete All Confirmation Modal */}
      {showDeleteConfirmation && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 max-w-md w-full shadow-xl`}>
            <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Delete All Classes
            </h3>
            <p className={`mb-6 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Are you sure you want to delete all classes? This action cannot be undone.
            </p>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowDeleteConfirmation(false)}
                className={`flex-1 px-4 py-2 rounded-lg border ${
                  isDarkMode 
                    ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                } transition-colors`}
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAllSyllabi}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        isDarkMode={isDarkMode}
      />

      {selectedSyllabus && (
        <SyllabusModal
          isOpen={selectedClass !== null}
          onClose={() => setSelectedClass(null)}
          syllabus={selectedSyllabus}
          isDarkMode={isDarkMode}
        />
      )}
    </div>
  );
};

export default DashboardPage;