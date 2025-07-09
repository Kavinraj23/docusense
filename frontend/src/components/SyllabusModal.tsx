import React, { useState } from 'react';
import type { Syllabus } from '../features/syllabi/syllabiApi';
import { updateSyllabusDetails, getSyllabusFileUrl } from '../features/syllabi/syllabiApi';
import { syncSyllabusToGoogleCalendar, getCalendarStatus, initiateGoogleAuth } from '../services/api';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  syllabus: Syllabus;
  isDarkMode?: boolean;
  onUpdate?: (updatedSyllabus: Partial<Syllabus>) => void;
}

interface EditableSyllabusFields {
  important_dates: {
    first_class: string;
    last_class: string;
    midterms: string[];
    final_exam: string;
  };
}

const SyllabusModal: React.FC<ModalProps> = ({ isOpen, onClose, syllabus, isDarkMode, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedFields, setEditedFields] = useState<EditableSyllabusFields>({
    important_dates: {
      first_class: syllabus.important_dates.first_class || '',
      last_class: syllabus.important_dates.last_class || '',
      midterms: [...syllabus.important_dates.midterms],
      final_exam: syllabus.important_dates.final_exam || ''
    }
  });
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const formatDateForDisplay = (dateString: string): string => {
    if (!dateString) return 'Not set';
    try {
      // Parse the date string as local time to avoid timezone issues
      const [year, month, day] = dateString.split('-').map(Number);
      const date = new Date(year, month - 1, day); // month is 0-indexed
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const formatDateForInput = (dateString: string): string => {
    if (!dateString) return '';
    try {
      // Parse the date string as local time to avoid timezone issues
      const [year, month, day] = dateString.split('-').map(Number);
      const date = new Date(year, month - 1, day); // month is 0-indexed
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
  };

  const createDateFromInput = (value: string): string => {
    if (!value) return '';
    try {
      // Parse the input value as local time to avoid timezone issues
      const [year, month, day] = value.split('-').map(Number);
      const date = new Date(year, month - 1, day); // month is 0-indexed
      return date.toISOString().split('T')[0];
    } catch {
      return value;
    }
  };

  const handleDateChange = (field: keyof EditableSyllabusFields['important_dates'], value: string) => {
    setEditedFields(prev => ({
      ...prev,
      important_dates: {
        ...prev.important_dates,
        [field]: createDateFromInput(value)
      }
    }));
  };

  const handleMidtermDateChange = (index: number, value: string) => {
    setEditedFields(prev => ({
      ...prev,
      important_dates: {
        ...prev.important_dates,
        midterms: prev.important_dates.midterms.map((date, i) => 
          i === index ? createDateFromInput(value) : date
        )
      }
    }));
  };

  const validateDates = () => {
    const { first_class, last_class, final_exam } = editedFields.important_dates;
    
    if (first_class && last_class && new Date(first_class) > new Date(last_class)) {
      return 'First class date cannot be after last class date';
    }
    
    if (first_class && final_exam && new Date(first_class) > new Date(final_exam)) {
      return 'First class date cannot be after final exam date';
    }
    
    if (last_class && final_exam && new Date(last_class) > new Date(final_exam)) {
      return 'Last class date cannot be after final exam date';
    }
    
    return null;
  };

  const handleSave = async () => {
    try {
      await updateSyllabusDetails(syllabus.id, {
        important_dates: editedFields.important_dates
      });
      setIsEditing(false);
      if (onUpdate) {
        onUpdate({ important_dates: editedFields.important_dates });
      }
    } catch (error) {
      console.error('Failed to update syllabus:', error);
    }
  };

  const showSuccessPopup = (message: string) => {
    setSuccessMessage(message);
    setShowSuccessNotification(true);
    // Auto-dismiss after 5 seconds
    setTimeout(() => setShowSuccessNotification(false), 5000);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl`}>
          {/* Header */}
          <div className="flex justify-between items-start p-6 border-b border-gray-200 dark:border-gray-700">
            <div>
              <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {syllabus.course_code} - {syllabus.course_name}
              </h2>
              <p className={`mt-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {syllabus.instructor.name} • {syllabus.term.semester} {syllabus.term.year}
              </p>
            </div>
            <button
              onClick={onClose}
              className={`${isDarkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-500'}`}
            >
              <span className="text-2xl">×</span>
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Important Dates */}
            <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
              <div className="flex justify-between items-center mb-4">
                <h3 className={`text-lg font-semibold flex items-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  <svg className="w-5 h-5 mr-2 opacity-80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Important Dates
                </h3>
                <button
                  onClick={() => {
                    if (isEditing) {
                      handleSave();
                    } else {
                      setIsEditing(!isEditing);
                    }
                  }}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    isEditing
                      ? 'bg-blue-600 text-white'
                      : isDarkMode
                        ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {isEditing ? 'Save' : 'Edit'}
                </button>
              </div>

              {validateDates() && isEditing && (
                <div className="mb-4 p-3 bg-yellow-100 text-yellow-700 rounded-md text-sm">
                  {validateDates()}
                </div>
              )}

              <div className={`grid gap-3 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {/* First Class Date */}
                <div className="flex items-center justify-between">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    First Class
                  </span>
                  {isEditing ? (
                    <input
                      type="date"
                      value={formatDateForInput(editedFields.important_dates.first_class)}
                      onChange={(e) => handleDateChange('first_class', e.target.value)}
                      className={`px-2 py-1 rounded border ${
                        isDarkMode
                          ? 'bg-gray-700 border-gray-600 text-gray-200'
                          : 'bg-white border-gray-300'
                      }`}
                    />
                  ) : (
                    <span className="font-medium">{formatDateForDisplay(editedFields.important_dates.first_class)}</span>
                  )}
                </div>

                {/* Last Class Date */}
                <div className="flex items-center justify-between">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Last Class
                  </span>
                  {isEditing ? (
                    <input
                      type="date"
                      value={formatDateForInput(editedFields.important_dates.last_class)}
                      onChange={(e) => handleDateChange('last_class', e.target.value)}
                      className={`px-2 py-1 rounded border ${
                        isDarkMode
                          ? 'bg-gray-700 border-gray-600 text-gray-200'
                          : 'bg-white border-gray-300'
                      }`}
                    />
                  ) : (
                    <span className="font-medium">{formatDateForDisplay(editedFields.important_dates.last_class)}</span>
                  )}
                </div>

                {/* Midterm Dates */}
                {editedFields.important_dates.midterms.map((date, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="flex items-center">
                      <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Midterm {index + 1}
                    </span>
                    {isEditing ? (
                      <input
                        type="date"
                        value={formatDateForInput(date)}
                        onChange={(e) => handleMidtermDateChange(index, e.target.value)}
                        className={`px-2 py-1 rounded border ${
                          isDarkMode
                            ? 'bg-gray-700 border-gray-600 text-gray-200'
                            : 'bg-white border-gray-300'
                        }`}
                      />
                    ) : (
                      <span className="font-medium">{formatDateForDisplay(date)}</span>
                    )}
                  </div>
                ))}

                {/* Final Exam Date */}
                <div className="flex items-center justify-between">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Final Exam
                  </span>
                  {isEditing ? (
                    <input
                      type="date"
                      value={formatDateForInput(editedFields.important_dates.final_exam)}
                      onChange={(e) => handleDateChange('final_exam', e.target.value)}
                      className={`px-2 py-1 rounded border ${
                        isDarkMode
                          ? 'bg-gray-700 border-gray-600 text-gray-200'
                          : 'bg-white border-gray-300'
                      }`}
                    />
                  ) : (
                    <span className="font-medium">{formatDateForDisplay(editedFields.important_dates.final_exam)}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Meeting Info */}
            <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
              <h3 className={`text-lg font-semibold mb-3 flex items-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                <svg className="w-5 h-5 mr-2 opacity-80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Meeting Information
              </h3>
              <div className={`space-y-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                <p className="flex items-center">
                  <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {syllabus.meeting_info.days}
                </p>
                <p className="flex items-center">
                  <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {syllabus.meeting_info.time}
                </p>
                <p className="flex items-center">
                  <svg className="w-4 h-4 mr-2 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {syllabus.meeting_info.location}
                </p>
              </div>
            </div>

            {/* Course Description */}
            <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
              <h3 className={`text-lg font-semibold mb-3 flex items-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                <svg className="w-5 h-5 mr-2 opacity-80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Course Description
              </h3>
              <p className={`whitespace-pre-line ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {syllabus.description}
              </p>
            </div>

            {/* Calendar Sync Button */}
            <div className="flex justify-between items-center pt-2">
              <button 
                onClick={async () => {
                  try {
                    const fileUrl = await getSyllabusFileUrl(syllabus.id);
                    window.open(fileUrl, '_blank');
                  } catch (error) {
                    console.error('Failed to get file URL:', error);
                  }
                }}
                className={`inline-flex items-center px-4 py-2.5 rounded-lg transition-colors transform hover:scale-105 ${
                  isDarkMode 
                    ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                View Syllabus
              </button>
              
              <button className="inline-flex items-center px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors transform hover:scale-105"
                onClick={async () => {
                  try {
                    // First check if user is connected to Google Calendar
                    const status = await getCalendarStatus();
                    
                    if (!status.connected) {
                      // User is not connected, initiate OAuth flow
                      const authData = await initiateGoogleAuth();
                      // Redirect to Google OAuth
                      window.location.href = authData.authorization_url;
                      return;
                    }
                    
                    // User is connected, proceed with sync
                    const result = await syncSyllabusToGoogleCalendar(syllabus.id.toString());
                    
                    // Extract calendar name from the message
                    const calendarName = result.message.includes('School') ? 'School' : 'Primary';
                    showSuccessPopup(`Successfully synced ${result.events?.length || 0} events to ${calendarName} Calendar!`);
                  } catch (error) {
                    console.error('Calendar sync error:', error);
                    const errorResponse = error as { response?: { status?: number } };
                    if (errorResponse.response?.status === 401) {
                      alert('Google Calendar not connected. Please connect your Google Calendar first.');
                    } else {
                      alert('Failed to sync syllabus to Google Calendar.');
                    }
                  }
                }}
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Sync to School Calendar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Success Notification */}
      {showSuccessNotification && (
        <div className="fixed top-4 right-4 z-[60] bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">{successMessage}</span>
            <button
              onClick={() => setShowSuccessNotification(false)}
              className="ml-4 text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default SyllabusModal;
