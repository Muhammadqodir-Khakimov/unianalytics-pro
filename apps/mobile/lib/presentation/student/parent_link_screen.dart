import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/my_remote_datasource.dart';
import '../../providers/data_providers.dart';

/// Talaba uchun: ota-onaning farzandiga bog'lanish so'rovini boshqarish.
/// TZ 4.2.4 — talaba ota-onaning so'rovini ko'rishi va tasdiqlash/rad etishi
/// kerak. Bu sahifa joriy so'rovlar ro'yxatini ham ko'rsatadi.
class ParentLinkScreen extends ConsumerStatefulWidget {
  const ParentLinkScreen({super.key});

  @override
  ConsumerState<ParentLinkScreen> createState() => _ParentLinkScreenState();
}

class _ParentLinkScreenState extends ConsumerState<ParentLinkScreen> {
  final _hemisCtrl = TextEditingController();
  bool _sending = false;
  String? _error;

  @override
  void dispose() {
    _hemisCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final hemis = _hemisCtrl.text.trim();
    if (hemis.isEmpty) {
      setState(() => _error = 'HEMIS ID kiriting');
      return;
    }
    setState(() { _sending = true; _error = null; });
    try {
      await ref.read(myRemoteDataSourceProvider).requestParentLink(hemis);
      _hemisCtrl.clear();
      ref.invalidate(parentLinksProvider);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('✅ So\'rov yuborildi, tasdiqlash kutilmoqda')),
      );
    } catch (e) {
      setState(() => _error = '$e');
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final links = ref.watch(parentLinksProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ota-onani bog\'lash')),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(parentLinksProvider.future),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Icon(Icons.family_restroom, color: theme.colorScheme.primary),
                      const SizedBox(width: 8),
                      Text('Yangi bog\'lanish so\'rovi',
                        style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                    ]),
                    const SizedBox(height: 12),
                    Text(
                      'Ota-onangiz HEMIS ID sini kiriting. Sizning ma\'lumotlaringizni ko\'rish uchun ular siz tomondan tasdiqlanishi kerak bo\'ladi.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _hemisCtrl,
                      decoration: InputDecoration(
                        labelText: 'HEMIS ID',
                        prefixIcon: const Icon(Icons.badge_outlined),
                        border: const OutlineInputBorder(),
                        errorText: _error,
                      ),
                      keyboardType: TextInputType.text,
                    ),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: _sending ? null : _submit,
                      icon: _sending
                          ? const SizedBox(
                              width: 16, height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.send),
                      label: const Text('Bog\'lanish so\'rovi yuborish'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('Joriy so\'rovlar',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            links.when(
              loading: () => const Padding(
                padding: EdgeInsets.all(16),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => Text('Xato: $e'),
              data: (items) {
                if (items.isEmpty) {
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.inbox_outlined),
                      title: const Text('Hozircha so\'rov yo\'q'),
                      subtitle: const Text('Yuqorida yangi so\'rov yuborishingiz mumkin'),
                    ),
                  );
                }
                return Column(children: [
                  for (final l in items)
                    Card(
                      child: ListTile(
                        leading: _statusIcon(l['status']?.toString() ?? '', theme),
                        title: Text(l['student_full_name'] ?? '—'),
                        subtitle: Text('HEMIS: ${l['student_hemis_id']}\nHolat: ${_statusLabel(l['status']?.toString())}'),
                        isThreeLine: true,
                        trailing: Text(
                          _shortDate(l['requested_at']),
                          style: theme.textTheme.labelSmall,
                        ),
                      ),
                    ),
                ]);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusIcon(String status, ThemeData theme) {
    switch (status) {
      case 'approved':
        return Icon(Icons.check_circle, color: theme.colorScheme.primary);
      case 'rejected':
        return Icon(Icons.cancel, color: theme.colorScheme.error);
      case 'revoked':
        return Icon(Icons.block, color: theme.colorScheme.outline);
      default:
        return Icon(Icons.hourglass_top, color: theme.colorScheme.tertiary);
    }
  }

  String _statusLabel(String? s) {
    switch (s) {
      case 'approved': return '✅ Tasdiqlangan';
      case 'rejected': return '❌ Rad etilgan';
      case 'revoked':  return '🔒 Bekor qilingan';
      default:         return '⏳ Tasdiqlash kutilmoqda';
    }
  }

  String _shortDate(dynamic v) {
    if (v is! String) return '';
    return v.substring(0, v.length >= 10 ? 10 : v.length);
  }
}
