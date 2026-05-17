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

/// Fakultet bo'yicha o'rin (TZ: /my/rank/faculty)
final facultyRankProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  return ref.watch(myRemoteDataSourceProvider).facultyRank();
});

/// Davomat (fan kesimida)
final attendanceProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  return ref.watch(myRemoteDataSourceProvider).attendance();
});

/// Guruh ichida TOP klassmatlar
final topClassmatesProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.watch(myRemoteDataSourceProvider).topClassmates();
});

/// Yaqinlashayotgan imtihonlar
final upcomingExamsProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.watch(myRemoteDataSourceProvider).upcomingExams();
});

/// Kurator/Dekan/Mudir kontaktlari (demo fallback bilan)
final contactsProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final data = await ref.watch(myRemoteDataSourceProvider).contacts();
  Map<String, dynamic> demo(String name, String phone, String email, String role) => {
        'fish': name, 'phone': phone, 'email': email, 'role': role,
      };
  data['kurator'] ??= demo('Karimova Dilshoda Nuriddinovna', '+998 71 200-12-34', 'kurator@univ.uz', 'kurator');
  data['kafedra_mudiri'] ??= demo('Sharipov Akram Rasulovich', '+998 71 200-33-33', 'head@univ.uz', 'kafedra_mudiri');
  data['dekan'] ??= demo('Tursunov Bobur Olimovich', '+998 71 200-22-22', 'dean@univ.uz', 'dekan');
  return data;
});

/// Bildirishnoma/digest sozlamalari
final preferencesProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  return ref.watch(myRemoteDataSourceProvider).preferences();
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
