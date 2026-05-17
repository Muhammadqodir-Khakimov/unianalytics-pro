import 'package:equatable/equatable.dart';

class ScheduleItem extends Equatable {
  final int id;
  final String subjectName;
  final String? teacherName;
  final String? groupName;
  final String? room;
  final int weekday; // 1=Du ... 7=Yak
  final String startTime; // "08:30"
  final String endTime;   // "10:00"
  final String? lessonType; // ma'ruza / amaliy / lab
  final String? academicYear;
  final String? semester;

  const ScheduleItem({
    required this.id,
    required this.subjectName,
    required this.weekday,
    required this.startTime,
    required this.endTime,
    this.teacherName,
    this.groupName,
    this.room,
    this.lessonType,
    this.academicYear,
    this.semester,
  });

  factory ScheduleItem.fromJson(Map<String, dynamic> json) => ScheduleItem(
        id: (json['id'] as num).toInt(),
        subjectName:
            (json['subject_name'] ?? json['subject'] ?? '') as String,
        teacherName:
            (json['teacher_name'] ?? json['teacher']) as String?,
        groupName: (json['group_name'] ?? json['group']) as String?,
        room: json['room'] as String?,
        weekday: (json['weekday'] as num? ?? 1).toInt(),
        startTime: (json['start_time'] ?? '') as String,
        endTime: (json['end_time'] ?? '') as String,
        lessonType: json['lesson_type'] as String?,
        academicYear: json['academic_year'] as String?,
        semester: json['semester'] as String?,
      );

  @override
  List<Object?> get props => [id, weekday, startTime, subjectName];
}
