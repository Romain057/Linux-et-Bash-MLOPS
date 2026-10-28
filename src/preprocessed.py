"""
-------------------------------------------------------------------------------
Ce script preprocessed.py récupère les données du dernier fichier CSV créé 
dans le dossier 'data/raw/'.

1. Il applique un prétraitement aux données
   
2. Les résultats du prétraitement sont enregistrés dans un nouveau fichier CSV 
   dans le dossier 'data/processed/', avec un nom au format 
   'sales_processed_YYYYMMDD_HHMM.csv'.
   
3. Toutes les étapes du prétraitement sont enregistrées dans le fichier 
   'logs/preprocessed.logs' afin de garantir un suivi détaillé du processus.

Les erreurs ou anomalies éventuelles sont également loguées pour assurer la traçabilité.
-------------------------------------------------------------------------------
"""

import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
LOG_FILE = PROJECT_DIR / "logs" / "preprocessed.logs"
MODELS = ["rtx3060", "rtx3070", "rtx3080", "rtx3090", "rx6700"]

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_latest_raw_file() -> Path:
   """
   Retourne le fichier sales_*.csv le plus récent dans data/raw/
   """
   files = list(RAW_DIR.glob("sales_*.csv"))
   if not files:
      raise FileNotFoundError(f"Aucun fichier sales_*.csv trouvé dans {RAW_DIR}")
   return max(files, key=lambda f: f.stat().st_mtime)


def clean(df: pd.DataFrame) -> pd.DataFrame:
   """
   Supprime les lignes manquantes, invalides ou en doubles
   """
   n_initial = len(df)
   df = df.dropna().copy()
   df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
   df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
   df = df.dropna(subset=["timestamp", "sales"])
   df = df[(df["sales"] >= 0) & df["model"].isin(MODELS)]
   df = df.drop_duplicates()
   logger.info(f"Nettoyage : {n_initial - len(df)} lignes supprimées, {len(df)} restantes")
   return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme timestamp et model en variables entières, sales en dernière colonne."""
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df = df.drop(columns=["timestamp"])
    df = pd.get_dummies(df, columns=["model"], prefix="model", dtype=int)
    df["sales"] = df["sales"].astype(int)
    features = [col for col in df.columns if col != "sales"]
    return df[features + ["sales"]]


def main() -> None:
    logger.info("Début du prétraitement")
    try:
        raw_file = get_latest_raw_file()
        df = pd.read_csv(raw_file)
        logger.info(f"Fichier source : {raw_file.relative_to(PROJECT_DIR)} ({len(df)} lignes)")

        df_processed = build_features(clean(df))

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        output_file = PROCESSED_DIR / f"sales_processed_{datetime.now():%Y%m%d_%H%M}.csv"
        df_processed.to_csv(output_file, index=False)
        logger.info(f"Colonnes : {list(df_processed.columns)}")
        logger.info(f"Fichier sauvegardé : {output_file.relative_to(PROJECT_DIR)} ({len(df_processed)} lignes)")
    except Exception:
        logger.exception("Échec du prétraitement")
        raise SystemExit(1)
    logger.info(" Fin du prétraitement")


if __name__ == "__main__":
    main()
