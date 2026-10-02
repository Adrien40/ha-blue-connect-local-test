# Journal des modifications

## Non publié

- Correction : les capteurs de volume perdu, de volume de douche confort et de
  volume de douche brut utilisent désormais la classe d'état `total_increasing`
  au lieu de `measurement`, que Home Assistant refuse pour la classe d'appareil
  `water` (avertissement au démarrage). Home Assistant peut proposer de
  corriger les statistiques à long terme de ces trois capteurs dans Outils de
  développement > Statistiques.
- Échelle de qualité d'intégration : niveau Platinum déclaré
  (`quality_scale.yaml`, `manifest.json`). La dernière règle ouverte,
  `test-coverage`, est remplie : chaque module est couvert à 100 % (lignes et
  branches) et le workflow de tests échoue désormais sous 95 %.
- 178 nouveaux tests : cycle de connexion BLE (faux client scripté), écritures
  de configuration, redémarrage « nouvelle douche », boucle d'arrière-plan,
  capteurs, bouton, nombre, interrupteur et cycle de vie de l'entrée.
- `quality_scale.yaml` est aussi vérifié par rapport au seuil de couverture de
  la CI et à l'étape `mypy --strict`.

## 1.1.0

- Nouveaux capteurs : durée de douche à l'eau froide et temps pour atteindre la température de confort.
- Les durées sont calculées en secondes à partir du compteur de l'appareil (1/50 s), avec gestion correcte du dépassement du compteur 16 bits.
- Toutes les entités partagent désormais une classe de base commune (`HydraoEntity`).
- Flux de configuration et d'options : une description pour chaque champ.
- Échelle de qualité d'intégration : niveau Bronze déclaré (`quality_scale.yaml`).
- Traductions complétées dans toutes les langues.
- Nécessite Home Assistant 2026.5.0 ou plus récent.
