import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../presentation/auth/app_lock_screen.dart';
import '../presentation/auth/login_screen.dart';
import '../presentation/auth/register_screen.dart';
import '../presentation/auth/splash_screen.dart';
import '../presentation/dashboard/dashboard_screen.dart';
import '../presentation/extras/extras_screen.dart';
import '../presentation/grades/grades_screen.dart';
import '../presentation/notifications/notifications_screen.dart';
import '../presentation/profile/profile_screen.dart';
import '../presentation/schedule/schedule_screen.dart';
import '../presentation/settings/settings_screen.dart';
import '../presentation/teacher/grade_entry_screen.dart';
import '../presentation/teacher/my_groups_screen.dart';
import '../presentation/teacher/my_subjects_screen.dart';
import '../presentation/widgets/app_shell.dart';
import '../providers/auth_provider.dart';
import '../providers/settings_provider.dart';

/// Auth va app-lock state'larini `Listenable` ga ulab, go_router refresh.
class _RouterRefresh extends ChangeNotifier {
  _RouterRefresh(Ref ref) {
    ref.listen<AuthState>(authControllerProvider, (_, _) => notifyListeners());
    ref.listen<bool>(appLockProvider, (_, _) => notifyListeners());
  }
}

/// Sliding (Cupertino-style) page transition har bir custom GoRoute uchun.
Page<T> _slidePage<T>(Widget child, GoRouterState state) {
  return CustomTransitionPage<T>(
    key: state.pageKey,
    child: child,
    transitionsBuilder: (context, animation, secondary, child) {
      final tween = Tween<Offset>(
        begin: const Offset(0.05, 0),
        end: Offset.zero,
      ).chain(CurveTween(curve: Curves.easeOutCubic));
      return FadeTransition(
        opacity: animation,
        child: SlideTransition(
          position: animation.drive(tween),
          child: child,
        ),
      );
    },
  );
}

final appRouterProvider = Provider<GoRouter>((ref) {
  final refresh = _RouterRefresh(ref);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: refresh,
    redirect: (context, state) {
      final auth = ref.read(authControllerProvider);
      final locked = ref.read(appLockProvider);
      final loc = state.matchedLocation;

      if (auth is AuthInitial || auth is AuthLoading) {
        return loc == '/splash' ? null : '/splash';
      }
      if (auth is Authenticated) {
        if (locked && loc != '/lock') return '/lock';
        if (!locked && loc == '/lock') return '/dashboard';
        if (loc == '/splash' || loc == '/login' || loc == '/register') {
          return '/dashboard';
        }
        return null;
      }
      // Unauthenticated yoki AuthError
      const publicRoutes = {'/login', '/register'};
      if (publicRoutes.contains(loc)) return null;
      return '/login';
    },
    routes: [
      GoRoute(
        path: '/splash',
        pageBuilder: (_, state) => _slidePage(const SplashScreen(), state),
      ),
      GoRoute(
        path: '/login',
        pageBuilder: (_, state) => _slidePage(const LoginScreen(), state),
      ),
      GoRoute(
        path: '/register',
        pageBuilder: (_, state) => _slidePage(const RegisterScreen(), state),
      ),
      GoRoute(
        path: '/lock',
        pageBuilder: (_, state) => _slidePage(const AppLockScreen(), state),
      ),
      GoRoute(
        path: '/settings',
        pageBuilder: (_, state) => _slidePage(const SettingsScreen(), state),
      ),
      GoRoute(
        path: '/teacher/subjects',
        pageBuilder: (_, state) => _slidePage(const MySubjectsScreen(), state),
      ),
      GoRoute(
        path: '/teacher/groups',
        pageBuilder: (_, state) => _slidePage(const MyGroupsScreen(), state),
      ),
      GoRoute(
        path: '/teacher/grade-entry',
        pageBuilder: (_, state) => _slidePage(const GradeEntryScreen(), state),
      ),

      StatefulShellRoute.indexedStack(
        builder: (context, state, shell) => AppShell(
          shell: shell,
          tabs: const [
            ShellTab(
              icon: Icons.dashboard_outlined,
              selectedIcon: Icons.dashboard,
              label: 'Asosiy',
            ),
            ShellTab(
              icon: Icons.assessment_outlined,
              selectedIcon: Icons.assessment,
              label: 'Baholar',
            ),
            ShellTab(
              icon: Icons.dashboard_customize_outlined,
              selectedIcon: Icons.dashboard_customize,
              label: 'Qo\'shimcha',
            ),
            ShellTab(
              icon: Icons.calendar_today_outlined,
              selectedIcon: Icons.calendar_today,
              label: 'Jadval',
            ),
            ShellTab(
              icon: Icons.notifications_outlined,
              selectedIcon: Icons.notifications,
              label: 'Xabarlar',
            ),
          ],
        ),
        branches: [
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/dashboard',
              builder: (_, _) => const DashboardScreen(),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/grades',
              builder: (_, _) => const GradesScreen(),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/extras',
              builder: (_, _) => const ExtrasScreen(),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/schedule',
              builder: (_, _) => const ScheduleScreen(),
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/notifications',
              builder: (_, _) => const NotificationsScreen(),
            ),
          ]),
        ],
      ),

      GoRoute(
        path: '/profile',
        pageBuilder: (_, state) => _slidePage(const ProfileScreen(), state),
      ),
    ],
  );
});
