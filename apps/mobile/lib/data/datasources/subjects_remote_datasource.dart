import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/paginated.dart';
import '../../domain/entities/subject.dart';

final subjectsRemoteDataSourceProvider =
    Provider<SubjectsRemoteDataSource>((ref) {
  return SubjectsRemoteDataSource(ref.watch(dioClientProvider));
});

class SubjectsRemoteDataSource {
  final Dio _dio;
  SubjectsRemoteDataSource(this._dio);

  Future<Paginated<Subject>> list({
    int page = 1,
    int pageSize = 50,
  }) async {
    final res = await _dio.get('/subjects', queryParameters: {
      'page': page,
      'page_size': pageSize,
    });
    return Paginated.fromJson(
      res.data as Map<String, dynamic>,
      Subject.fromJson,
    );
  }
}
