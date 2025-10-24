# Guide d'utilisation de DVC pour votre projet DVF

## 📋 Qu'est-ce que DVC ?

**DVC (Data Version Control)** est un système de versionnage pour vos données et modèles ML, similaire à Git mais optimisé pour les fichiers volumineux. Il vous permet de :
- 🗂️ Versionner vos datasets et modèles sans alourdir Git
- 🔄 Reproduire n'importe quelle expérience passée
- 📊 Suivre l'évolution de vos données et résultats
- 🤝 Collaborer efficacement sur des projets data

## 🎯 Pourquoi utiliser DVC ?

| Problème sans DVC | Solution avec DVC |
|-------------------|-------------------|
| Datasets volumineux dans Git | Stockage externe + références légères |
| Impossible de retrouver quelle version de données a produit quel modèle | Versionnage automatique data ↔ code ↔ modèle |
| Pas d'historique des transformations | Pipeline traçable et reproductible |
| Collaboration difficile sur les données | Partage via remote storage (S3, Drive, etc.) |

## 📦 Prérequis

Installez DVC :
```bash
uv add dvc
```

Pour utiliser un stockage distant (optionnel) :
```bash
# Pour Google Drive
uv add 'dvc[gdrive]'

# Pour Amazon S3
uv add 'dvc[s3]'

# Pour Azure
uv add 'dvc[azure]'
```

## 🚀 Configuration initiale (une seule fois)

### 1. Initialiser DVC dans votre projet

```bash
# Depuis la racine de votre projet
dvc init
```

Cela crée :
- Un dossier `.dvc/` avec la configuration
- Un fichier `.dvcignore` (comme `.gitignore`)
- Des fichiers de config dans `.dvc/config`

### 2. Configurer un stockage distant (optionnel mais recommandé)

```bash
# Exemple avec un dossier local (pour débuter)
dvc remote add -d storage /chemin/vers/stockage

# Exemple avec Google Drive
dvc remote add -d storage gdrive://votre_folder_id

# Exemple avec S3
dvc remote add -d storage s3://mon-bucket/dvc-storage
```

### 3. Commiter la configuration

```bash
git add .dvc/.gitignore .dvc/config
git commit -m "Initialize DVC"
```

## 📊 Versionner vos données

### Ajouter un fichier de données à DVC

```bash
# Ajouter votre dataset principal
dvc add data/dvf_data.csv

# DVC crée un fichier .dvc qui référence vos données
git add data/dvf_data.csv.dvc data/.gitignore
git commit -m "Track DVF dataset with DVC"
```

**Que se passe-t-il ?**
- ✅ `dvf_data.csv` est déplacé dans `.dvc/cache`
- ✅ Un fichier `dvf_data.csv.dvc` est créé (léger, versionné par Git)
- ✅ Le vrai fichier CSV est ajouté à `.gitignore`
- ✅ Vous versionnez la référence, pas le fichier volumineux !

### Pousser les données vers le stockage distant

```bash
dvc push
```

Vos données sont maintenant sauvegardées dans votre remote storage !

### Récupérer les données (sur une autre machine ou après un clone)

```bash
# Cloner le repo Git
git clone votre_repo.git
cd votre_repo

# Récupérer les données
dvc pull
```

## 🔄 Créer un pipeline reproductible

### 1. Définir les étapes de votre pipeline

Créez un fichier `dvc.yaml` à la racine :

```yaml
stages:
  prepare_data:
    cmd: python scripts/prepare_data.py
    deps:
      - scripts/prepare_data.py
      - data/dvf_raw.csv
    outs:
      - data/dvf_clean.csv
    params:
      - prepare.test_size
      - prepare.random_state

  train_model:
    cmd: python model_training.py
    deps:
      - model_training.py
      - data/dvf_clean.csv
    params:
      - train.max_depth
      - train.n_estimators
    outs:
      - models/random_forest.pkl
    metrics:
      - metrics/train_metrics.json:
          cache: false

  evaluate:
    cmd: python evaluate.py
    deps:
      - evaluate.py
      - models/random_forest.pkl
      - data/dvf_clean.csv
    metrics:
      - metrics/test_metrics.json:
          cache: false
```

### 2. Définir vos paramètres

Créez un fichier `params.yaml` :

```yaml
prepare:
  test_size: 0.2
  random_state: 42

train:
  max_depth: 10
  n_estimators: 100
  min_samples_split: 2
  random_state: 42
```

### 3. Exécuter le pipeline

```bash
# Exécuter toutes les étapes
dvc repro

# Exécuter une étape spécifique
dvc repro train_model
```

**DVC va automatiquement :**
- ✅ Détecter les dépendances modifiées
- ✅ Ré-exécuter uniquement les étapes nécessaires
- ✅ Cacher les résultats intermédiaires
- ✅ Tracker les métriques

### 4. Versionner le pipeline

```bash
git add dvc.yaml dvc.lock params.yaml
git commit -m "Add training pipeline"
dvc push
```

## 📈 Comparer les expériences

### Visualiser les métriques

```bash
# Afficher les métriques actuelles
dvc metrics show

# Comparer avec une version précédente
dvc metrics diff main
```

### Visualiser les paramètres

```bash
# Afficher les paramètres actuels
dvc params diff
```

### Comparer plusieurs expériences

```bash
# Créer une nouvelle branche pour une expérience
git checkout -b experiment/more-trees

# Modifier les paramètres
# params.yaml : n_estimators: 200

# Exécuter le pipeline
dvc repro

# Comparer avec la branche main
dvc metrics diff main
dvc params diff main
```

