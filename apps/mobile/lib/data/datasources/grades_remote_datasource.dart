import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/grade.dart';
import '../../domain/entities/paginated.dart';

final gradesRemoteDataSourceProvider = Provider<GradesRemoteDataSource>((ref) {
  return GradesRemoteDataSource(ref.watch(dioClientProvider));
});

class GradesRemoteDataSource {
  final Dio _dio;
  GradesRemoteDataSource(this._dio);

  Future<Paginated<Grade>> list({
    int page = 1,
    int pageSize = 20,
    int? studentId,
    int? subjectId,
    String? semester,
    String? academicYear,
  }) async {
    // Backend `/my/grades` joriy talabaga tegishli baholar (bot/mobile uchun).
    // `/grades` esa admin/dekan uchun — barcha baholar.
    final res = await _dio.get('/my/grades', queryParameters: {
      'page': page,
      'page_size': pageSize,
      // ignore: use_null_aware_elements — map entry null-aware syntax issue
      if (studentId != null) 'student_id': studentId,
      // ignore: use_null_aware_elements
      if (subjectId != null) 'subject_id': subjectId,
      // ignore: use_null_aware_elements
      if (semester != null) 'semester': semester,
      // ignore: use_null_aware_elements
      if (academicYear != null) 'academic_year': academicYear,
    });
    return Paginated.fromJson(
      res.data as Map<String, dynamic>,
      Grade.fromJson,
    );
  }
}
