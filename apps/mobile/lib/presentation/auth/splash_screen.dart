import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants/app_constants.dart';
import '../../providers/auth_provider.dart';
import '../widgets/animated_blobs_background.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Faqat haqiqiy boshlang'ich holatda bootstrap chaqirilsin.
      // AuthLoading paytida login allaqachon ishlamoqda — uni buzmaymiz
      // (router AuthLoading'ni /splash ga yo'naltirgan bo'lsa ham).
      final state = ref.read(authControllerProvider);
      if (state is AuthInitial) {
        ref.read(authControllerProvider.notifier).bootstrap();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return Scaffold(
      body: AnimatedBlobsBackground(
        child: SafeArea(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Hero(
                  tag: 'app-logo',
                  child: _Logo(scheme: scheme),
                ).animate().scale(
                      duration: 700.ms,
                      curve: Curves.easeOutBack,
                      begin: const Offset(0.7, 0.7),
                    ),
                const SizedBox(height: 28),
                Text(
                  AppConstants.appName,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    color: scheme.onSurface,
                  ),
                ).animate(delay: 200.ms).fadeIn(duration: 600.ms).slideY(
                      begin: 0.2,
                      curve: Curves.easeOutCubic,
                    ),
                const SizedBox(height: 6),
                Text(
                  'Talabalar reyting tahlili',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: scheme.onSurfaceVariant,
                    fontWeight: FontWeight.w500,
                  ),
                ).animate(delay: 400.ms).fadeIn(duration: 600.ms),
                const SizedBox(height: 56),
                SizedBox(
                  width: 26,
                  height: 26,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    color: scheme.primary,
                  ),
                ).animate(delay: 600.ms).fadeIn(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Logo extends StatelessWidget {
  final ColorScheme scheme;
  const _Logo({required this.scheme});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 116,
      height: 116,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [scheme.primary, scheme.tertiary],
        ),
        borderRadius: BorderRadius.circular(34),
        boxShadow: [
          BoxShadow(
            color: scheme.primary.withValues(alpha: 0.45),
            blurRadius: 40,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: const Icon(
        Icons.analytics_outlined,
        size: 64,
        color: Colors.white,
      ),
    );
  }
}
