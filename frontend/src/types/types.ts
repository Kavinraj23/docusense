export interface UploadResponse {
  filename: string;
  metadata: {
    title: string;
    author: string;
    document_type: string;
    date: string;
    [key: string]: string; // allow extra fields
  };
}