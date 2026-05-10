// =============================================================================
// Fichier : screens/analyse_screen.dart
// Rôle    : Écran principal. L'étudiant saisit son commentaire, choisit
//           la matière, et obtient l'analyse de sentiment en temps réel.
// =============================================================================

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/commentaire.dart';
import '../widgets/sentiment_card.dart';

const List<String> _matieres = [
  'Mathématiques', 'Informatique', 'Physique', 'Algorithmique',
  'Base de données', 'Réseaux', 'Statistiques',
  'Intelligence artificielle', 'Programmation', 'Autre',
];

class AnalyseScreen extends StatefulWidget {
  const AnalyseScreen({super.key});

  @override
  State<AnalyseScreen> createState() => _AnalyseScreenState();
}

class _AnalyseScreenState extends State<AnalyseScreen> {
  final _controleurTexte = TextEditingController();
  final _formKey          = GlobalKey<FormState>();

  String?      _matiereSelectionnee;
  bool         _chargement = false;
  Commentaire? _resultat;
  String?      _messageErreur;

  @override
  void dispose() {
    _controleurTexte.dispose();
    super.dispose();
  }

  Future<void> _analyser() async {
    if (!_formKey.currentState!.validate()) return;
    FocusScope.of(context).unfocus();

    setState(() {
      _chargement    = true;
      _resultat      = null;
      _messageErreur = null;
    });

    final resultat = await ApiService.analyserCommentaire(
      texte  : _controleurTexte.text.trim(),
      matiere: _matiereSelectionnee,
    );

    setState(() {
      _chargement = false;
      if (resultat != null) {
        _resultat = resultat;
      } else {
        _messageErreur = 'Impossible de joindre l\'API. Vérifiez que le serveur est démarré.';
      }
    });
  }

  void _reinitialiser() {
    setState(() {
      _controleurTexte.clear();
      _matiereSelectionnee = null;
      _resultat            = null;
      _messageErreur       = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        title: const Text('Analyser un commentaire',
            style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1F497D),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_resultat != null || _messageErreur != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Réinitialiser',
              onPressed: _reinitialiser,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // ── Carte de saisie ────────────────────────────────────────────
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('💬 Votre commentaire',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 10),
                      TextFormField(
                        controller: _controleurTexte,
                        maxLines    : 5,
                        maxLength   : 2000,
                        decoration  : InputDecoration(
                          hintText     : 'Ex : Ce cours est excellent, le professeur explique très bien...',
                          hintStyle    : TextStyle(color: Colors.grey.shade400),
                          border       : OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide  : const BorderSide(color: Color(0xFF1F497D), width: 2),
                          ),
                          filled     : true,
                          fillColor  : Colors.white,
                        ),
                        validator: (val) {
                          if (val == null || val.trim().length < 5) {
                            return 'Le commentaire doit contenir au moins 5 caractères.';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 12),

                      // Sélection de la matière
                      const Text('📚 Matière (optionnel)',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value      : _matiereSelectionnee,
                        hint       : const Text('Sélectionner une matière'),
                        isExpanded : true,
                        decoration : InputDecoration(
                          border     : OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                          filled     : true,
                          fillColor  : Colors.white,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        ),
                        items: _matieres.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                        onChanged: (val) => setState(() => _matiereSelectionnee = val),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // ── Bouton analyser ────────────────────────────────────────────
              SizedBox(
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: _chargement ? null : _analyser,
                  icon : _chargement
                      ? const SizedBox(width: 20, height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.psychology, size: 22),
                  label: Text(
                    _chargement ? 'Analyse en cours...' : '🚀 Analyser',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1F497D),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    elevation: 3,
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // ── Résultat ───────────────────────────────────────────────────
              if (_messageErreur != null)
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFE8E8),
                    borderRadius: BorderRadius.circular(12),
                    border: const Border(left: BorderSide(color: Color(0xFFE74C3C), width: 4)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Color(0xFFE74C3C)),
                      const SizedBox(width: 10),
                      Expanded(child: Text(_messageErreur!,
                          style: const TextStyle(color: Color(0xFFB03A2E)))),
                    ],
                  ),
                ),

              if (_resultat != null) ...[
                const Text('📊 Résultat de l\'analyse',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 10),
                SentimentCard(commentaire: _resultat!),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
