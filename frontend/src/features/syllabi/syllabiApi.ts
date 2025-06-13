import api from '../../services/api';

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
}

export const fetchSyllabi = async (): Promise<Syllabus[]> => {
  const response = await api.get('/syllabi');
  return response.data;
};
