# -----------------------------------------------------------------------------
# Ce script train.sh exécute le programme Python src/train.py
# Ce programme entraîne un modèle de prédiction et enregistre le modèle final
# dans le répertoire model/. Le script enregistre également tous les détails
# de l'exécution dans le fichier logs/train.logs.
# -----------------------------------------------------------------------------

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Interpréteur du venv en chemin absolu : fonctionne aussi sous cron,
# où le venv n'est pas activé et où uv n'est pas dans le PATH.
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_FILE="logs/train.logs"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1 - $2" >> "$LOG_FILE"
}

log "INFO" "Lancement de src/train.py"
# stdout reste affiché (métriques), stderr est ajouté au log.
if "$PYTHON" src/train.py 2>> "$LOG_FILE"; then
    log "INFO" "Entraînement terminé avec succès"
else
    status=$?
    log "ERROR" "Échec de l'entraînement (code retour $status)"
    exit "$status"
fi