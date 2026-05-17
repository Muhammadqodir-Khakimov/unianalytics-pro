import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';

/// O'qituvchi guruhlari (placeholder — backendda /teachers/me/groups endpointi
/// keyingi iteratsiyada qo'shilishi mumkin). Hozircha dashboard'dagi
/// `recent_grades` dan studentlarning guruhlarini ko'rsatadi.
class MyGroupsScreen extends ConsumerWidget {
  const MyGroupsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(myDashboardProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Mening guruhlarim')),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(myDashboardProvider.future),
        child: async.when(
          loading: () => const LoadingCenter(),
          error: (e, _) => ErrorRetry(
            message: '$e',
            onRetry: () => ref.invalidate(myDashboardProvider),
          ),
          data: (data) => const EmptyView(
            icon: Icons.groups_outlined,
            message: 'Guruhlar API endpointi keyingi versiyada qo‘shiladi',
          ),
        ),
      ),
    );
  }
}
