import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/datasources/my_remote_datasource.dart';
import '../../domain/entities/user.dart';
import '../../providers/auth_provider.dart';
import '../../providers/data_providers.dart';
import '../../providers/settings_provider.dart';
import '../../services/biometric_service.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsControllerProvider);
    final controller = ref.read(settingsControllerProvider.notifier);
    final auth = ref.watch(authControllerProvider);
    final user = auth is Authenticated ? auth.user : null;

    Future<void> handleLogout() async {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Akkauntdan chiqish'),
          content: const Text(
            'Tizimdan chiqishni istaysizmi? Saqlangan ma\'lumotlar tozalanadi.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Bekor qilish'),
            ),
            FilledButton.tonal(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Chiqish'),
            ),
          ],
        ),
      );
      if (confirmed != true) return;
      await ref.read(authControllerProvider.notifier).logout();
      if (!context.mounted) return;
      context.go('/login');
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Sozlamalar')),
      body: ListView(
        children: [
          if (user != null) ...[
            const _SectionHeader('Akkaunt'),
            ListTile(
              leading: CircleAvatar(
                radius: 24,
                backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                child: Text(
                  user.fullName.isEmpty ? '?' : user.fullName[0].toUpperCase(),
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
                ),
              ),
              title: Text(user.fullName.isEmpty ? user.username : user.fullName),
              subtitle: Text('${_roleLabel(user.role)} · ${user.email}'),
            ),
            ListTile(
              leading: const Icon(Icons.logout_outlined),
              title: const Text('Akkauntdan chiqish'),
              subtitle: const Text(
                'Boshqa foydalanuvchi sifatida kirish uchun chiqing',
              ),
              onTap: handleLogout,
            ),
            const Divider(),
          ],
          const _SectionHeader('Ko‘rinish'),
          RadioGroup<ThemeMode>(
            groupValue: settings.themeMode,
            onChanged: (m) => m != null ? controller.setTheme(m) : null,
            child: const Column(
              children: [
                RadioListTile<ThemeMode>(
                  value: ThemeMode.system,
                  title: Text('Tizim'),
                  secondary: Icon(Icons.brightness_auto_outlined),
                ),
                RadioListTile<ThemeMode>(
                  value: ThemeMode.light,
                  title: Text('Yorug‘'),
                  secondary: Icon(Icons.light_mode_outlined),
                ),
                RadioListTile<ThemeMode>(
                  value: ThemeMode.dark,
                  title: Text('Qorong‘i'),
                  secondary: Icon(Icons.dark_mode_outlined),
                ),
              ],
            ),
          ),
          const Divider(),
          const _SectionHeader('Til'),
          RadioGroup<String>(
            groupValue: settings.locale.languageCode,
            onChanged: (l) =>
                l != null ? controller.setLocale(Locale(l)) : null,
            child: const Column(
              children: [
                RadioListTile<String>(
                  value: 'uz',
                  title: Text('O‘zbekcha'),
                ),
                RadioListTile<String>(
                  value: 'ru',
                  title: Text('Русский'),
                ),
                RadioListTile<String>(
                  value: 'en',
                  title: Text('English'),
                ),
              ],
            ),
          ),
          const Divider(),
          const _SectionHeader('Bildirishnomalar'),
          const _PreferencesPanel(),
          const Divider(),
          const _SectionHeader('Xavfsizlik'),
          SwitchListTile(
            secondary: const Icon(Icons.fingerprint),
            title: const Text('Biometrik qulflash'),
            subtitle: const Text(
              'Ilovaga kirishda Touch ID / Face ID / PIN so‘rash',
            ),
            value: settings.biometricEnabled,
            onChanged: (v) async {
              if (v) {
                final ok = await ref
                    .read(biometricServiceProvider)
                    .authenticate(reason: 'Biometrikni yoqish');
                if (!context.mounted) return;
                if (!ok) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Tasdiqlanmadi')),
                  );
                  return;
                }
              }
              await controller.setBiometric(v);
            },
          ),
        ],
      ),
    );
  }
}

class _PreferencesPanel extends ConsumerWidget {
  const _PreferencesPanel();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(preferencesProvider);
    return async.when(
      loading: () => const Padding(
        padding: EdgeInsets.all(16),
        child: LinearProgressIndicator(minHeight: 2),
      ),
      error: (e, _) => ListTile(
        leading: const Icon(Icons.error_outline),
        title: const Text('Yuklab bo\'lmadi'),
        subtitle: Text('$e'),
        trailing: TextButton(
          onPressed: () => ref.invalidate(preferencesProvider),
          child: const Text('Qayta urinish'),
        ),
      ),
      data: (prefs) {
        Future<void> patch(String key, bool value) async {
          await ref.read(myRemoteDataSourceProvider).updatePreferences({key: value});
          ref.invalidate(preferencesProvider);
        }
        return Column(children: [
          SwitchListTile(
            secondary: const Icon(Icons.school_outlined),
            title: const Text('Yangi baho qo\'yilganda'),
            value: prefs['notify_new_grade'] == true,
            onChanged: (v) => patch('notify_new_grade', v),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.warning_amber_outlined),
            title: const Text('Akademik xavf signali'),
            value: prefs['notify_academic_risk'] == true,
            onChanged: (v) => patch('notify_academic_risk', v),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.event_note_outlined),
            title: const Text('Haftalik dayjest'),
            subtitle: const Text('Har juma 18:00 da hisobot'),
            value: prefs['weekly_digest_enabled'] == true,
            onChanged: (v) => patch('weekly_digest_enabled', v),
          ),
        ]);
      },
    );
  }
}


String _roleLabel(UserRole role) {
  switch (role) {
    case UserRole.admin:   return 'Administrator';
    case UserRole.rector:  return 'Rektor';
    case UserRole.dean:    return 'Dekan';
    case UserRole.teacher: return 'O\'qituvchi';
    case UserRole.student: return 'Talaba';
    case UserRole.unknown: return 'Foydalanuvchi';
  }
}


class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(
        text.toUpperCase(),
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.primary,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.8,
        ),
      ),
    );
  }
}
