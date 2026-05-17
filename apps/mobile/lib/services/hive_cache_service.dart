import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_ce_flutter/hive_flutter.dart';

/// Offline cache uchun yengil JSON kalit-qiymat xizmati.
/// Hive boxlari `cache_<box>` shaklida nomlanadi. Har bir yozuv:
/// `{"data": <json>, "ts": <millis>}` — TTL tekshirish uchun.
class HiveCacheService {
  static const String _boxName = 'app_cache_v1';

  Box<String>? _box;

  Future<void> init() async {
    await Hive.initFlutter();
    _box = await Hive.openBox<String>(_boxName);
  }

  Box<String> get _b {
    final box = _box;
    if (box == null) {
      throw StateError('HiveCacheService init() chaqirilmagan');
    }
    return box;
  }

  Future<void> put(String key, Map<String, dynamic> json) async {
    final wrapper = {
      'data': json,
      'ts': DateTime.now().millisecondsSinceEpoch,
    };
    await _b.put(key, jsonEncode(wrapper));
  }

  /// `maxAge` o'tib ketgan bo'lsa `null` qaytaradi.
  Map<String, dynamic>? get(String key, {Duration? maxAge}) {
    final raw = _b.get(key);
    if (raw == null) return null;
    try {
      final wrapper = jsonDecode(raw) as Map<String, dynamic>;
      if (maxAge != null) {
        final ts = (wrapper['ts'] as num?)?.toInt() ?? 0;
        final age = DateTime.now().millisecondsSinceEpoch - ts;
        if (age > maxAge.inMilliseconds) return null;
      }
      return (wrapper['data'] as Map).cast<String, dynamic>();
    } catch (_) {
      return null;
    }
  }

  Future<void> remove(String key) => _b.delete(key);
  Future<void> clear() => _b.clear();
}

final hiveCacheProvider = Provider<HiveCacheService>((ref) {
  throw UnimplementedError(
    'hiveCacheProvider main.dart ichida override qilinishi kerak',
  );
});
