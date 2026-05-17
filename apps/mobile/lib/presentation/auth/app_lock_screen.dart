import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/auth_provider.dart';
import '../../providers/settings_provider.dart';
import '../../services/biometric_service.dart';

class AppLockScreen extends ConsumerStatefulWidget {
  const AppLockScreen({super.key});

  @override
  ConsumerState<AppLockScreen> createState() => _AppLockScreenState();
}

class _AppLockScreenState extends ConsumerState<AppLockScreen> {
  bool _trying = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _unlock());
  }

  Future<void> _unlock() async {
    if (_trying) return;
    setState(() {
      _trying = true;
      _error = null;
    });
    final ok = await ref
        .read(biometricServiceProvider)
        .authenticate(reason: 'UniAnalytics PRO ga kirish');
    if (!mounted) return;
    if (ok) {
      ref.read(appLockProvider.notifier).state = false;
    } else {
      setState(() {
        _trying = false;
        _error = 'Tasdiqlanmadi';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(28),
                ),
                child: Icon(
                  Icons.fingerprint,
                  size: 56,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Ilova qulflangan',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Davom etish uchun biometrik tasdiqlash kerak',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(
                  _error!,
                  style: TextStyle(color: theme.colorScheme.error),
                ),
              ],
              const SizedBox(height: 32),
              FilledButton.icon(
                onPressed: _trying ? null : _unlock,
                icon: const Icon(Icons.fingerprint),
                label: Text(_trying ? 'Tekshirilmoqda…' : 'Tasdiqlash'),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () =>
                    ref.read(authControllerProvider.notifier).logout(),
                child: const Text('Chiqish'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
