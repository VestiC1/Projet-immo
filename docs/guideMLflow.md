# Guide d'utilisation de MLflow pour votre projet DVF

## 📋 Prérequis

Installez MLflow si ce n'est pas déjà fait :
```bash
uv add mlflow
```

## 🚀 Étapes pour utiliser MLflow

### 1. Configuration initiale (une seule fois)

Lancez le script de configuration :
```bash
python setupmlflow.py
```

Cela va :
- Créer le dossier `mlruns` pour stocker vos expériences
- Créer l'expérience "DVF_Price_Prediction"
- Afficher les instructions pour lancer l'interface web

### 2. Entraîner votre modèle avec tracking MLflow

```bash
python model_training_mlflow.py
```

Ce script va :
- Charger vos données
- Entraîner le modèle RandomForest
- Logger automatiquement dans MLflow :
  - ✅ Les hyperparamètres (max_depth, n_estimators, etc.)
  - ✅ Les métriques (R², RMSE, MAE)
  - ✅ Le modèle entraîné
  - ✅ La signature du modèle (schéma input/output)
  - ✅ L'importance des features

### 3. Visualiser les résultats dans l'interface MLflow

Lancez l'interface web MLflow :
```bash
mlflow ui --backend-store-uri file://$(pwd)/mlruns
```

Puis ouvrez votre navigateur sur : **http://127.0.0.1:5000**

## 📊 Que pouvez-vous faire dans l'interface MLflow ?

### Comparer les runs
- Visualisez tous vos entraînements dans un tableau
- Comparez les métriques (R², RMSE) entre différents runs
- Triez par performance pour identifier le meilleur modèle

### Analyser un run spécifique
Pour chaque run, vous pouvez voir :
- **Parameters** : tous les hyperparamètres utilisés
- **Metrics** : graphiques d'évolution des métriques
- **Artifacts** : le modèle sauvegardé et les fichiers annexes
- **Tags** : métadonnées (auteur, type de modèle, etc.)

### Charger un modèle sauvegardé

```python
import mlflow

# Charger le modèle depuis un run spécifique
run_id = "votre_run_id"
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# Ou charger le dernier modèle enregistré dans le registry
model = mlflow.sklearn.load_model("models:/DVF_RandomForest_Production/latest")

# Faire des prédictions
predictions = model.predict(X_new)
```

## 🔄 Workflow recommandé

1. **Expérimenter** : Modifiez les hyperparamètres dans `model_training_mlflow.py`
2. **Entraîner** : Lancez le script, chaque run est automatiquement tracké
3. **Comparer** : Utilisez l'interface MLflow pour comparer les performances
4. **Sélectionner** : Identifiez le meilleur modèle
5. **Déployer** : Chargez le modèle depuis le Model Registry

## 🎯 Avantages de MLflow

- ✅ **Traçabilité** : Vous ne perdez jamais un modèle ou ses hyperparamètres
- ✅ **Comparaison** : Identifiez rapidement ce qui fonctionne le mieux
- ✅ **Reproductibilité** : Retrouvez exactement comment un modèle a été entraîné
- ✅ **Collaboration** : Partagez facilement vos résultats avec l'équipe
- ✅ **Versionning** : Gérez plusieurs versions de modèles en production

## 📝 Avec MLflow

| Aspect | Avec MLflow |
|--------|-------------|
| Sauvegarde modèle | .pkl local + MLflow tracking |
| Métriques | Stockées et comparables dans MLflow UI |
| Hyperparamètres | Automatiquement loggés |
| Historique | Tous les runs sont conservés |
| Comparaison | Interface graphique interactive |

## 🔧 Personnalisation

Pour tester d'autres hyperparamètres, modifiez simplement la section `params` dans `model_training_mlflow.py` :

```python
params = {
    "max_depth": 10,  # Testez différentes valeurs
    "random_state": 0,
    "n_estimators": 200,  # Augmentez le nombre d'arbres
    "min_samples_split": 5,  # Ajoutez de nouveaux paramètres
}
```

Chaque exécution créera un nouveau run dans MLflow pour comparaison !

## 🆘 Problèmes courants

**MLflow UI ne démarre pas ?**
- Vérifiez que le dossier `mlruns` existe
- Assurez-vous d'être dans le bon répertoire

**Erreur "Experiment not found" ?**
- Relancez `python setupmlflow.py` pour recréer l'expérience

**Modèle non trouvé dans le registry ?**
- Vérifiez que `registered_model_name` est bien défini dans `log_model()`