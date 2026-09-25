# Journal des modifications

## 1.2.0

### Prérequis (changement cassant)
- **Home Assistant 2026.3.0 ou plus récent** (`hacs.json`), c'est-à-dire la première version
  livrée avec Python 3.14. La suite de tests passe sur 2026.3.0 et 2026.9.3.

### Ajouté
- Capteur de diagnostic **Redox Brut** (mV), à côté du pH brut existant : la valeur de la sonde
  *avant* tout décalage, pour calibrer sur une solution étalon.

### À propos du chlore
- L'intégration n'a **volontairement aucune estimation de chlore** : le Redox est un pouvoir oxydant,
  pas une concentration (il varie avec le pH, la température, le stabilisant, les autres oxydants et
  le vieillissement de la sonde), et une valeur de chlore fausse mais qui a l'air précise est pire que
  pas de valeur. L'entité **CyA** et le **type de traitement** (chlore/brome) sont conservés, mais
  aucune valeur calculée n'en dépend pour le moment.

### Corrigé
- Les trames BLE invalides étaient retentées indéfiniment : `retry_count` était remis à zéro avant
  le décodage de la trame, donc les tentatives ne s'épuisaient jamais et l'état « injoignable »
  n'était jamais atteint.
- `async_shutdown` n'appelait pas l'implémentation parente (rafraîchissement planifié et debouncer
  laissés actifs après le déchargement) et n'était pas idempotent : maintenant que le coordinateur
  reçoit son `config_entry`, Home Assistant l'appelle aussi au déchargement, ce qui aurait annulé
  deux fois les callbacks Bluetooth.
- La minuterie de la 1re analyse (2 s après le démarrage) n'était jamais annulée au déchargement.
- `device_registry.async_get_device` est déprécié sur Home Assistant récent (2026.9) alors que son
  remplaçant n'existe pas encore sur 2026.3.0 : une fonction de compatibilité fonctionne sur les deux.
- `validate_calibration` levait une exception sur une valeur ORP / décalage / CyA / intervalle non numérique.

### Durci
- Un pH calculé hors de 0–14 devient *inconnu* au lieu d'être affiché.
- L'indice de Langelier et le pH d'équilibre refusent NaN et l'infini.

### Interne
- Le coordinateur reçoit explicitement son `config_entry` ; les pauses BLE sont des constantes nommées.
- Suite de tests passée de 40 à ~300 tests : Bluetooth simulé (authentification, notifications,
  annonces passives, échos, Silver/Gold), coordinateur, config/options flow, chaîne de migration
  1.1 → 1.4, entités, cohérence des traductions, tests par propriétés.
- CI : workflow pytest + couverture (Python 3.14, mêmes versions d'actions GitHub que les autres
  workflows) ; configuration ruff / pytest explicite dans `pyproject.toml` ; `requirements_test.txt`.
- Style (ruff) : `asyncio.TimeoutError` → `TimeoutError` et syntaxe Python 3.14 `except A, B:` dans
  `button.py`, `time.py` et `coordinator.py`.
- Version portée à 1.2.0.

### Documentation
- `README.md` / `README.fr.md` : version minimale de Home Assistant, Redox brut, pourquoi il n'y a
  pas de capteur de chlore, section développement.
