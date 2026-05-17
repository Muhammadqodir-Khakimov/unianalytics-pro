import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../widgets/animated_blobs_background.dart';
import '../widgets/glass_card.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscure = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    ref.read(authControllerProvider.notifier).login(
          username: _usernameController.text.trim(),
          password: _passwordController.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    final state = ref.watch(authControllerProvider);
    final isLoading = state is AuthLoading;

    ref.listen<AuthState>(authControllerProvider, (prev, next) {
      if (next is AuthError) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(SnackBar(content: Text(next.message)));
      }
    });

    return Scaffold(
      body: AnimatedBlobsBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 24),
                  _Branding(scheme: scheme, theme: theme),
                  const SizedBox(height: 32),
                  GlassCard(
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Tizimga kirish',
                            style: theme.textTheme.titleLarge,
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Hisobingiz orqali kirish',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: scheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 24),
                          TextFormField(
                            controller: _usernameController,
                            autocorrect: false,
                            textInputAction: TextInputAction.next,
                            decoration: const InputDecoration(
                              labelText: 'Username',
                              prefixIcon: Icon(Icons.person_outline),
                            ),
                            validator: (v) {
                              final value = (v ?? '').trim();
                              if (value.isEmpty) return 'Usernameni kiriting';
                              if (value.length < 3) return 'Username juda qisqa';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),
                          TextFormField(
                            controller: _passwordController,
                            obscureText: _obscure,
                            textInputAction: TextInputAction.done,
                            onFieldSubmitted: (_) => _submit(),
                            decoration: InputDecoration(
                              labelText: 'Parol',
                              prefixIcon: const Icon(Icons.lock_outline),
                              suffixIcon: IconButton(
                                icon: Icon(_obscure
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined),
                                onPressed: () =>
                                    setState(() => _obscure = !_obscure),
                              ),
                            ),
                            validator: (v) {
                              if ((v ?? '').isEmpty) return 'Parolni kiriting';
                              if ((v ?? '').length < 4) return 'Parol juda qisqa';
                              return null;
                            },
                          ),
                          const SizedBox(height: 8),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: isLoading ? null : () {},
                              child: const Text('Parolni unutdingizmi?'),
                            ),
                          ),
                          const SizedBox(height: 16),
                          _GradientButton(
                            scheme: scheme,
                            onPressed: isLoading ? null : _submit,
                            child: isLoading
                                ? const SizedBox(
                                    width: 22,
                                    height: 22,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.5,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Text('Kirish'),
                          ),
                        ],
                      ),
                    ),
                  )
                      .animate(delay: 250.ms)
                      .fadeIn(duration: 500.ms)
                      .slideY(
                        begin: 0.15,
                        curve: Curves.easeOutCubic,
                        duration: 600.ms,
                      ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Akkauntingiz yo‘qmi?',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: scheme.onSurfaceVariant,
                        ),
                      ),
                      TextButton(
                        onPressed: () => GoRouter.of(context).push('/register'),
                        child: const Text('Ro‘yxatdan o‘tish'),
                      ),
                    ],
                  ).animate(delay: 500.ms).fadeIn(),
                  const SizedBox(height: 24),
                  _TrustBadges().animate(delay: 700.ms).fadeIn(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _Branding extends StatelessWidget {
  final ColorScheme scheme;
  final ThemeData theme;
  const _Branding({required this.scheme, required this.theme});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Hero(
          tag: 'app-logo',
          child: Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [scheme.primary, scheme.tertiary],
              ),
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: scheme.primary.withValues(alpha: 0.35),
                  blurRadius: 28,
                  offset: const Offset(0, 12),
                ),
              ],
            ),
            child: const Icon(Icons.analytics_outlined,
                size: 52, color: Colors.white),
          ),
        ),
        const SizedBox(height: 18),
        Text(
          'UniAnalytics PRO',
          style: theme.textTheme.headlineSmall,
        ).animate().fadeIn(delay: 150.ms, duration: 500.ms),
        const SizedBox(height: 4),
        Text(
          'Talabalar reyting tahlili',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: scheme.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 250.ms, duration: 500.ms),
      ],
    );
  }
}

class _GradientButton extends StatelessWidget {
  final ColorScheme scheme;
  final VoidCallback? onPressed;
  final Widget child;
  const _GradientButton({
    required this.scheme,
    required this.onPressed,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null;
    return AnimatedOpacity(
      duration: const Duration(milliseconds: 200),
      opacity: enabled ? 1.0 : 0.6,
      child: Container(
        height: 56,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [scheme.primary, scheme.tertiary],
          ),
          borderRadius: BorderRadius.circular(18),
          boxShadow: enabled
              ? [
                  BoxShadow(
                    color: scheme.primary.withValues(alpha: 0.4),
                    blurRadius: 18,
                    offset: const Offset(0, 8),
                  ),
                ]
              : null,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(18),
            child: Center(
              child: DefaultTextStyle.merge(
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.2,
                ),
                child: child,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _TrustBadges extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    final items = const [
      (Icons.lock_outline, 'JWT auth'),
      (Icons.shield_outlined, 'TLS shifrlash'),
      (Icons.bolt_outlined, 'Real OLAP'),
    ];
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        for (final (icon, label) in items)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: scheme.surfaceContainerHigh.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: scheme.outlineVariant.withValues(alpha: 0.3),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 14, color: scheme.primary),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: scheme.onSurfaceVariant,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
