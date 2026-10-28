# ==============================================================================
# Script : collect.sh
# Description :
#   Ce script interroge une API afin de récupérer les ventes des modèles de cartes graphiques suivants :
#     - rtx3060
#     - rtx3070
#     - rtx3080
#     - rtx3090
#     - rx6700
#
#   Les données collectées sont ajoutées à une copie du fichier :
#     data/raw/sales_data.csv
#
#   Le fichier de sortie est sauvegardé au format :
#     data/raw/sales_YYYYMMDD_HHMM.csv
#   avec les colonnes suivantes :
#     timestamp, model, sales
#
#   L’activité de collecte (requêtes, modèles interrogés, résultats, erreurs)
#   est enregistrée dans un fichier de log :
#     logs/collect.logs
#
#   Le log est lisible et doit inclure :
#     - La date et l’heure de chaque requête
#     - Les modèles interrogés
#     - Les ventes récupérées
#     - Les éventuelles erreurs
# ==============================================================================
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

API_URL="http://0.0.0.0:5000"
MODELS=("rtx3060" "rtx3070" "rtx3080" "rtx3090" "rx6700")
LOG_FILE="logs/collect.logs"
RAW_DIR="data/raw"
OUTPUT_FILE="$RAW_DIR/sales_$(date +%Y%m%d_%H%M).csv"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1 - $2" >> "$LOG_FILE"
}

if [[ ! -f "$OUTPUT_FILE" ]]; then
    LATEST_FILE=$(ls -t "$RAW_DIR"/sales_*.csv | head -n 1)
    cp "$LATEST_FILE" "$OUTPUT_FILE"
    if [[ -n "$(tail -c 1 "$OUTPUT_FILE")" ]]; then
        echo >> "$OUTPUT_FILE"
    fi
    log "INFO" "Copie de $LATEST_FILE vers $OUTPUT_FILE"
fi

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
log "INFO" "Début de la collecte -> $OUTPUT_FILE"

for model in "${MODELS[@]}"; do
    if ! sales=$(curl -sS --fail --max-time 5 "$API_URL/$model" 2>&1); then
        log "ERROR" "Requête $API_URL/$model échouée : $sales"
        continue
    fi
    sales="${sales//[[:space:]]/}"
    if [[ ! "$sales" =~ ^[0-9]+$ ]]; then
        log "ERROR" "Réponse invalide pour $model : '$sales'"
        continue
    fi
    echo "$TIMESTAMP,$model,$sales" >> "$OUTPUT_FILE"
    log "INFO" "Requête $API_URL/$model -> modèle : $model, ventes : $sales"
done

log "INFO" "Fin de la collecte"