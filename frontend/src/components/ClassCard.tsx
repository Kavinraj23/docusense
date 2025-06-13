import React from 'react';
import type { Syllabus } from '../features/syllabi/syllabiApi';

interface ClassCardProps {
  syllabus: Syllabus;
  onClick: () => void;
}

const ClassCard: React.FC<ClassCardProps> = ({ syllabus, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
    >
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{syllabus.course_name}</h3>
      <div className="space-y-2">
        <p className="text-sm text-gray-600">
          {syllabus.course_code}
        </p>
        <p className="text-gray-600">
          <span className="font-medium">Instructor:</span> {syllabus.instructor.name}
        </p>
        <p className="text-gray-600">
          <span className="font-medium">Term:</span>{' '}
          {syllabus.term.semester} {syllabus.term.year}
        </p>
      </div>
    </div>
  );
};

export default ClassCard;
