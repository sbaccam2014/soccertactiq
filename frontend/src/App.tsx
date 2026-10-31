import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LandingPage } from './pages/LandingPage';
import { RegisterPage } from './pages/RegisterPage';
import { LoginPage } from './pages/LoginPage';
import { VideosPage } from './pages/VideosPage';
import { VideoQuestionPage } from './pages/VideoQuestionPage';
import { AttemptResultPage } from './pages/AttemptResultPage';
import { ProgressPage } from './pages/ProgressPage';
import { VideoLibraryPage } from './pages/VideoLibraryPage';
import { TrainingPage } from './pages/TrainingPage';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<LandingPage />} />
          <Route path="register" element={<RegisterPage />} />
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
            path="videos-questions/:videoId"
            element={
              <ProtectedRoute>
                <VideoQuestionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="attempts/:attemptId"
            element={
              <ProtectedRoute>
                <AttemptResultPage />
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
          <Route
            path="videos"
            element={
              <ProtectedRoute>
                <VideoLibraryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="training"
            element={
              <ProtectedRoute>
                <TrainingPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
