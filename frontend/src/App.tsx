import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { CoachProtectedRoute } from './components/CoachProtectedRoute';
import { ParentProtectedRoute } from './components/ParentProtectedRoute';
import { AnyAuthenticatedRoute } from './components/AnyAuthenticatedRoute';
import { LandingPage } from './pages/LandingPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage } from './pages/LoginPage';
import { VideosPage } from './pages/VideosPage';
import { VideoWatchPage } from './pages/VideoWatchPage';
import { ProgressPage } from './pages/ProgressPage';
import { TrainingPage } from './pages/TrainingPage';
import { CoachDashboardPage } from './pages/CoachDashboardPage';
import { CoachPlayerDetailPage } from './pages/CoachPlayerDetailPage';
import { CoachAddVideoPage } from './pages/CoachAddVideoPage';
import { ParentDashboardPage } from './pages/ParentDashboardPage';
import { ParentChildDetailPage } from './pages/ParentChildDetailPage';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<LandingPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <VideosPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="videos/:videoId"
            element={
              <ProtectedRoute>
                <VideoWatchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="progress"
            element={
              <ProtectedRoute>
                <ProgressPage />
              </ProtectedRoute>
            }
          />
          <Route path="videos" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="training"
            element={
              <ProtectedRoute>
                <TrainingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="coach"
            element={
              <CoachProtectedRoute>
                <CoachDashboardPage />
              </CoachProtectedRoute>
            }
          />
          <Route
            path="coach/players/:playerId"
            element={
              <CoachProtectedRoute>
                <CoachPlayerDetailPage />
              </CoachProtectedRoute>
            }
          />
          <Route
            path="coach/videos/new"
            element={
              <CoachProtectedRoute>
                <CoachAddVideoPage />
              </CoachProtectedRoute>
            }
          />
          <Route
            path="parent"
            element={
              <ParentProtectedRoute>
                <ParentDashboardPage />
              </ParentProtectedRoute>
            }
          />
          <Route
            path="parent/children/:childId"
            element={
              <ParentProtectedRoute>
                <ParentChildDetailPage />
              </ParentProtectedRoute>
            }
          />
          <Route
            path="about"
            element={
              <AnyAuthenticatedRoute>
                <AboutPage />
              </AnyAuthenticatedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
