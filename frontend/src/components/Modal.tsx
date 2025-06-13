import React from 'react';
import type { Syllabus } from '../features/syllabi/syllabiApi';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  syllabus: Syllabus;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, syllabus }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{syllabus.course_name}</h2>
            <p className="text-gray-600">{syllabus.course_code}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <span className="text-2xl">×</span>
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500">Instructor</p>
            <p className="text-gray-900">{syllabus.instructor.name}</p>
            <p className="text-gray-600 text-sm">{syllabus.instructor.email}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Term</p>
            <p className="text-gray-900">{syllabus.term.semester} {syllabus.term.year}</p>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
              onClick={() => console.log('View Syllabus PDF:', syllabus.filename)}
            >
              View Syllabus PDF
            </button>
            <button
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition"
              onClick={() => console.log('Generate Study Plan')}
            >
              Generate Study Plan
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
