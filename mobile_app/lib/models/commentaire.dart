// =============================================================================
// Fichier : models/commentaire.dart
// Rôle    : Modèle de données représentant un commentaire analysé.
//           Correspond exactement à la structure JSON retournée par l'API.
// =============================================================================

class Commentaire {
  final int id;
  final String texteOriginal;
  final String? matiere;
  final int sentimentPredit;
  final String labelSentiment;
  final Map<String, double> scores;
  final String? dateCreation;

  const Commentaire({
    required this.id,
    required this.texteOriginal,
    this.matiere,
    required this.sentimentPredit,
    required this.labelSentiment,
    required this.scores,
    this.dateCreation,
  });

  /// Construit un Commentaire depuis un Map JSON reçu de l'API
  factory Commentaire.fromJson(Map<String, dynamic> json) {
    final scoresJson = json['scores'] as Map<String, dynamic>? ?? {};
    return Commentaire(
      id              : json['id'] as int,
      texteOriginal   : json['texte_original'] as String,
      matiere         : json['matiere'] as String?,
      sentimentPredit : json['sentiment_predit'] as int,
      labelSentiment  : json['label_sentiment'] as String,
      scores          : {
        'negatif': (scoresJson['negatif'] as num?)?.toDouble() ?? 0.0,
        'neutre' : (scoresJson['neutre']  as num?)?.toDouble() ?? 0.0,
        'positif': (scoresJson['positif'] as num?)?.toDouble() ?? 0.0,
      },
      dateCreation: json['date_creation'] as String?,
    );
  }

  /// Emoji correspondant au sentiment prédit
  String get emoji {
    switch (sentimentPredit) {
      case 0: return '😞';
      case 1: return '😐';
      case 2: return '😊';
      default: return '❓';
    }
  }

  /// Score de la classe prédite (entre 0 et 1)
  double get scoreConfiance {
    switch (sentimentPredit) {
      case 0: return scores['negatif'] ?? 0.0;
      case 1: return scores['neutre']  ?? 0.0;
      case 2: return scores['positif'] ?? 0.0;
      default: return 0.0;
    }
  }

  /// Date formatée lisible (ex: "10/05/2026 22:07")
  String get dateFormatee {
    if (dateCreation == null) return '—';
    try {
      final dt = DateTime.parse(dateCreation!);
      return '${dt.day.toString().padLeft(2,'0')}/${dt.month.toString().padLeft(2,'0')}/${dt.year} '
             '${dt.hour.toString().padLeft(2,'0')}:${dt.minute.toString().padLeft(2,'0')}';
    } catch (_) {
      return dateCreation!.substring(0, 16).replaceAll('T', ' ');
    }
  }
}
