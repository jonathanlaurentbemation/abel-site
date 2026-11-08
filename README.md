# Site abel.be

Site statique d'ABEL, hébergé sur Cloudflare (Worker `abel-site`), alimenté par Airtable.

## Comment ça marche

1. Les références (projets réalisés) vivent dans Airtable : base **ABEL Community Management**, table **Références**. Seules les fiches cochées **Publié** apparaissent sur le site.
2. GitHub Actions (`.github/workflows/publier.yml`) lit Airtable, télécharge et réduit les photos, génère toutes les pages et déploie sur Cloudflare.
3. La publication se lance :
   - automatiquement chaque nuit ;
   - à la demande : onglet **Actions** > **Publier abel.be** > **Run workflow** ;
   - à chaque modification de ce dépôt.

## Ajouter une référence

Dans Airtable, nouvelle ligne : Titre (ex. « Soignies - École »), Ville, Projet, Description, intervenants, Catégories, Vignette (1 photo), Galerie (les photos de la fiche), puis cocher **Publié**. Laisser **Slug** vide : il est créé à partir du titre. Ne plus modifier le Slug d'une fiche déjà en ligne (adresse Google).

## Contenu du dépôt

- `build/sync_airtable.py` : Airtable vers `data/references.json` et `dist/refs/`
- `build/build.py` : génère `dist/` (pages, sitemap, robots) ; `site.css`, `site.js` : mise en forme
- `data/` : actualités, textes des pages, diaporama
- `static/` : images hors références, chatbot Célia, `_headers`, `_redirects` (redirections 301)
- `wrangler.jsonc` : configuration du Worker Cloudflare

## Secrets GitHub nécessaires

- `AIRTABLE_TOKEN` : jeton Airtable, lecture seule (`data.records:read`) sur la base ABEL Community Management
- `CLOUDFLARE_API_TOKEN` : jeton Cloudflare, modèle « Edit Cloudflare Workers »
