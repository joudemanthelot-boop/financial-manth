# Agent Financial Manth IA

Agent d'analyse financière pour TPE du cabinet **Manthelot Associés**, construit avec le
[Mistral Agents SDK](https://docs.mistral.ai).

## Fonctionnement

1. **À chaque appel**, l'agent charge automatiquement le skill Registry
   `financial-manth-ia` (id `01a1ccc2-eebc-7360-8812-2d2431d5c837`, version 7) et suit sa
   méthode : collecte, extraction et validation des données comptables, calculs
   déterministes, contrôles, diagnostic en 4 catégories, comparaison N/N-1, livrable final
   (page HTML autonome au logo « Manthelot Associés », ou rapport Markdown + JSON).
2. **Fin d'analyse** : l'agent propose d'être mis en relation avec le cabinet pour un
   conseil personnalisé.
3. **Si l'utilisateur accepte** : il demande son nom, son numéro de téléphone et l'objet de
   sa demande, puis envoie une notification par e-mail (connecteur Gmail) à
   `joude.manthelot@gmail.com` — le dirigeant, joignable au +33 7 52 34 42 97.
   La notification contient uniquement nom / téléphone / objet, jamais les données financières.

## Prérequis

- Python 3.12+
- Une clé `MISTRAL_API_KEY` (workflows activés) pour l'exécution locale ou `agents serve`
- Le skill `financial-manth-ia` partagé avec le workspace (fait)
- Le connecteur **Gmail** connecté par l'utilisateur qui lance la session

## Lancer localement

```bash
uv sync
export MISTRAL_API_KEY="..."
uv run main.py
```

Ou en worker durable : `uv run agents serve`.

## Déployer (agent managé Mistral)

```bash
git init && git add . && git commit -m "Agent Financial Manth IA"
git remote add origin git@github.com:<org>/<repo>.git && git push -u origin main
uv run agents deploy
```

Le déploiement crée un déploiement managé Workflows ; l'agent est enregistré comme workflow
sous le nom `financial-manth-ia` et devient appelable en permanence.

## Variables / configuration

| Élément | Valeur par défaut | Variable d'environnement |
| --- | --- | --- |
| E-mail de notification | `joude.manthelot@gmail.com` | `FINANCIAL_MANTH_NOTIFY_EMAIL` |
| Téléphone du cabinet | +33 7 52 34 42 97 | constantes dans `main.py` |
| Skill Registry | `01a1ccc2-eebc-7360-8812-2d2431d5c837` v7 | constantes dans `main.py` |
