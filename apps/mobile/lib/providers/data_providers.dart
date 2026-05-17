import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/datasources/grades_remote_datasource.dart';
import '../data/datasources/my_remote_datasource.dart';
import '../data/datasources/notifications_remote_datasource.dart';
import '../data/datasources/schedule_remote_datasource.dart';
import '../data/datasources/subjects_remote_datasource.dart';
import '../domain/entities/grade.dart';
import '../domain/entities/my_dashboard.dart';
import '../domain/entities/notification_item.dart';
import '../domain/entities/paginated.dart';
import '../domain/entities/schedule_item.dart';
import '../domain/entities/subject.dart';
import '../services/hive_cache_service.dart';

/// Dashboard ma'lumotlari — offline-first: kechiktirilgan tarmoqdan
/// avval cache'dan ko'rsatadi, keyin tarmoq javobi bilan yangilaydi.
final myDashboardProvider =
    FutureProvider.autoDispose<MyDashboard>((ref) async {
  final cache = ref.watch(hiveCacheProvider);
  final remote = ref.watch(myRemoteDataSourceProvider);

  try {
    final data = await remote.dashboard();
    await cache.put('my_dashboard', data.raw);
    return data;
  } catch (e) {
    // Tarmoq xatosi — cache'dan o'qishga harakat (3 kungacha eski bo'lsa ham)
    final cached = cache.get('my_dashboard', maxAge: const Duration(days: 3));
    if (cached != null) {
      return MyDashboard.fromJson(cached);
    }
    rethrow;
  }
});

/// Baholar — birinchi sahifa (paginatsiya keyingi bosqichda).
final myGradesProvider =
    FutureProvider.autoDispose<Paginated<Grade>>((ref) async {
  return ref.watch(gradesRemoteDataSourceProvider).list(page: 1, pageSize: 50);
});

final subjectsProvider =
    FutureProvider.autoDispose<Paginated<Subject>>((ref) async {
  return ref.watch(subjectsRemoteDataSourceProvider).list(pageSize: 100);
});

final myScheduleProvider =
    FutureProvider.autoDispose<List<ScheduleItem>>((ref) async {
  return ref.watch(scheduleRemoteDataSourceProvider).mySchedule();
});

/// Bildirishnomalar — `NotificationsController` orqali read holatini boshqaramiz.
final notificationsControllerProvider = StateNotifierProvider.autoDispose<
    NotificationsController, AsyncValue<List<NotificationItem>>>((ref) {
  return NotificationsController(
    ref.watch(notificationsRemoteDataSourceProvider),
  );
});

class NotificationsController
    extends StateNotifier<AsyncValue<List<NotificationItem>>> {
  final NotificationsRemoteDataSource _remote;

  NotificationsController(this._remote) : super(const AsyncValue.loading()) {
    refresh();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      state = AsyncValue.data(await _remote.list());
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> markRead(int id) async {
    await _remote.markRead(id);
    state.whenData((items) {
      state = AsyncValue.data([
        for (final n in items)
          if (n.id == id)
            NotificationItem(
              id: n.id,
              title: n.title,
              body: n.body,
              type: n.type,
              isRead: true,
              createdAt: n.createdAt,
            )
          else
            n,
      ]);
    });
  }

  Future<void> markAllRead() async {
    await _remote.markAllRead();
    state.whenData((items) {
      state = AsyncValue.data([
        for (final n in items)
          NotificationItem(
            id: n.id,
            title: n.title,
            body: n.body,
            type: n.type,
            isRead: true,
            createdAt: n.createdAt,
          ),
      ]);
    });
  }
}
