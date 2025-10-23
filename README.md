![presentation airflow](img/airflow_logo.webp)
# Automatisation d'un Workflow ML avec Airflow et Notifications

Ce projet déploie un pipeline de Machine Learning complet orchestré par Apache Airflow. Le workflow automatise le chargement des données, le prétraitement, l'entraînement d'un modèle de régression logistique, son évaluation, et envoie des notifications par e-mail en cas de succès ou d'échec.

Le projet est conçu pour être exécuté localement dans un environnement de développement et inclut des outils comme **MailCatcher** pour simuler l'envoi d'e-mails.

## 📋 Contexte

Ce projet a été réalisé dans le cadre d'une évaluation visant à démontrer les compétences suivantes :
- Installation et configuration d'un environnement Apache Airflow.
- Création et déploiement d'un DAG (Directed Acyclic Graph).
- Orchestration d'un workflow de Machine Learning de bout en bout.
- Implémentation de notifications pour le monitoring.

## ✨ Fonctionnalités

- **Pipeline ML Automatisé** : Enchaînement des tâches de préparation des données, entraînement et évaluation.
- **Notifications par E-mail** : Utilisation des `callbacks` Airflow pour envoyer un e-mail en cas de succès ou d'échec du DAG.
- **Test d'E-mail Local** : Intégration de MailCatcher pour intercepter les e-mails envoyés par Airflow sans nécessiter de serveur SMTP réel.
- **Simulation de Défaillance** : Une tâche de test permet de forcer l'échec du DAG via une Variable Airflow pour tester les notifications d'erreur.
- **Scripts d'Automatisation** : Des scripts shell (`init_airflow.sh`, `run_airflow.sh`) simplifient l'installation et le lancement du projet.
- **Intégration Externe** : Le DAG notifie une API Flask externe en fin d'exécution.

## ⚙️ Workflow du DAG

Le DAG `Airflow_Lab2` suit la séquence de tâches suivante :

```
[load_data] >> [data_preprocessing] >> [separate_data_outputs] >> [build_model] >> [evaluate_model] >> [test_failure] >> [notify_flask]
```

## 🛠️ Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre système (testé sur Ubuntu) :

- **Python 3.12+**
- **Ruby 2.5+** et les outils de développement associés (`ruby-dev`, `build-essential`)
- **SQLite3** (`libsqlite3-dev`)
- **Git**

## 🚀 Installation et Configuration

Suivez ces étapes pour mettre en place l'environnement.

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/benjsant/airflow_ml_mail_automation.git
    cd airflow_ml_mail_automation
    ```

2.  **Rendez les scripts exécutables :**
    ```bash
    chmod +x init_airflow.sh run_airflow.sh
    ```

3.  **Lancez le script d'initialisation :**
    Ce script va :
    - Installer et lancer MailCatcher en arrière-plan.
    - Créer un environnement virtuel Python (`.venv`).
    - Installer les dépendances depuis `requirements.txt`.
    - Importer les variables Airflow depuis `dags/data/variables.json`.

    ```bash
    ./init_airflow.sh
    ```

## ▶️ Lancement du Projet

Une fois l'initialisation terminée, lancez Airflow avec le script suivant :

```bash
./run_airflow.sh
```

Ce script active l'environnement virtuel et démarre Airflow en mode `standalone`, ce qui lance le webserver et le scheduler.

## 💻 Comment Utiliser

1.  **Accéder à l'interface web d'Airflow** :
    - Ouvrez votre navigateur et allez sur `http://localhost:8080`.
    - Les identifiants par défaut pour le mode `standalone` sont `airflow` / `airflow25`.

2.  **Accéder à MailCatcher** :
    - Pour voir les e-mails qui seront envoyés, ouvrez un autre onglet et allez sur `http://localhost:1080`.

3.  **Activer et Déclencher le DAG** :
    - Dans l'interface Airflow, trouvez le DAG nommé `Airflow_Lab2`.
    - Activez-le en cliquant sur le bouton à gauche de son nom.
    - Pour le lancer manuellement, cliquez sur le bouton "Play" (▶️) à droite.

4.  **Observer les Résultats** :
    - Suivez l'exécution des tâches dans la vue "Graph" ou "Grid".
    - Une fois le DAG terminé (avec succès ou en échec), consultez l'interface de MailCatcher (`http://localhost:1080`) pour voir l'e-mail de notification.


## 🔧 Configuration Avancée

### Simuler un Échec

Pour tester la notification d'échec, vous pouvez modifier la Variable Airflow `force_failure`.
- Dans l'interface Airflow, allez dans `Admin -> Variables`.
- Modifiez la variable `force_failure` et mettez sa valeur à `true`.
- Relancez le DAG. La tâche `test_failure_task` échouera, ce qui déclenchera l'envoi de l'e-mail d'erreur.

## 🧩 Intégration Flask

Une petite API Flask est intégrée au projet (dags/Flask_API.py).
Elle est utilisée pour afficher les résultats du pipeline Airflow (succès ou échec) et tester la communication entre Airflow et un service externe.

L’API expose les routes suivantes :

| Endpoint | Description |
|-----------|--------------|
| `/` | Redirige vers la dernière exécution (`/success` ou `/failure`) |
| `/success` | Page de succès après exécution du DAG |
| `/failure` | Page d’erreur après échec du DAG |
| `/health` | Vérifie que l’API est active |

## 📂 Structure du Projet

```bash
airflow_ml_mail_automation/
├── airflow
│   ├── airflow.cfg
│   ├── airflow.db
│   ├── logs
│   └── simple_auth_manager_passwords.json.generated
├── dags
│   ├── data
│   │   ├── advertising.csv
│   │   ├── __init__.py
│   │   └── variables.json
│   ├── Flask_API.py
│   ├── __init__.py
│   ├── main.py
│   ├── model
│   │   └── model.sav
│   ├── src
│   │   ├── __init__.py
│   │   ├── model_development.py
│   ├── templates
│   │   ├── failure.html
│   │   └── success.html
│   ├── templates_flask
│   │   └── failure.html
│   └── working_data
│       ├── preprocessed.pkl
│       └── raw.pkl
├── init_airflow.sh
├── LICENSE
├── README.md
├── requirements.txt
└── run_airflow.sh
```
