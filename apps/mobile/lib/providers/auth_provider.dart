import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/datasources/auth_remote_datasource.dart';
import '../domain/entities/user.dart';
import '../services/secure_storage_service.dart';

sealed class AuthState {
  const AuthState();
}

class AuthInitial extends AuthState {
  const AuthInitial();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class Authenticated extends AuthState {
  final User user;
  const Authenticated(this.user);
}

class Unauthenticated extends AuthState {
  final String? message;
  const Unauthenticated({this.message});
}

class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(
    ref.watch(authRemoteDataSourceProvider),
    ref.watch(secureStorageProvider),
  );
});

class AuthController extends StateNotifier<AuthState> {
  final AuthRemoteDataSource _remote;
  final SecureStorageService _storage;

  AuthController(this._remote, this._storage) : super(const AuthInitial());

  /// App boshlanganda — saqlangan tokenni tekshirib, kerak bo'lsa `/auth/me`
  /// dan foydalanuvchini olib keladi.
  Future<void> bootstrap() async {
    state = const AuthLoading();
    final token = await _storage.getAccessToken();
    if (token == null || token.isEmpty) {
      state = const Unauthenticated();
      return;
    }
    try {
      final user = await _remote.me();
      await _storage.setUserJson(jsonEncode(user.toJson()));
      state = Authenticated(user);
    } catch (_) {
      await _storage.clearAll();
      state = const Unauthenticated();
    }
  }

  Future<void> login({
    required String username,
    required String password,
  }) async {
    state = const AuthLoading();
    try {
      final result =
          await _remote.login(username: username, password: password);
      await _storage.setAccessToken(result.tokens.accessToken);
      if (result.tokens.refreshToken != null) {
        await _storage.setRefreshToken(result.tokens.refreshToken!);
      }
      final user = result.user ?? await _remote.me();
      await _storage.setUserJson(jsonEncode(user.toJson()));
      state = Authenticated(user);
    } catch (e) {
      state = AuthError(_extractMessage(e));
    }
  }

  Future<bool> register({
    required String username,
    required String email,
    required String fullName,
    required String password,
  }) async {
    state = const AuthLoading();
    try {
      await _remote.register(
        username: username,
        email: email,
        fullName: fullName,
        password: password,
      );
      // Avto-login
      await login(username: username, password: password);
      return state is Authenticated;
    } catch (e) {
      state = AuthError(_extractMessage(e));
      return false;
    }
  }

  Future<void> logout() async {
    state = const AuthLoading();
    await _remote.logout();
    await _storage.clearAll();
    state = const Unauthenticated();
  }

  String _extractMessage(Object e) {
    final s = e.toString();
    return s.length > 200 ? '${s.substring(0, 200)}…' : s;
  }
}
