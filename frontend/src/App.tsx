import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { AnimatePresence } from 'framer-motion';
import { useEffect } from 'react';
import { Login } from './pages/auth/Login';
import { Register } from './pages/auth/Register';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/dashboard/Dashboard';
import { CubeAnalysis } from './pages/olap/CubeAnalysis';
import { PivotAnalysis } from './pages/olap/PivotAnalysis';
import { StudentsPage } from './pages/students/StudentsPage';
import { TeachersPage } from './pages/teachers/TeachersPage';
import { SubjectsPage } from './pages/subjects/SubjectsPage';
import { GradesPage } from './pages/grades/GradesPage';
import { FacultiesPage } from './pages/faculties/FacultiesPage';
import { ReportsPage } from './pages/reports/ReportsPage';
import { StudentDetail } from './pages/detail/StudentDetail';
import { TeacherDetail } from './pages/detail/TeacherDetail';
import { SubjectDetail } from './pages/detail/SubjectDetail';
import { FacultyDetail } from './pages/detail/FacultyDetail';
import { SettingsPage } from './pages/settings/SettingsPage';
import { AnalyticsPage } from './pages/analytics/AnalyticsPage';
import { GradeEntryWizard } from './pages/teaching/GradeEntryWizard';
import { SchedulePage } from './pages/schedule/SchedulePage';
import { ApplicationsPage } from './pages/applications/ApplicationsPage';
import { ScholarshipPage } from './pages/scholarship/ScholarshipPage';
import { UsersAdmin } from './pages/admin/UsersAdmin';
import { AuditPage } from './pages/admin/AuditPage';
import { AnnouncementsPage } from './pages/announcements/AnnouncementsPage';
import { PaymentsPage } from './pages/payments/PaymentsPage';
import { LibraryPage } from './pages/library/LibraryPage';
import { MessagesPage } from './pages/messages/MessagesPage';
import { CalendarPage } from './pages/calendar/CalendarPage';
import { ThesisPage } from './pages/thesis/ThesisPage';
import { DormitoryPage } from './pages/dormitory/DormitoryPage';
import { DocumentsPage } from './pages/documents/DocumentsPage';
import { AITutorPage } from './pages/tutor/AITutorPage';
import { MLInsightsPage } from './pages/ml/MLInsightsPage';
import { LandingPage } from './pages/landing/LandingPage';
import { OnboardingWizard } from './pages/landing/OnboardingWizard';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { CommandPalette } from './components/common/CommandPalette';
import { OnboardingTour } from './components/common/OnboardingTour';
import { useThemeStore, THEME_COLORS } from './store/themeStore';

export default function App() {
  const { isDark, color } = useThemeStore();
  const location = useLocation();

  // Set data-theme attribute on <html>
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    document.documentElement.style.setProperty('--color-primary', THEME_COLORS[color].primary);
  }, [isDark, color]);

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: {
          colorPrimary: THEME_COLORS[color].primary,
          borderRadius: 8,
          fontFamily: 'Inter, system-ui, sans-serif',
        },
      }}
    >
      <CommandPalette />
      <OnboardingTour />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/landing" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingWizard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />

            <Route path="olap/cube" element={<CubeAnalysis />} />
            <Route path="olap/pivot" element={<PivotAnalysis />} />

            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="grade-entry" element={<GradeEntryWizard />} />

            <Route path="schedule" element={<SchedulePage />} />
            <Route path="applications" element={<ApplicationsPage />} />
            <Route path="scholarship" element={<ScholarshipPage />} />

            <Route path="students" element={<StudentsPage />} />
            <Route path="students/:id" element={<StudentDetail />} />

            <Route path="teachers" element={<TeachersPage />} />
            <Route path="teachers/:id" element={<TeacherDetail />} />

            <Route path="subjects" element={<SubjectsPage />} />
            <Route path="subjects/:id" element={<SubjectDetail />} />

            <Route path="grades" element={<GradesPage />} />

            <Route path="faculties" element={<FacultiesPage />} />
            <Route path="faculties/:id" element={<FacultyDetail />} />

            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />

            <Route path="admin/users" element={<UsersAdmin />} />
            <Route path="admin/audit" element={<AuditPage />} />

            {/* HEMIS-style features */}
            <Route path="announcements" element={<AnnouncementsPage />} />
            <Route path="payments" element={<PaymentsPage />} />
            <Route path="library" element={<LibraryPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="thesis" element={<ThesisPage />} />
            <Route path="dormitory" element={<DormitoryPage />} />
            <Route path="documents" element={<DocumentsPage />} />

            {/* ML / AI */}
            <Route path="ai-tutor" element={<AITutorPage />} />
            <Route path="ml-insights" element={<MLInsightsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </ConfigProvider>
  );
}
