import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/user.dart';
import '../../providers/auth_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(authControllerProvider);
    final user = state is Authenticated ? state.user : null;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Profil')),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 16),
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: theme.colorScheme.primaryContainer,
                      child: Icon(
                        Icons.person_outline,
                        size: 40,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      user?.fullName ?? '—',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Text(
                      user?.email ?? '',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.secondaryContainer,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        user?.role.name.toUpperCase() ?? '—',
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: theme.colorScheme.onSecondaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          ListTile(
            leading: const Icon(Icons.person_outline),
            title: const Text('Username'),
            subtitle: Text(user?.username ?? '—'),
          ),
          if (user != null) ..._roleActions(context, user.role),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: const Text('Sozlamalar'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => GoRouter.of(context).push('/settings'),
          ),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('Ilova haqida'),
            subtitle: const Text('UniAnalytics PRO • v1.0.0'),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'UniAnalytics PRO',
                applicationVersion: '1.0.0',
                applicationLegalese: 'Talabalar reyting tahlili (BMI)',
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: Icon(Icons.logout, color: theme.colorScheme.error),
            title: Text(
              'Chiqish',
              style: TextStyle(color: theme.colorScheme.error),
            ),
            onTap: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Chiqish'),
                  content: const Text(
                      'Akkauntdan chiqishni xohlaysizmi?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      child: const Text('Bekor qilish'),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.of(ctx).pop(true),
                      child: const Text('Chiqish'),
                    ),
                  ],
                ),
              );
              if (ok == true) {
                await ref.read(authControllerProvider.notifier).logout();
              }
            },
          ),
        ],
      ),
    );
  }

  /// Rol-aware tezkor amallar — har bir foydalanuvchi o'z vazifalariga
  /// to'g'ridan-to'g'ri kira oladi.
  List<Widget> _roleActions(BuildContext context, UserRole role) {
    Widget tile(IconData icon, String title, String subtitle, String route) =>
        ListTile(
          leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
          title: Text(title),
          subtitle: Text(subtitle, maxLines: 1, overflow: TextOverflow.ellipsis),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => GoRouter.of(context).push(route),
        );

    switch (role) {
      case UserRole.student:
        return [
          tile(Icons.family_restroom, 'Ota-onani bog\'lash',
              'HEMIS ID orqali so\'rov yuborish', '/parent-link'),
          tile(Icons.menu_book_outlined, 'Mening baholarim',
              'Fanlar bo\'yicha barcha baholar', '/grades'),
          tile(Icons.event_available_outlined, 'Davomat tafsiloti',
              'Har fan bo\'yicha qatnashish', '/extras'),
        ];
      case UserRole.teacher:
        return [
          tile(Icons.people_outline, 'Mening talabalarim',
              'Talabalar ro\'yxati, GPA, davomat', '/teacher/students'),
          tile(Icons.groups_outlined, 'Mening guruhlarim',
              'Bilgan guruhlar', '/teacher/groups'),
          tile(Icons.menu_book_outlined, 'Mening fanlarim',
              'O\'qitilayotgan fanlar', '/teacher/subjects'),
          tile(Icons.edit_note_outlined, 'Baho qo\'yish',
              'Tezkor baho kiritish formasi', '/teacher/grade-entry'),
        ];
      case UserRole.dean:
        return [
          tile(Icons.people_outline, 'Talabalar ro\'yxati',
              'Fakultet talabalari', '/teacher/students'),
          tile(Icons.warning_amber_outlined, 'Akademik xavf',
              'GPA < 2.0 talabalar', '/extras'),
          tile(Icons.bar_chart_outlined, 'Fakultet hisoboti',
              'Yo\'nalish va kurs kesimida', '/dashboard'),
        ];
      case UserRole.admin:
        return [
          tile(Icons.people_outline, 'Barcha talabalar',
              'Universitet darajasida', '/teacher/students'),
          tile(Icons.school_outlined, 'TOP fakultetlar',
              'GPA bo\'yicha reyting', '/dashboard'),
          tile(Icons.warning_amber_outlined, 'Risk talabalar',
              'Tezkor monitoring', '/extras'),
          tile(Icons.bar_chart_outlined, 'Tahliliy panel',
              'Universitet bo\'yicha KPI', '/dashboard'),
        ];
      case UserRole.rector:
        return [
          tile(Icons.school_outlined, 'TOP fakultetlar',
              'Rektorat tahlili', '/dashboard'),
          tile(Icons.bar_chart_outlined, 'Universitet KPI',
              'Strategik ko\'rsatkichlar', '/dashboard'),
        ];
      case UserRole.unknown:
        return [];
    }
  }
}
