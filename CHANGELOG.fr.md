# Journal des modifications

## 1.1.0

- Nouveaux capteurs : durée de douche à l'eau froide et temps pour atteindre la température de confort.
- Les durées sont calculées en secondes à partir du compteur de l'appareil (1/50 s), avec gestion correcte du dépassement du compteur 16 bits.
- Toutes les entités partagent désormais une classe de base commune (`HydraoEntity`).
- Flux de configuration et d'options : une description pour chaque champ.
- Échelle de qualité d'intégration : niveau Bronze déclaré (`quality_scale.yaml`).
- Traductions complétées dans toutes les langues.
- Nécessite Home Assistant 2026.5.0 ou plus récent.
