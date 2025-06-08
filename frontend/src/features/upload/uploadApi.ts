import api from '../../services/api';
import type { UploadResponse } from '../../types/types';

export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData);
  return response.data;
};