// =============================================================================
// Fichier : services/api_service.dart
// Rôle    : Service de communication avec l'API FastAPI.
//           Centralise tous les appels HTTP. L'URL 10.0.2.2 correspond à
//           localhost du PC hôte depuis l'émulateur Android.
// =============================================================================

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/commentaire.dart';

class ApiService {
  // 10.0.2.2 = localhost de l'ordinateur hôte vu depuis l'émulateur Android
  // Remplace par l'IP locale (ex: 192.168.1.X) pour un vrai téléphone
  static const String _baseUrl = 'http://10.0.2.2:8000/api';
  static const Duration _timeout = Duration(seconds: 30);

  // ── Analyser un commentaire ─────────────────────────────────────────────────
  static Future<Commentaire?> analyserCommentaire({
    required String texte,
    String? matiere,
  }) async {
    try {
      final body = <String, dynamic>{'texte': texte};
      if (matiere != null && matiere.isNotEmpty) {
        body['matiere'] = matiere;
      }
      final reponse = await http
          .post(
            Uri.parse('$_baseUrl/predict'),
            headers: {'Content-Type': 'application/json; charset=utf-8'},
            body: jsonEncode(body),
          )
          .timeout(_timeout);

      if (reponse.statusCode == 200) {
        final json = jsonDecode(utf8.decode(reponse.bodyBytes)) as Map<String, dynamic>;
        return Commentaire.fromJson(json);
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  // ── Récupérer la liste des commentaires ─────────────────────────────────────
  static Future<List<Commentaire>> obtenirCommentaires({
    int limite = 50,
    int? sentiment,
    String? matiere,
  }) async {
    try {
      final params = <String, String>{'limite': '$limite'};
      if (sentiment != null) params['sentiment'] = '$sentiment';
      if (matiere != null && matiere.isNotEmpty) params['matiere'] = matiere;

      final uri = Uri.parse('$_baseUrl/commentaires').replace(queryParameters: params);
      final reponse = await http.get(uri).timeout(_timeout);

      if (reponse.statusCode == 200) {
        final json = jsonDecode(utf8.decode(reponse.bodyBytes)) as Map<String, dynamic>;
        final liste = json['commentaires'] as List<dynamic>;
        return liste.map((e) => Commentaire.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  // ── Récupérer les statistiques ──────────────────────────────────────────────
  static Future<Map<String, dynamic>?> obtenirStats() async {
    try {
      final reponse = await http
          .get(Uri.parse('$_baseUrl/stats'))
          .timeout(_timeout);
      if (reponse.statusCode == 200) {
        return jsonDecode(utf8.decode(reponse.bodyBytes)) as Map<String, dynamic>;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  // ── Supprimer un commentaire ────────────────────────────────────────────────
  static Future<bool> supprimerCommentaire(int id) async {
    try {
      final reponse = await http
          .delete(Uri.parse('$_baseUrl/commentaires/$id'))
          .timeout(_timeout);
      return reponse.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Vérifier la connexion à l'API ───────────────────────────────────────────
  static Future<bool> verifierConnexion() async {
    try {
      final reponse = await http
          .get(Uri.parse('http://10.0.2.2:8000/health'))
          .timeout(const Duration(seconds: 5));
      return reponse.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
