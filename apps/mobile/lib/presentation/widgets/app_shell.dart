import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Bottom navigation bilan asosiy shell. Branch state-ni go_router boshqaradi.
class AppShell extends StatelessWidget {
  final StatefulNavigationShell shell;
  final List<ShellTab> tabs;

  const AppShell({super.key, required this.shell, required this.tabs});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: shell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: shell.currentIndex,
        onDestinationSelected: (i) => shell.goBranch(
          i,
          initialLocation: i == shell.currentIndex,
        ),
        destinations: [
          for (final tab in tabs)
            NavigationDestination(
              icon: Icon(tab.icon),
              selectedIcon: Icon(tab.selectedIcon),
              label: tab.label,
            ),
        ],
      ),
    );
  }
}

class ShellTab {
  final IconData icon;
  final IconData selectedIcon;
  final String label;

  const ShellTab({
    required this.icon,
    required this.selectedIcon,
    required this.label,
  });
}
