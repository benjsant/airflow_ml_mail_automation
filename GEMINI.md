### 2. Mini projet

**Objectifs :** 

Ce Lab vous montre **comment orchestrer un pipeline ML existant avec Airflow**. Le cœur pédagogique du lab, c’est **l’automatisation du workflow**, pas la conception du modèle.

Le fichier `model_development.py` contient **le modèle ML prêt à être exécuté**

(une **régression logistique** sur `advertising.csv`).

Ce script fait par exemple :

- le chargement du dataset,
- la séparation train/test,
- l’entraînement du modèle,
- la sauvegarde du modèle entraîné dans `/model/`.

Vos mission, c’est :

1. **Créer les tâches Airflow** (`PythonOperator`, `BashOperator`, `EmailOperator`, etc.)
    
    qui vont exécuter les fonctions du script déjà existant (`load_data()`, `build_model()`, etc.)
    
2. **Gérer les dépendances** entre ces tâches (ex. `load_data` → `preprocess` → `train` → `evaluate`)
3. **Configurer les notifications par mail**
4. **Relier le tout à la mini-API Flask** qui affiche le statut du DAG

> Le but est d’apprendre à industrialiser un workflow de ML, pas à inventer le modèle.
> 
1. Supervision du workflow

**Le lien du Lab avec le Github** 

https://www.mlwithramin.com/blog/airflow-lab2 + https://github.com/raminmohammadi/MLOps/tree/main/Labs/Airflow_Labs/Lab_2

**NB :** Vous n’êtes pas obligé de faire le lab 1 comme mentionné dans l’article, le lab1 vous servira de base pour structurer votre projet correctement.

---

### Livrables

- Lien GitHub du projet complet
- README documenté
- Captures d’écran des résultats
- Fichier `.pdf` de synthèse avec les captures et le résumé du fonctionnement

### Pour aller plus loin :

[Déploiement complet d’un environnement Airflow sur une VM dans le cloud](https://www.notion.so/D-ploiement-d-un-environnement-Airflow-sur-une-VM-dans-le-cloud-2934c05a793281ce972fc103c023bcfa?pvs=21)