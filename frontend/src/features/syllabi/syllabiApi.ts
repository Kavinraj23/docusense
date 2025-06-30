import api from '../../services/api';
import type { AccentColor } from '../../components/ClassCard';

export interface Syllabus {
  id: number;
  filename: string;
  course_code: string;
  course_name: string;
  instructor: {
    name: string;
    email: string;
  };
  term: {
    semester: string;
    year: string;
  };
  description: string;
  meeting_info: {
    days: string;
    time: string;
    location: string;
  };
  important_dates: {
    first_class: string;
    last_class: string;
    midterms: string[];
    final_exam: string;
  };
  grading_policy: Record<string, string>;
  schedule_summary: string;
  accent_color?: AccentColor;
}

export const fetchSyllabi = async (): Promise<Syllabus[]> => {
  const response = await api.get('/syllabi');
  return response.data;
};

export const deleteSyllabus = async (id: number): Promise<void> => {
  await api.delete(`/syllabi/${id}`);
};

export const updateSyllabusColor = async (id: number, color: AccentColor): Promise<void> => {
  await api.patch(`/syllabi/${id}/color`, { accent_color: color });
};

export const updateSyllabusDetails = async (id: number, updates: Partial<Syllabus>): Promise<void> => {
  await api.patch(`/syllabi/${id}`, updates);
};

// Note: File URL functionality removed as we don't store file_url in database anymore
export const getSyllabusFileUrl = async (id: number): Promise<string> => {
  throw new Error("File URL functionality not available");
};
