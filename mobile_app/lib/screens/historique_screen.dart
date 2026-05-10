// =============================================================================
// Fichier : screens/historique_screen.dart
// Rôle    : Affiche l'historique de tous les commentaires analysés.
//           Permet de filtrer par sentiment et de supprimer un commentaire.
// =============================================================================

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/commentaire.dart';

class HistoriqueScreen extends StatefulWidget {
  const HistoriqueScreen({super.key});

  @override
  State<HistoriqueScreen> createState() => _HistoriqueScreenState();
}

class _HistoriqueScreenState extends State<HistoriqueScreen> {
  List<Commentaire> _commentaires = [];
  bool  _chargement   = false;
  int?  _filtreActif  = null; // null = Tous, 0/1/2 = filtre sentiment

  static const _filtres = [
    {'label': 'Tous',    'value': null,  'emoji': '📋'},
    {'label': 'Positif', 'value': 2,    'emoji': '😊'},
    {'label': 'Neutre',  'value': 1,    'emoji': '😐'},
    {'label': 'Négatif', 'value': 0,    'emoji': '😞'},
  ];

  @override
  void initState() {
    super.initState();
    _charger();
  }

  Future<void> _charger() async {
    setState(() => _chargement = true);
    final data = await ApiService.obtenirCommentaires(
      limite: 100,
      sentiment: _filtreActif,
    );
    setState(() {
      _commentaires = data;
      _chargement   = false;
    });
  }

  Future<void> _supprimer(Commentaire c) async {
    final confirme = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer ce commentaire ?'),
        content: Text(
          '"${c.texteOriginal.length > 80 ? '${c.texteOriginal.substring(0, 80)}...' : c.texteOriginal}"',
          style: const TextStyle(fontStyle: FontStyle.italic),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false),
              child: const Text('Annuler')),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Supprimer', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirme == true) {
      final succes = await ApiService.supprimerCommentaire(c.id);
      if (succes && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Commentaire #${c.id} supprimé'),
            backgroundColor: Colors.green.shade700,
          ),
        );
        _charger();
      }
    }
  }

  Color _couleurSentiment(int s) {
    switch (s) {
      case 0: return const Color(0xFFE74C3C);
      case 1: return const Color(0xFFF1C40F);
      case 2: return const Color(0xFF1F8A70);
      default: return Colors.grey;
    }
  }

  Color _fondSentiment(int s) {
    switch (s) {
      case 0: return const Color(0xFFFFE8E8);
      case 1: return const Color(0xFFFFF9E0);
      case 2: return const Color(0xFFE8F8F0);
      default: return Colors.grey.shade100;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        title: const Text('Historique', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1F497D),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualiser',
            onPressed: _charger,
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Filtres ────────────────────────────────────────────────────────
          Container(
            color: const Color(0xFF1F497D),
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            child: Row(
              children: _filtres.map((f) {
                final actif = _filtreActif == f['value'];
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: ElevatedButton(
                      onPressed: () {
                        setState(() => _filtreActif = f['value'] as int?);
                        _charger();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: actif ? Colors.white : Colors.white24,
                        foregroundColor: actif ? const Color(0xFF1F497D) : Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        elevation: actif ? 2 : 0,
                      ),
                      child: Text('${f['emoji']} ${f['label']}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: actif ? FontWeight.bold : FontWeight.normal,
                          )),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          // ── Compteur ───────────────────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                Text('${_commentaires.length} commentaire(s)',
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
              ],
            ),
          ),

          // ── Liste ──────────────────────────────────────────────────────────
          Expanded(
            child: _chargement
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF1F497D)))
                : _commentaires.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.inbox_outlined, size: 64, color: Colors.grey.shade300),
                            const SizedBox(height: 16),
                            Text('Aucun commentaire trouvé',
                                style: TextStyle(color: Colors.grey.shade500, fontSize: 15)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                        itemCount: _commentaires.length,
                        itemBuilder: (ctx, i) {
                          final c = _commentaires[i];
                          return Dismissible(
                            key: Key('c_${c.id}'),
                            direction: DismissDirection.endToStart,
                            background: Container(
                              alignment: Alignment.centerRight,
                              padding: const EdgeInsets.only(right: 20),
                              margin: const EdgeInsets.symmetric(vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.red.shade400,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(Icons.delete, color: Colors.white, size: 28),
                            ),
                            confirmDismiss: (_) async {
                              await _supprimer(c);
                              return false; // on gère nous-mêmes
                            },
                            child: _carteCommentaire(c),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _carteCommentaire(Commentaire c) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 5),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onLongPress: () => _supprimer(c),
        child: Container(
          decoration: BoxDecoration(
            color: _fondSentiment(c.sentimentPredit),
            borderRadius: BorderRadius.circular(12),
            border: Border(
              left: BorderSide(color: _couleurSentiment(c.sentimentPredit), width: 4),
            ),
          ),
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // En-tête
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(children: [
                    Text(c.emoji, style: const TextStyle(fontSize: 20)),
                    const SizedBox(width: 8),
                    Text(c.labelSentiment,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _couleurSentiment(c.sentimentPredit),
                          fontSize: 14,
                        )),
                  ]),
                  Row(children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: _couleurSentiment(c.sentimentPredit).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text('${(c.scoreConfiance * 100).toStringAsFixed(0)}%',
                          style: TextStyle(
                            fontSize: 12, fontWeight: FontWeight.bold,
                            color: _couleurSentiment(c.sentimentPredit),
                          )),
                    ),
                    const SizedBox(width: 8),
                    Text('#${c.id}', style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
                  ]),
                ],
              ),
              const SizedBox(height: 8),

              // Texte du commentaire
              Text(
                c.texteOriginal,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13, height: 1.4),
              ),
              const SizedBox(height: 8),

              // Pied : matière + date
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  if (c.matiere != null)
                    Row(children: [
                      const Icon(Icons.school, size: 12, color: Colors.grey),
                      const SizedBox(width: 4),
                      Text(c.matiere!,
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 11)),
                    ])
                  else
                    const SizedBox(),
                  Row(children: [
                    const Icon(Icons.access_time, size: 12, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(c.dateFormatee,
                        style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
                  ]),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
