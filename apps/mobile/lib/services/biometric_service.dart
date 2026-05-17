import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';

class BiometricService {
  final LocalAuthentication _auth = LocalAuthentication();

  Future<bool> isAvailable() async {
    try {
      final supported = await _auth.isDeviceSupported();
      if (!supported) return false;
      final can = await _auth.canCheckBiometrics;
      return can;
    } on PlatformException {
      return false;
    }
  }

  Future<List<BiometricType>> availableTypes() async {
    try {
      return await _auth.getAvailableBiometrics();
    } on PlatformException {
      return const [];
    }
  }

  Future<bool> authenticate({
    String reason = 'Davom etish uchun shaxsingizni tasdiqlang',
  }) async {
    try {
      return await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false, // PIN/parol fallback ham ruxsat
        ),
      );
    } on PlatformException {
      return false;
    }
  }
}

final biometricServiceProvider =
    Provider<BiometricService>((ref) => BiometricService());
