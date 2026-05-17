import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/notification_item.dart';

final notificationsRemoteDataSourceProvider =
    Provider<NotificationsRemoteDataSource>((ref) {
  return NotificationsRemoteDataSource(ref.watch(dioClientProvider));
});

class NotificationsRemoteDataSource {
  final Dio _dio;
  NotificationsRemoteDataSource(this._dio);

  Future<List<NotificationItem>> list({int limit = 50}) async {
    final res = await _dio.get('/notifications', queryParameters: {
      'limit': limit,
    });
    final data = res.data;
    final list = data is List
        ? data
        : (data is Map && data['items'] is List ? data['items'] as List : []);
    return list
        .whereType<Map>()
        .map((e) => NotificationItem.fromJson(e.cast<String, dynamic>()))
        .toList(growable: false);
  }

  Future<void> markRead(int id) =>
      _dio.post('/notifications/$id/read');

  Future<void> markAllRead() => _dio.post('/notifications/mark-all-read');
}
