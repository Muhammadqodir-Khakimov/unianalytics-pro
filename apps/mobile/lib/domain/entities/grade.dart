import 'package:equatable/equatable.dart';

class Grade extends Equatable {
  final int id;
  final int studentId;
  final int subjectId;
  final int? teacherId;
  final String? subjectName;
  final String? teacherName;
  final double gradeValue;
  final double? maxValue;
  final double? gpaPoints;
  final bool isPassed;
  final String? assessmentType; // JN, ON, YN, FINAL
  final String? academicYear;
  final String? semester;
  final DateTime? gradeDate;

  const Grade({
    required this.id,
    required this.studentId,
    required this.subjectId,
    required this.gradeValue,
    required this.isPassed,
    this.teacherId,
    this.subjectName,
    this.teacherName,
    this.maxValue,
    this.gpaPoints,
    this.assessmentType,
    this.academicYear,
    this.semester,
    this.gradeDate,
  });

  factory Grade.fromJson(Map<String, dynamic> json) {
    DateTime? parseDate(dynamic v) {
      if (v == null) return null;
      try {
        return DateTime.parse(v.toString());
      } catch (_) {
        return null;
      }
    }

    return Grade(
      id: (json['id'] as num).toInt(),
      studentId: (json['student_id'] as num? ?? 0).toInt(),
      subjectId: (json['subject_id'] as num? ?? 0).toInt(),
      teacherId: (json['teacher_id'] as num?)?.toInt(),
      subjectName: json['subject_name'] as String?,
      teacherName: json['teacher_name'] as String?,
      gradeValue: (json['grade_value'] as num? ?? 0).toDouble(),
      maxValue: (json['max_value'] as num?)?.toDouble(),
      gpaPoints: (json['gpa_points'] as num?)?.toDouble(),
      isPassed: (json['is_passed'] as bool?) ?? false,
      assessmentType: json['assessment_type'] as String?,
      academicYear: json['academic_year'] as String?,
      semester: json['semester'] as String?,
      gradeDate: parseDate(json['grade_date']),
    );
  }

  @override
  List<Object?> get props => [id, gradeValue, gpaPoints, isPassed, gradeDate];
}
