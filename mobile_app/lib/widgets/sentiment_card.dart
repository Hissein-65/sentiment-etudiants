// =============================================================================
// Fichier : widgets/sentiment_card.dart
// Rôle    : Widget réutilisable affichant le résultat d'une analyse
//           de sentiment avec couleur, emoji, label et barres de scores.
// =============================================================================

import 'package:flutter/material.dart';
import '../models/commentaire.dart';

class SentimentCard extends StatelessWidget {
  final Commentaire commentaire;

  const SentimentCard({super.key, required this.commentaire});

  // Couleurs selon le sentiment
  Color get _couleurPrimaire {
    switch (commentaire.sentimentPredit) {
      case 0: return const Color(0xFFE74C3C);
      case 1: return const Color(0xFFF1C40F);
      case 2: return const Color(0xFF1F8A70);
      default: return Colors.grey;
    }
  }

  Color get _couleurFond {
    switch (commentaire.sentimentPredit) {
      case 0: return const Color(0xFFFFE8E8);
      case 1: return const Color(0xFFFFF9E0);
      case 2: return const Color(0xFFE8F8F0);
      default: return Colors.grey.shade100;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          color: _couleurFond,
          borderRadius: BorderRadius.circular(16),
          border: Border(left: BorderSide(color: _couleurPrimaire, width: 5)),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête : emoji + label
            Row(
              children: [
                Text(commentaire.emoji, style: const TextStyle(fontSize: 40)),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      commentaire.labelSentiment,
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: _couleurPrimaire,
                      ),
                    ),
                    Text(
                      'Confiance : ${(commentaire.scoreConfiance * 100).toStringAsFixed(1)}%',
                      style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 12),

            // Barres de scores
            _barreScore('😞 Négatif',  commentaire.scores['negatif'] ?? 0, const Color(0xFFE74C3C)),
            const SizedBox(height: 10),
            _barreScore('😐 Neutre',   commentaire.scores['neutre']  ?? 0, const Color(0xFFF1C40F)),
            const SizedBox(height: 10),
            _barreScore('😊 Positif',  commentaire.scores['positif'] ?? 0, const Color(0xFF1F8A70)),

            if (commentaire.matiere != null) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.school, size: 16, color: Colors.grey),
                  const SizedBox(width: 6),
                  Text(
                    'Matière : ${commentaire.matiere}',
                    style: TextStyle(color: Colors.grey.shade700, fontSize: 13),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _barreScore(String label, double score, Color couleur) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
            Text(
              '${(score * 100).toStringAsFixed(1)}%',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: couleur),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: score,
            minHeight: 10,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(couleur),
          ),
        ),
      ],
    );
  }
}
