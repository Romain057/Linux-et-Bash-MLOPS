"""
-------------------------------------------------------------------------------
Ce script exécute l'entraînement d'un modèle XGBoost pour prédire les ventes de 
cartes graphiques à partir des données prétraitées.

1. Il commence par rechercher le dernier fichier CSV prétraité dans le dossier 
   'data/processed/'.
2. Si un modèle standard (model.pkl) n'existe pas, il charge les données, les 
   divise en ensembles d'entraînement et de test, entraîne un modèle sur ces 
   données, l'évalue, puis le sauvegarde dans 'model/model.pkl'.
3. Si un modèle standard existe déjà, il entraîne un nouveau modèle sur les 
   données les plus récentes, l'évalue, puis sauvegarde le modèle dans le dossier 
   'model/' sous formats : model_YYYYMMDD_HHMM.pkl.
4. Les métriques de performance (RMSE, MAE, R²) sont affichées et sauvegardées dans 
   le fichier de log.
5. Des erreurs éventuelles sont gérées et signalées dans les logs.

Les modèles sont sauvegardés dans le dossier 'model/' avec le nom 'model.pkl' pour 
le modèle standard et avec un horodatage pour les versions ultérieures.
Les métriques du modèle sont enregistrées dans les logs du script.
-------------------------------------------------------------------------------
"""

import logging
import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
MODEL_DIR = PROJECT_DIR / "model"
STANDARD_MODEL = MODEL_DIR / "model.pkl"
LOG_FILE = PROJECT_DIR / "logs" / "train.logs"
TARGET = "sales"
PARAMS = {"n_estimators": 100, "max_depth": 3, "learning_rate": 0.1, "random_state": 42}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_latest_processed_file() -> Path:
    """
    Retourne le fichier sales_processed_*.csv le plus récent de data/processed/
    """
    files = list(PROCESSED_DIR.glob("sales_processed_*.csv"))
    if not files:
        raise FileNotFoundError(f"Aucun fichier sales_processed_*.csv dans {PROCESSED_DIR}")
    return max(files, key=lambda f: f.stat().st_mtime)
   

def train_and_evaluate(df: pd.DataFrame) -> tuple[XGBRegressor, dict[str, float]]:
   """
   Entraine un XGBoost et evalue sur un jeu de test. 
   """
   X = df.drop(columns=[TARGET])
   y = df[TARGET]
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

   logger.info(f"Découpage : {len(X_train)} lignes d'entraînement, {len(X_test)} de test")
   model = XGBRegressor(**PARAMS)
   model.fit(X_train, y_train)
   y_pred = model.predict(X_test)

   metrics = {
      "RMSE": root_mean_squared_error(y_test, y_pred),
      "MAE": mean_absolute_error(y_test, y_pred),
      "R2": r2_score(y_test, y_pred),
   }
   return model, metrics


def get_model_path() -> Path:
    """
    model.pkl au premier entraînement, puis une version horodatée
    """
    if not STANDARD_MODEL.exists():
        return STANDARD_MODEL
    return MODEL_DIR / f"model_{datetime.now():%Y%m%d_%H%M}.pkl"


def main() -> None:
   
   logger.info("Début de l'entraînement")
   try:
      
      data_file = get_latest_processed_file()
      df = pd.read_csv(data_file)
      logger.info(f"Données : {data_file.relative_to(PROJECT_DIR)} ({len(df)} lignes)")
      logger.info(f"Hyperparamètres : {PARAMS}")

      model, metrics = train_and_evaluate(df)
      summary = ", ".join(f"{name} = {value:.3f}" for name, value in metrics.items())
      logger.info(f"Métriques sur le jeu de test : {summary}")
      print(f"Métriques sur le jeu de test : {summary}")

      MODEL_DIR.mkdir(parents=True, exist_ok=True)
      model_path = get_model_path()
      with open(model_path, "wb") as f:
         pickle.dump(model, f)
      logger.info(f"Modèle sauvegardé : {model_path.relative_to(PROJECT_DIR)}")
   except Exception:
      logger.exception("Échec de l'entraînement")
      raise SystemExit(1)
   logger.info("Fin de l'entraînement")


if __name__ == "__main__":
    main()