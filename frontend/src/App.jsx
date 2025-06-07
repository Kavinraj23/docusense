import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const[loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");

    const formData = new FormData();
    formData.append("file", file);
    
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/upload/", formData);
      setResponse(res.data);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6 text-gray-900">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">📄 DocuSense Metadata Extractor</h1>

        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="mb-4"
        />
        <button
          onClick={handleUpload}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {loading ? "Processing..." : "Upload & Analyze"}
        </button>

        {response && (
          <div className="mt-6 bg-white shadow rounded p-4">
            <h2 className="text-xl font-semibold mb-2">📑 Metadata</h2>
            <ul className="list-disc ml-5 text-sm">
              {Object.entries(response.metadata).map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong>{" "}
                  {Array.isArray(value) ? value.join(", ") : value}
                </li>
              ))}
            </ul>

            <div className="mt-4">
              <h3 className="text-lg font-semibold">📝 PNreview</h3>
              <p className="text-gray-700 mt-2 whitespace-pre-wrap text-sm">
                {response.preview}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App
