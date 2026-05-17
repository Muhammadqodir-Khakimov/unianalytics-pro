import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/my_dashboard.dart';

final myRemoteDataSourceProvider = Provider<MyRemoteDataSource>((ref) {
  return MyRemoteDataSource(ref.watch(dioClientProvider));
});

class MyRemoteDataSource {
  final Dio _dio;
  MyRemoteDataSource(this._dio);

  Future<MyDashboard> dashboard() async {
    final res = await _dio.get('/my/dashboard');
    return MyDashboard.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> facultyRank() async {
    final res = await _dio.get('/my/rank/faculty');
    return (res.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> attendance() async {
    final res = await _dio.get('/my/attendance');
    return (res.data as Map).cast<String, dynamic>();
  }

  Future<List<Map<String, dynamic>>> topClassmates({int limit = 10}) async {
    final res = await _dio.get(
      '/my/top-classmates',
      queryParameters: {'limit': limit},
    );
    final data = (res.data as Map).cast<String, dynamic>();
    final items = (data['items'] as List? ?? [])
        .whereType<Map>()
        .map((m) => m.cast<String, dynamic>())
        .toList();
    return items;
  }

  Future<List<Map<String, dynamic>>> upcomingExams({int limit = 10}) async {
    final res = await _dio.get(
      '/my/exams/upcoming',
      queryParameters: {'limit': limit},
    );
    final data = (res.data as Map).cast<String, dynamic>();
    final items = (data['items'] as List? ?? [])
        .whereType<Map>()
        .map((m) => m.cast<String, dynamic>())
        .toList();
    return items;
  }

  Future<Map<String, dynamic>> contacts() async {
    final res = await _dio.get('/my/contacts');
    return (res.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> preferences() async {
    final res = await _dio.get('/users/me/preferences');
    return (res.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> updatePreferences(
    Map<String, dynamic> patch,
  ) async {
    final res = await _dio.patch('/users/me/preferences', data: patch);
    return (res.data as Map).cast<String, dynamic>();
  }

  // ---- Teacher / Dean / Admin: students list ----
  Future<List<Map<String, dynamic>>> students({int limit = 50}) async {
    final res = await _dio.get('/my/students', queryParameters: {'limit': limit});
    final data = (res.data as Map).cast<String, dynamic>();
    return (data['items'] as List? ?? [])
        .whereType<Map>()
        .map((m) => m.cast<String, dynamic>())
        .toList();
  }

  // ---- Student: parent link ----
  Future<Map<String, dynamic>> requestParentLink(String hemisId, {String? note}) async {
    final res = await _dio.post('/bot/link-parent', data: {
      'talaba_hemis_id': hemisId,
      if (note != null) 'note': note,
    });
    return (res.data as Map).cast<String, dynamic>();
  }

  Future<List<Map<String, dynamic>>> parentLinks() async {
    final res = await _dio.get('/bot/parent-links');
    return (res.data as List? ?? [])
        .whereType<Map>()
        .map((m) => m.cast<String, dynamic>())
        .toList();
  }
}
