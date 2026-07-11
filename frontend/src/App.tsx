import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/Home/HomePage';
import ChatPage from './pages/Chat/ChatPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import ComplaintsPage from './pages/Complaints/ComplaintsPage';
import DepartmentsPage from './pages/Departments/DepartmentsPage';
import EmergencyPage from './pages/Emergency/EmergencyPage';
import TourismPage from './pages/Tourism/TourismPage';
import ProfilePage from './pages/Profile/ProfilePage';
import SettingsPage from './pages/Settings/SettingsPage';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/complaints" element={<ComplaintsPage />} />
        <Route path="/complaints/:id" element={<ComplaintsPage />} />
        <Route path="/departments" element={<DepartmentsPage />} />
        <Route path="/departments/:id" element={<DepartmentsPage />} />
        <Route path="/weather" element={<div>Weather Page</div>} />
        <Route path="/traffic" element={<div>Traffic Page</div>} />
        <Route path="/tourism" element={<TourismPage />} />
        <Route path="/emergency" element={<EmergencyPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/admin" element={<div>Admin Page</div>} />
        <Route path="/officer" element={<div>Officer Page</div>} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
