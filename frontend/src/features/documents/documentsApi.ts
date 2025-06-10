import api from '../../services/api';

export interface Document {
  id: number;
  filename: string;
  content_type: string;
  upload_time: string;
  title: string;
  summary: string;
  keywords: string;
}

export const fetchDocuments = async (): Promise<Document[]> => {
  const response = await api.get('/documents');
  return response.data;
};
