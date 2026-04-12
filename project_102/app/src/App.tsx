/**
 * DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System
 * Main App Component
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Pages
import ChooseLogin from './pages/ChooseLogin';
import AdminLogin from './pages/AdminLogin';
import StaffLogin from './pages/StaffLogin';
import AdminDashboard from './pages/AdminDashboard';
import StaffDashboard from './pages/StaffDashboard';
import IncidentReports from './pages/IncidentReports';
import UserManagement from './pages/UserManagement';
import Settings from './pages/Settings';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Toaster 
            position="top-right" 
            richColors 
            closeButton
            toastOptions={{
              style: {
                fontSize: '14px',
              },
            }}
          />
          <Routes>
            {/* Choose Login Page */}
            <Route path="/" element={<ChooseLogin />} />

            {/* Separate Login Pages */}
            <Route path="/admin-login" element={<AdminLogin />} />
            <Route path="/staff-login" element={<StaffLogin />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                {/* Admin Routes */}
                <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                  <Route path="/admin/dashboard" element={<AdminDashboard />} />
                  <Route path="/admin/users" element={<UserManagement />} />
                </Route>

                {/* Staff Routes */}
                <Route element={<ProtectedRoute allowedRoles={['staff']} />}>
                  <Route path="/staff/dashboard" element={<StaffDashboard />} />
                </Route>

                {/* Common Routes */}
                <Route path="/reports" element={<IncidentReports />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <SpeedInsights />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;