import 'package:equatable/equatable.dart';

class NotificationItem extends Equatable {
  final int id;
  final String title;
  final String? body;
  final String? type;
  final bool isRead;
  final DateTime? createdAt;

  const NotificationItem({
    required this.id,
    required this.title,
    required this.isRead,
    this.body,
    this.type,
    this.createdAt,
  });

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    DateTime? parseDate(dynamic v) {
      if (v == null) return null;
      try {
        return DateTime.parse(v.toString());
      } catch (_) {
        return null;
      }
    }

    return NotificationItem(
      id: (json['id'] as num).toInt(),
      title: (json['title'] ?? '') as String,
      body: (json['body'] ?? json['message']) as String?,
      type: json['type'] as String?,
      isRead: (json['is_read'] as bool?) ?? false,
      createdAt: parseDate(json['created_at']),
    );
  }

  @override
  List<Object?> get props => [id, isRead, createdAt];
}
