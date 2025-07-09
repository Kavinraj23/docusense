import { uploadApi } from '../../services/api';
import type { UploadResponse } from '../../types/types';

export const uploadDocument = async (formData: FormData): Promise<UploadResponse> => {
  const response = await uploadApi.post('/upload/', formData);
  return response.data;
};