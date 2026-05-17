import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_client.dart';
import '../../domain/entities/user.dart';

class AuthTokens {
  final String accessToken;
  final String? refreshToken;
  final String tokenType;

  const AuthTokens({
    required this.accessToken,
    this.refreshToken,
    this.tokenType = 'bearer',
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String?,
        tokenType: (json['token_type'] as String?) ?? 'bearer',
      );
}

class LoginResult {
  final AuthTokens tokens;
  final User? user;
  const LoginResult(this.tokens, this.user);
}

final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  return AuthRemoteDataSource(ref.watch(dioClientProvider));
});

class AuthRemoteDataSource {
  final Dio _dio;

  AuthRemoteDataSource(this._dio);

  Future<LoginResult> login({
    required String username,
    required String password,
  }) async {
    // Backend OAuth2PasswordRequestForm kutadi — form-urlencoded, JSON emas.
    final response = await _dio.post(
      '/auth/login',
      data: {'username': username, 'password': password},
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );

    final data = response.data as Map<String, dynamic>;
    final tokens = AuthTokens.fromJson(data);

    // Backend ba'zan login javobida `user` qo'shadi
    final user = data['user'] is Map<String, dynamic>
        ? User.fromJson(data['user'] as Map<String, dynamic>)
        : null;
    return LoginResult(tokens, user);
  }

  Future<User> register({
    required String username,
    required String email,
    required String fullName,
    required String password,
    String role = 'student',
  }) async {
    final response = await _dio.post('/auth/register', data: {
      'username': username,
      'email': email,
      'full_name': fullName,
      'password': password,
      'role': role,
    });
    return User.fromJson(response.data as Map<String, dynamic>);
  }

  Future<User> me() async {
    final response = await _dio.get('/auth/me');
    return User.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    try {
      await _dio.post('/auth/logout');
    } on DioException {
      // Server logout xatosini yutamiz — lokal tokenni baribir tozalaymiz
    }
  }

  Future<AuthTokens> refresh(String refreshToken) async {
    final response = await _dio.post(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    return AuthTokens.fromJson(response.data as Map<String, dynamic>);
  }
}