## 🔧 Workflow recommandé

### Workflow quotidien

1. **Nouvelle expérience** : Créez une branche Git
   ```bash
   git checkout -b experiment/test-params
   ```

2. **Modifiez les paramètres** : Éditez `params.yaml`
   ```yaml
   train:
     max_depth: 15
     n_estimators: 200
   ```

3. **Exécutez le pipeline** :
   ```bash
   dvc repro
   ```

4. **Comparez les résultats** :
   ```bash
   dvc metrics diff main
   ```

5. **Si satisfait, commitez** :
   ```bash
   git add dvc.lock params.yaml
   git commit -m "Experiment: increase tree depth"
   dvc push
   git push origin experiment/test-params
   ```

6. **Fusionnez si meilleurs résultats** :
   ```bash
   git checkout main
   git merge experiment/test-params
   ```

## 📦 Cas d'usage pratiques

### Récupérer une ancienne version des données

```bash
# Voir l'historique
git log data/dvf_data.csv.dvc

# Revenir à une version spécifique
git checkout <commit_hash> data/dvf_data.csv.dvc
dvc checkout
```

### Partager un modèle avec un collègue

```bash
# Vous : versionnez et poussez le modèle
dvc add models/best_model.pkl
git add models/best_model.pkl.dvc
git commit -m "Add best model"
dvc push
git push

# Collègue : récupère le modèle
git pull
dvc pull
```

### Reproduire une expérience passée

```bash
# Revenir à un commit spécifique
git checkout <commit_hash>

# Récupérer les données et modèles de cette version
dvc checkout

# Ré-exécuter le pipeline (résultats identiques garantis)
dvc repro
```

## 🎨 Interface graphique avec DVC Studio (optionnel)

DVC propose une interface web pour visualiser vos expériences :

```bash
# Installer l'extension
uv add dvclive

# Dans votre code, logger des métriques
from dvclive import Live

with Live() as live:
    live.log_metric("rmse", rmse)
    live.log_metric("r2", r2)
    live.log_param("max_depth", params["max_depth"])
```

Visitez [studio.iterative.ai](https://studio.iterative.ai) pour connecter votre repo et visualiser vos expériences.

## 🆚 DVC vs MLflow : Quelle différence ?

| Aspect | DVC | MLflow |
|--------|-----|--------|
| **Focus** | Versionnage data/modèles + pipelines | Tracking expériences + déploiement |
| **Stockage** | Remote storage (S3, Drive, etc.) | Base de données locale/serveur |
| **Pipeline** | ✅ Définition déclarative | ❌ Pas de gestion de pipeline |
| **Versionnage** | ✅ Intégré avec Git | ⚠️ Versionning séparé |
| **Reproductibilité** | ✅ Totale (data + code + params) | ⚠️ Code uniquement |
| **Comparaison** | CLI + DVC Studio | ✅ Interface web riche |
| **Collaboration** | Via Git + remote storage | Via serveur MLflow |

**💡 Conseil** : Utilisez les deux ensemble !
- **DVC** pour versionner données et pipelines
- **MLflow** pour tracker les métriques et comparer les runs

## 🔧 Commandes essentielles

```bash
# Versionner un fichier
dvc add fichier.csv

# Pousser vers le remote
dvc push

# Récupérer depuis le remote
dvc pull

# Exécuter le pipeline
dvc repro

# Voir les métriques
dvc metrics show

# Comparer avec une autre branche
dvc metrics diff autre_branche

# Voir le statut
dvc status

# Voir le DAG du pipeline
dvc dag
```

## 🆘 Problèmes courants

**Erreur "file is not tracked by DVC" ?**
- Vérifiez que vous avez bien fait `dvc add fichier`
- Le fichier `.dvc` doit être commité dans Git

**`dvc pull` ne fonctionne pas ?**
- Vérifiez votre configuration remote : `dvc remote list`
- Testez la connexion : `dvc remote list`

**Pipeline ne se ré-exécute pas ?**
- Vérifiez les dépendances dans `dvc.yaml`
- Forcez l'exécution : `dvc repro --force`

**Conflit sur `dvc.lock` ?**
- Résolvez le conflit dans Git
- Ou ré-exécutez : `dvc repro` puis commitez

## ✅ Checklist de démarrage

- [ ] Installer DVC : `uv add dvc`
- [ ] Initialiser : `dvc init`
- [ ] Configurer un remote : `dvc remote add`
- [ ] Tracker vos données : `dvc add data/`
- [ ] Créer `dvc.yaml` pour votre pipeline
- [ ] Créer `params.yaml` pour vos hyperparamètres
- [ ] Exécuter : `dvc repro`
- [ ] Commiter dans Git : `git add dvc.yaml dvc.lock`
- [ ] Pousser les données : `dvc push`

## 🎓 Pour aller plus loin

- Documentation officielle : [dvc.org/doc](https://dvc.org/doc)
- Tutoriels : [dvc.org/doc/start](https://dvc.org/doc/start)
- Exemples de projets : [github.com/iterative/example-repos](https://github.com/iterative/example-repos)
- DVC Studio : [studio.iterative.ai](https://studio.iterative.ai)

---

**🎯 En résumé** : DVC transforme votre projet ML en un système reproductible où chaque version de code est liée à ses données et résultats. Plus besoin de se demander "quelle version des données a produit ce modèle" !