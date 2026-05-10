import 'package:flutter/material.dart';
import 'screens/analyse_screen.dart';
import 'screens/historique_screen.dart';

void main() {
  runApp(const SentimentApp());
}

class SentimentApp extends StatelessWidget {
  const SentimentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sentiments Étudiants',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F497D),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const AccueilPage(),
    );
  }
}

class AccueilPage extends StatefulWidget {
  const AccueilPage({super.key});

  @override
  State<AccueilPage> createState() => _AccueilPageState();
}

class _AccueilPageState extends State<AccueilPage> {
  int _ongletActif = 0;

  final List<Widget> _ecrans = const [
    AnalyseScreen(),
    HistoriqueScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _ongletActif,
        children: _ecrans,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _ongletActif,
        onDestinationSelected: (i) => setState(() => _ongletActif = i),
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFF1F497D).withOpacity(0.15),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.psychology_outlined),
            selectedIcon: Icon(Icons.psychology, color: Color(0xFF1F497D)),
            label: 'Analyser',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history, color: Color(0xFF1F497D)),
            label: 'Historique',
          ),
        ],
      ),
    );
  }
}
