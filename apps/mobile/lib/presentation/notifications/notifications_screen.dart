import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/notification_item.dart';
import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(notificationsControllerProvider);
    final controller = ref.read(notificationsControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bildirishnomalar'),
        actions: [
          IconButton(
            tooltip: 'Hammasini o‘qilgan deb belgilash',
            icon: const Icon(Icons.done_all),
            onPressed: () => controller.markAllRead(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => controller.refresh(),
        child: state.when(
          loading: () => const LoadingCenter(),
          error: (e, _) => ErrorRetry(
            message: '$e',
            onRetry: () => controller.refresh(),
          ),
          data: (items) {
            if (items.isEmpty) {
              return const EmptyView(
                icon: Icons.notifications_none_outlined,
                message: 'Hozircha bildirishnomalar yo‘q',
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (_, i) => _NotificationTile(
                item: items[i],
                onTap: () => controller.markRead(items[i].id),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final NotificationItem item;
  final VoidCallback onTap;
  const _NotificationTile({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: ListTile(
        onTap: item.isRead ? null : onTap,
        leading: CircleAvatar(
          backgroundColor: item.isRead
              ? theme.colorScheme.surfaceContainerHigh
              : theme.colorScheme.primaryContainer,
          child: Icon(
            Icons.notifications_outlined,
            color: item.isRead
                ? theme.colorScheme.onSurfaceVariant
                : theme.colorScheme.onPrimaryContainer,
          ),
        ),
        title: Text(
          item.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontWeight: item.isRead ? FontWeight.w500 : FontWeight.w700,
          ),
        ),
        subtitle: item.body != null
            ? Text(item.body!, maxLines: 2, overflow: TextOverflow.ellipsis)
            : null,
        trailing: item.createdAt != null
            ? Text(
                DateFormat('dd.MM HH:mm').format(item.createdAt!.toLocal()),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              )
            : null,
      ),
    );
  }
}
