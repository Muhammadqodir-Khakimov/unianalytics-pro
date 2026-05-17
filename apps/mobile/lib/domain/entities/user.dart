import 'package:equatable/equatable.dart';

/// Foydalanuvchi rollari — backend `UserRole` enum bilan mos.
enum UserRole {
  admin,
  rector,
  dean,
  teacher,
  student,
  unknown;

  static UserRole fromString(String? value) {
    if (value == null) return UserRole.unknown;
    return UserRole.values.firstWhere(
      (r) => r.name == value.toLowerCase(),
      orElse: () => UserRole.unknown,
    );
  }
}

class User extends Equatable {
  final String id;
  final String username;
  final String email;
  final String fullName;
  final UserRole role;
  final bool isActive;
  final int? telegramId;

  const User({
    required this.id,
    required this.username,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isActive,
    this.telegramId,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'].toString(),
      username: (json['username'] ?? '') as String,
      email: json['email'] as String? ?? '',
      fullName: (json['full_name'] ?? json['fullName'] ?? '') as String,
      role: UserRole.fromString(json['role'] as String?),
      isActive: (json['is_active'] ?? json['isActive'] ?? true) as bool,
      telegramId: json['telegram_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'username': username,
        'email': email,
        'full_name': fullName,
        'role': role.name,
        'is_active': isActive,
        'telegram_id': telegramId,
      };

  @override
  List<Object?> get props =>
      [id, username, email, fullName, role, isActive, telegramId];
}
