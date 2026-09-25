# 🏊‍♂️ Blue Connect Local pour Home Assistant

Intégration locale et sans cloud pour les analyseurs de piscine **ZODIAC Blue Connect** (Gold / Silver).

Cette intégration libère votre Blue Connect du cloud en dialoguant directement en Bluetooth Low Energy (BLE) avec la sonde, sans jamais dépendre des serveurs officiels ni d'un abonnement.

## ✨ Fonctionnalités
* **100% Local :** aucune dépendance au cloud, aucune limite d'appels API.
* **Détection automatique du modèle :** Gold ou Silver, avec activation/désactivation automatique des capteurs Conductivité et Salinité selon la sonde détectée.
* **Métriques complètes :** Température, pH, Redox (ORP), Salinité, Conductivité, Batterie, Indice de Langelier (LSI).
* **Analyse à la demande :** déclenchement manuel d'une mesure via le code d'accès, en plus de l'écoute passive des trames régulières.
* **Calibration haute précision :** contrairement à l'application officielle (valeurs fixes), vous saisissez la valeur exacte de vos solutions tampon (ex. pH 7.02, 4.01), ajustée à la température.

## ⚠️ Prérequis important
Une bonne couverture Bluetooth est essentielle (RSSI idéalement au-dessus de -75 dBm). Comme pour toute sonde de piscine, l'eau absorbe fortement le signal : l'installation d'un **Proxy Bluetooth ESPHome** au plus près du bassin est fortement recommandée pour une stabilité optimale.

> ❌ Non compatible avec les versions Blueriiot.

---
*Développé par un passionné, pour la communauté.*
