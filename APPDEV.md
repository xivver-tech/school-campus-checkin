# AppDev — contrôle total

Compte démo : **AppDev** / PIN **9999** (max. 2 comptes appdev).

## Ce que AppDev peut faire (tout)

| Zone | Accès |
|------|--------|
| Pointage GPS (entrée / sortie) | Oui |
| Historique global | Oui |
| Tableau campus | Oui |
| Pointage manuel | Oui |
| Annonces | Oui |
| Canaux de classe (créer, poster, membres) | Oui |
| Créer / désactiver utilisateurs | Oui |
| Export CSV | Oui |
| Forcer sortie de tous | Oui |
| Panneau admin | Oui |
| **Modifier GPS, rayon, horaires, nom d'école** | **Oui (seul)** |
| Contournement des contrôles de rôle | Oui (`require_role` laisse passer AppDev) |

## Différence Admin vs AppDev

- **Admin** : gestion quotidienne (comptes, export, présence). **Ne peut pas** changer les coordonnées GPS ni les horaires verrouillés de Rowad Nahda.
- **AppDev** : même chose **plus** le verrou école (latitude, longitude, rayon, début, fin, retard après, nom).

Dans le code (`rbac.py`) :

```python
if role == "appdev":
    return True  # toute permission
```

## Panneau admin (AppDev)

Après connexion AppDev → **Admin** :

1. Bloc **École — AppDev (contrôle total)** pour GPS / horaires  
2. Ajout d'utilisateurs (tous rôles)  
3. Liste des comptes  
4. Export CSV + lien campus  

## Limite de sécurité

Maximum **2** comptes `appdev` actifs (comme pour admin = 3).  
Ne partagez pas le PIN AppDev avec le personnel ordinaire.
