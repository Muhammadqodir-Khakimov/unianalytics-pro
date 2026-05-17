import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../core/constants/app_constants.dart';

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService(const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  ));
});

class SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService(this._storage);

  Future<void> setAccessToken(String token) =>
      _storage.write(key: AppConstants.accessTokenKey, value: token);

  Future<String?> getAccessToken() =>
      _storage.read(key: AppConstants.accessTokenKey);

  Future<void> setRefreshToken(String token) =>
      _storage.write(key: AppConstants.refreshTokenKey, value: token);

  Future<String?> getRefreshToken() =>
      _storage.read(key: AppConstants.refreshTokenKey);

  Future<void> setUserJson(String json) =>
      _storage.write(key: AppConstants.userKey, value: json);

  Future<String?> getUserJson() =>
      _storage.read(key: AppConstants.userKey);

  Future<void> clearAll() async {
    await _storage.delete(key: AppConstants.accessTokenKey);
    await _storage.delete(key: AppConstants.refreshTokenKey);
    await _storage.delete(key: AppConstants.userKey);
  }
}
