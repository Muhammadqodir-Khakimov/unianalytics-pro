import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/schedule_item.dart';

final scheduleRemoteDataSourceProvider =
    Provider<ScheduleRemoteDataSource>((ref) {
  return ScheduleRemoteDataSource(ref.watch(dioClientProvider));
});

class ScheduleRemoteDataSource {
  final Dio _dio;
  ScheduleRemoteDataSource(this._dio);

  Future<List<ScheduleItem>> mySchedule() async {
    final res = await _dio.get('/schedule/my');
    final data = res.data;
    final list = data is List
        ? data
        : (data is Map && data['items'] is List ? data['items'] as List : []);
    return list
        .whereType<Map>()
        .map((e) => ScheduleItem.fromJson(e.cast<String, dynamic>()))
        .toList(growable: false);
  }
}
