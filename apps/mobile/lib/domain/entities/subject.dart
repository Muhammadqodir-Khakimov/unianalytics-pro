import 'package:equatable/equatable.dart';

class Subject extends Equatable {
  final int id;
  final String code;
  final String name;
  final int? creditHours;
  final String? subjectType; // mandatory / elective
  final int? semesterNum;
  final String? department;

  const Subject({
    required this.id,
    required this.code,
    required this.name,
    this.creditHours,
    this.subjectType,
    this.semesterNum,
    this.department,
  });

  factory Subject.fromJson(Map<String, dynamic> json) => Subject(
        id: (json['id'] as num).toInt(),
        code: (json['code'] ?? '') as String,
        name: (json['name'] ?? json['subject_name'] ?? '') as String,
        creditHours: (json['credit_hours'] as num?)?.toInt(),
        subjectType: json['subject_type'] as String?,
        semesterNum: (json['semester_num'] as num?)?.toInt(),
        department: json['department'] as String?,
      );

  @override
  List<Object?> get props => [id, code, name];
}
