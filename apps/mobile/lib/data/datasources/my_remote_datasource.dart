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
}
