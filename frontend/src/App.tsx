import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ConfigProvider, theme as antdTheme, Spin } from 'antd';
import { AnimatePresence } from 'framer-motion';
import { useEffect, lazy, Suspense } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { CommandPalette } from './components/common/CommandPalette';
import { OnboardingTour } from './components/common/OnboardingTour';
import { useThemeStore, THEME_COLORS } from './store/themeStore';

// Lazy load all pages — route-based code splitting
const Login = lazy(() => import('./pages/auth/Login').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./pages/auth/Register').then(m => ({ default: m.Register })));
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard').then(m => ({ default: m.Dashboard })));
const CubeAnalysis = lazy(() => import('./pages/olap/CubeAnalysis').then(m => ({ default: m.CubeAnalysis })));
const PivotAnalysis = lazy(() => import('./pages/olap/PivotAnalysis').then(m => ({ default: m.PivotAnalysis })));
const StudentsPage = lazy(() => import('./pages/students/StudentsPage').then(m => ({ default: m.StudentsPage })));
const TeachersPage = lazy(() => import('./pages/teachers/TeachersPage').then(m => ({ default: m.TeachersPage })));
const SubjectsPage = lazy(() => import('./pages/subjects/SubjectsPage').then(m => ({ default: m.SubjectsPage })));
const GradesPage = lazy(() => import('./pages/grades/GradesPage').then(m => ({ default: m.GradesPage })));
const FacultiesPage = lazy(() => import('./pages/faculties/FacultiesPage').then(m => ({ default: m.FacultiesPage })));
const ReportsPage = lazy(() => import('./pages/reports/ReportsPage').then(m => ({ default: m.ReportsPage })));
const StudentDetail = lazy(() => import('./pages/detail/StudentDetail').then(m => ({ default: m.StudentDetail })));
const TeacherDetail = lazy(() => import('./pages/detail/TeacherDetail').then(m => ({ default: m.TeacherDetail })));
const SubjectDetail = lazy(() => import('./pages/detail/SubjectDetail').then(m => ({ default: m.SubjectDetail })));
const FacultyDetail = lazy(() => import('./pages/detail/FacultyDetail').then(m => ({ default: m.FacultyDetail })));
const SettingsPage = lazy(() => import('./pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));
const AnalyticsPage = lazy(() => import('./pages/analytics/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })));
const GradeEntryWizard = lazy(() => import('./pages/teaching/GradeEntryWizard').then(m => ({ default: m.GradeEntryWizard })));
const SchedulePage = lazy(() => import('./pages/schedule/SchedulePage').then(m => ({ default: m.SchedulePage })));
const ApplicationsPage = lazy(() => import('./pages/applications/ApplicationsPage').then(m => ({ default: m.ApplicationsPage })));
const ScholarshipPage = lazy(() => import('./pages/scholarship/ScholarshipPage').then(m => ({ default: m.ScholarshipPage })));
const UsersAdmin = lazy(() => import('./pages/admin/UsersAdmin').then(m => ({ default: m.UsersAdmin })));
const AuditPage = lazy(() => import('./pages/admin/AuditPage').then(m => ({ default: m.AuditPage })));
const AnnouncementsPage = lazy(() => import('./pages/announcements/AnnouncementsPage').then(m => ({ default: m.AnnouncementsPage })));
const PaymentsPage = lazy(() => import('./pages/payments/PaymentsPage').then(m => ({ default: m.PaymentsPage })));
const LibraryPage = lazy(() => import('./pages/library/LibraryPage').then(m => ({ default: m.LibraryPage })));
const MessagesPage = lazy(() => import('./pages/messages/MessagesPage').then(m => ({ default: m.MessagesPage })));
const CalendarPage = lazy(() => import('./pages/calendar/CalendarPage').then(m => ({ default: m.CalendarPage })));
const ThesisPage = lazy(() => import('./pages/thesis/ThesisPage').then(m => ({ default: m.ThesisPage })));
const DormitoryPage = lazy(() => import('./pages/dormitory/DormitoryPage').then(m => ({ default: m.DormitoryPage })));
const DocumentsPage = lazy(() => import('./pages/documents/DocumentsPage').then(m => ({ default: m.DocumentsPage })));
const AITutorPage = lazy(() => import('./pages/tutor/AITutorPage').then(m => ({ default: m.AITutorPage })));
const MLInsightsPage = lazy(() => import('./pages/ml/MLInsightsPage').then(m => ({ default: m.MLInsightsPage })));
const AdvancedVisualsPage = lazy(() => import('./pages/advanced/AdvancedVisualsPage'));
const UniversitiesAdmin = lazy(() => import('./pages/admin/UniversitiesAdmin'));
const TenantsAdmin = lazy(() => import('./pages/admin/TenantsAdmin'));
const LandingPage = lazy(() => import('./pages/landing/LandingPage').then(m => ({ default: m.LandingPage })));
const OnboardingWizard = lazy(() => import('./pages/landing/OnboardingWizard').then(m => ({ default: m.OnboardingWizard })));

function PageFallback() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
      <Spin size="large" />
    </div>
  );
}

export default function App() {
  const { isDark, color } = useThemeStore();
  const location = useLocation();

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
        <Suspense fallback={<PageFallback />}>
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
              <Route path="admin/universities" element={<UniversitiesAdmin />} />
              <Route path="admin/tenants" element={<TenantsAdmin />} />

              <Route path="announcements" element={<AnnouncementsPage />} />
              <Route path="payments" element={<PaymentsPage />} />
              <Route path="library" element={<LibraryPage />} />
              <Route path="messages" element={<MessagesPage />} />
              <Route path="calendar" element={<CalendarPage />} />
              <Route path="thesis" element={<ThesisPage />} />
              <Route path="dormitory" element={<DormitoryPage />} />
              <Route path="documents" element={<DocumentsPage />} />

              <Route path="ai-tutor" element={<AITutorPage />} />
              <Route path="ml-insights" element={<MLInsightsPage />} />
              <Route path="advanced-visuals" element={<AdvancedVisualsPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AnimatePresence>
    </ConfigProvider>
  );
}
