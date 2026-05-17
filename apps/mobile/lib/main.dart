import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/constants/app_constants.dart';
import 'providers/settings_provider.dart';
import 'routing/app_router.dart';
import 'services/hive_cache_service.dart';
import 'theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cache = HiveCacheService();
  await cache.init();

  runApp(
    ProviderScope(
      overrides: [hiveCacheProvider.overrideWithValue(cache)],
      child: const UniAnalyticsApp(),
    ),
  );
}

class UniAnalyticsApp extends ConsumerWidget {
  const UniAnalyticsApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final settings = ref.watch(settingsControllerProvider);

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: settings.themeMode,
      locale: settings.locale,
      routerConfig: router,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('uz'),
        Locale('ru'),
        Locale('en'),
      ],
    );
  }
}
