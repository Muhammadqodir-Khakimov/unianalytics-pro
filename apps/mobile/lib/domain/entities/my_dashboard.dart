import 'package:equatable/equatable.dart';

/// `GET /my/dashboard` — rolga qarab strukturasi farq qiladi.
/// Eng muhim maydonlarni ajratib chiqaramiz; xom JSON ham saqlanadi
/// (UI ehtiyojiga qarab keyinroq foydalanish uchun).
class MyDashboard extends Equatable {
  final String role; // student / teacher / dean / admin
  final bool linked;
  final String? message;

  // Talaba
  final String? studentId;
  final String? studentFullName;
  final String? groupName;
  final int? course;

  // O'qituvchi
  final String? teacherFullName;
  final String? department;
  final String? position;

  // Statistika (umumiy)
  final int? gradesCount;
  final double? avgGrade;
  final double? avgGpa;
  final double? avgAttendance;
  final int? passedCount;
  final int? failedCount;

  // Faqat talaba
  final int? rank;
  final int? rankTotal;

  // Trendlar va kesimlar — UIga xom map sifatida beriladi
  final List<Map<String, dynamic>> gpaTrend;
  final List<Map<String, dynamic>> bySubject;
  final List<Map<String, dynamic>> recentGrades;

  final Map<String, dynamic> raw;

  const MyDashboard({
    required this.role,
    required this.linked,
    this.message,
    this.studentId,
    this.studentFullName,
    this.groupName,
    this.course,
    this.teacherFullName,
    this.department,
    this.position,
    this.gradesCount,
    this.avgGrade,
    this.avgGpa,
    this.avgAttendance,
    this.passedCount,
    this.failedCount,
    this.rank,
    this.rankTotal,
    this.gpaTrend = const [],
    this.bySubject = const [],
    this.recentGrades = const [],
    this.raw = const {},
  });

  factory MyDashboard.fromJson(Map<String, dynamic> json) {
    final stats = (json['stats'] as Map?)?.cast<String, dynamic>() ?? {};
    final student = (json['student'] as Map?)?.cast<String, dynamic>() ?? {};
    final teacher = (json['teacher'] as Map?)?.cast<String, dynamic>() ?? {};
    final rank = (json['rank'] as Map?)?.cast<String, dynamic>() ?? {};

    List<Map<String, dynamic>> mapList(dynamic v) {
      if (v is List) {
        return v
            .whereType<Map>()
            .map((e) => e.cast<String, dynamic>())
            .toList(growable: false);
      }
      return const [];
    }

    // Backend Decimal qiymatlarni JSON string sifatida qaytaradi
    // ("90.63", "3.800"). Avval string, keyin son sifatida parse qilamiz.
    double? toDouble(dynamic v) {
      if (v == null) return null;
      if (v is num) return v.toDouble();
      if (v is String) return double.tryParse(v);
      return null;
    }
    int? toInt(dynamic v) {
      if (v == null) return null;
      if (v is num) return v.toInt();
      if (v is String) return int.tryParse(v);
      return null;
    }

    return MyDashboard(
      role: (json['role'] ?? 'unknown') as String,
      linked: (json['linked'] ?? false) as bool,
      message: json['message'] as String?,
      studentId: student['student_id']?.toString(),
      studentFullName: student['full_name'] as String?,
      groupName: student['group_name'] as String?,
      course: toInt(student['course']),
      teacherFullName: teacher['full_name'] as String?,
      department: teacher['department'] as String?,
      position: teacher['position'] as String?,
      gradesCount: toInt(stats['grades_count'] ?? stats['grades_given']),
      avgGrade: toDouble(stats['avg_grade']),
      avgGpa: toDouble(stats['avg_gpa']),
      avgAttendance: toDouble(stats['avg_attendance']),
      passedCount: toInt(stats['passed_count']),
      failedCount: toInt(stats['failed_count']),
      rank: toInt(rank['rnk']),
      rankTotal: toInt(rank['total']),
      gpaTrend: mapList(json['gpa_trend']),
      bySubject: mapList(json['by_subject']),
      recentGrades: mapList(json['recent_grades']),
      raw: json,
    );
  }

  @override
  List<Object?> get props => [role, linked, avgGpa, rank];
}
