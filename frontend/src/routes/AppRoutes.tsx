import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadPage from '../pages/Upload';

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<UploadPage />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;