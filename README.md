# Outil d'Intelligence Produit - Benchmark VOD/TV
👉 **https://intelligence-tv.streamlit.app/**
## Contexte & Objectif
Ce projet est un moteur d'analyse conçu pour extraire des signaux faibles et actionnables à partir de données non structurées (verbatims utilisateurs). 

En l'absence d'accès aux bases de données internes (tickets de support, CRM), cet outil a été modélisé sur les données publiques des leaders du marché français (Oqee, OrangeTV) pour établir un benchmark sectoriel. L'architecture est entièrement **"Plug-and-Play"** : le pipeline est prêt à ingérer de nouvelles données propriétaires pour générer instantanément des recommandations d'optimisation produit et technique.

## Architecture du Pipeline End-to-End
Le système repose sur un traitement de données en trois couches :

1. **Couche d'Ingestion (Extraction) :** Collecte automatisée et nettoyage des avis publics issus des plateformes de distribution (Google Play Store, App Store).
2. **Couche d'Intelligence (Moteur NLP) :** 
    * **Analyse de Sentiment :** Déploiement d'un modèle LLM pré-entraîné (`transformers`) pour extraire le sentiment intrinsèque du texte, palliant ainsi le biais des notations par étoiles.
    * **Topic Modeling Dynamique :** Implémentation de `BERTopic` pour la vectorisation et le clustering sémantique des commentaires. L'algorithme identifie et catégorise mathématiquement les points de friction (ex: UX, stabilité de flux, bugs de connexion).
3. **Couche de Restitution (Dashboarding) :** Interface d'aide à la décision construite autour d'une **Matrice de Priorisation Produit** (Fréquence du problème vs. Gravité de l'impact), permettant d'allouer les ressources de développement techniques de manière empirique.

## Stack Technique
* **Langage & Traitement :** Python, Pandas, Numpy.
* **Natural Language Processing :** Hugging Face `transformers`, `BERTopic`, `sentence-transformers`.
* **Visualisation & Déploiement :** Streamlit, Plotly Express.

## Lancement & Démonstration
L'outil d'analyse interactif est hébergé et accessible en production. 

👉 **https://intelligence-tv.streamlit.app/**
