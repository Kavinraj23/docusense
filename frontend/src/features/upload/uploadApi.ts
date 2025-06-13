import api from '../../services/api';
import type { UploadResponse } from '../../types/types';

export const uploadDocument = async (formData: FormData): Promise<UploadResponse> => {
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};