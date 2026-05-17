import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/settings_provider.dart';
import '../../services/biometric_service.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsControllerProvider);
    final controller = ref.read(settingsControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Sozlamalar')),
      body: ListView(
        children: [
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
