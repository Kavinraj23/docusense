import React, { useState } from 'react';
import type { Syllabus } from '../features/syllabi/syllabiApi';

export type AccentColor = 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple' | 'pink' | 'indigo';

const ACCENT_COLORS: Record<AccentColor, { bg: string, hover: string, text: string }> = {
  red: { bg: 'bg-red-500', hover: 'hover:bg-red-600', text: 'text-red-500' },
  orange: { bg: 'bg-orange-500', hover: 'hover:bg-orange-600', text: 'text-orange-500' },
  yellow: { bg: 'bg-yellow-500', hover: 'hover:bg-yellow-600', text: 'text-yellow-500' },
  green: { bg: 'bg-green-500', hover: 'hover:bg-green-600', text: 'text-green-500' },
  blue: { bg: 'bg-blue-500', hover: 'hover:bg-blue-600', text: 'text-blue-500' },
  purple: { bg: 'bg-purple-500', hover: 'hover:bg-purple-600', text: 'text-purple-500' },
  pink: { bg: 'bg-pink-500', hover: 'hover:bg-pink-600', text: 'text-pink-500' },
  indigo: { bg: 'bg-indigo-500', hover: 'hover:bg-indigo-600', text: 'text-indigo-500' }
};

interface ClassCardProps {
  syllabus: Syllabus;
  onClick: () => void;
  onDelete: (id: number) => void;
  accentColor?: AccentColor;
  onColorChange?: (color: AccentColor) => void;
  isDarkMode?: boolean;
}

const ColorPickerModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onColorSelect: (color: AccentColor) => void;
  currentColor: AccentColor;
  isDarkMode?: boolean;
}> = ({ isOpen, onClose, onColorSelect, currentColor, isDarkMode }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-full max-w-md shadow-xl`} onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h3 className={`text-xl font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Choose Color</h3>
          <button onClick={onClose} className={`${isDarkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'} transition-colors`}>
            <svg className="w-6 h-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {(Object.keys(ACCENT_COLORS) as AccentColor[]).map((color) => (
            <button
              key={color}
              onClick={() => {
                onColorSelect(color);
                onClose();
              }}
              className={`
                w-full aspect-square rounded-lg transition-all transform 
                ${ACCENT_COLORS[color].bg} ${ACCENT_COLORS[color].hover}
                ${currentColor === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'hover:scale-105'}
              `}
              title={color.charAt(0).toUpperCase() + color.slice(1)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const DeleteConfirmationModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  courseName: string;
  isDarkMode?: boolean;
}> = ({ isOpen, onClose, onConfirm, courseName, isDarkMode }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-full max-w-md shadow-xl`}>
        <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Delete Syllabus</h3>
        <p className={`mb-6 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
          Are you sure you want to delete the syllabus for <span className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{courseName}</span>? 
          This action cannot be undone.
        </p>
        <div className="flex space-x-4">
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 rounded-lg border ${
              isDarkMode 
                ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            } transition-colors`}
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

const ClassCard: React.FC<ClassCardProps> = ({ syllabus, onClick, onDelete, accentColor = 'blue', onColorChange, isDarkMode }) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    onDelete(syllabus.id);
    setShowDeleteModal(false);
  };

  const handleColorButtonClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowColorPicker(true);
  };

  return (
    <>      <div
        onClick={onClick}
        className={`relative group rounded-lg shadow-md overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02] ${
          isDarkMode ? 'bg-gray-800' : 'bg-white'
        }`}
      >
        {/* Accent color bar */}
        <div className={`h-2 ${ACCENT_COLORS[accentColor].bg}`} />

        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className={`text-lg font-semibold mb-1 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {syllabus.course_code}
              </h3>
              <h4 className={`text-sm line-clamp-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {syllabus.course_name}
              </h4>
            </div>
          </div>

          <div className={`text-sm space-y-1 mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            <p className="flex items-center">
              <svg className="w-4 h-4 mr-2 opacity-70" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {syllabus.instructor.name}
            </p>
            <p className="flex items-center">
              <svg className="w-4 h-4 mr-2 opacity-70" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {syllabus.term.semester} {syllabus.term.year}
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex justify-end space-x-2 mt-4">
            {onColorChange && (
              <button
                onClick={handleColorButtonClick}
                className={`p-2 rounded-full hover:bg-gray-100 transition-colors ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}
              >
                <svg className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              </button>
            )}
            <button
              onClick={handleDelete}
              className={`p-2 rounded-full transition-colors ${
                isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-600'
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <ColorPickerModal
        isOpen={showColorPicker}
        onClose={() => setShowColorPicker(false)}
        onColorSelect={(color) => {
          if (onColorChange) onColorChange(color);
          setShowColorPicker(false);
        }}
        currentColor={accentColor}
        isDarkMode={isDarkMode}
      />

      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={confirmDelete}
        courseName={`${syllabus.course_code} - ${syllabus.course_name}`}
        isDarkMode={isDarkMode}
      />
    </>
  );
};

export default ClassCard;