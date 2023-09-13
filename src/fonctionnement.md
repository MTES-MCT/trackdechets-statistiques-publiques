# Principes de l'application

Les statistiques et graphiques sont précalculés et stockés dans des champs textes ou json de modèles django (stats.Computation).

La commande `manage.py build_stats` effectue ces opérations:

- calcul et stockage pour l'année en cours
- calcul et stockage pour l'année n-1 si le calcul n'existe pas
- la commande est lancée chaque nuit dans un container 2XL via un cron.json
- les calculs sont assez lourds et exigent un container one-off xl ou 2xl, l'application elle-même est peu gourmande

Principes d'affichage:

- L'affichage de la page de statistiques effectue une requête vers les objets des années n et  n-1
- Les sections dynamiques de la page (onglets) sont des views django appelées via la librairie [htmx](https://htmx.org/) (attributs hx-*)
- En cas d'erreur (objet Computation non trouvé), un message d'erreur est affiché et un email est envoyé à `MESSAGE_RECIPIENTS`

