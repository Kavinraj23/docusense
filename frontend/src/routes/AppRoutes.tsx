import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardPage from '../pages/Dashboard';
import LoginPage from '../pages/Login';
import SignupPage from '../pages/Signup';
import ProtectedRoute from '../components/ProtectedRoute';

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      
      {/* Protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      
      {/* Redirect root to login for now */}
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;