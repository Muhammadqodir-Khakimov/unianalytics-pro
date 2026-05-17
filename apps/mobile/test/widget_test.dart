import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:unianalytics_mobile/main.dart';

void main() {
  testWidgets('App boots and shows splash screen', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: UniAnalyticsApp()));

    // Splash da app nomi ko'rinadi
    expect(find.text('UniAnalytics PRO'), findsOneWidget);
    expect(find.byIcon(Icons.analytics_outlined), findsOneWidget);
  });
}
