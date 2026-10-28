# =============================================================================
# Ce script preprocessed.sh exécute le programme src/preprocessed.py
# et enregistre les détails de son exécution dans le fichier de log
# logs/preprocessed.logs.
# =============================================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Interpréteur du venv en chemin absolu : fonctionne aussi sous cron,
# où le venv n'est pas activé et où uv n'est pas dans le PATH.
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_FILE="logs/preprocessed.logs"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1 - $2" >> "$LOG_FILE"
}

log "INFO" "Lancement de src/preprocessed.py"
if "$PYTHON" src/preprocessed.py >> "$LOG_FILE" 2>&1; then
    log "INFO" "Prétraitement terminé avec succès"
else
    status=$?
    log "ERROR" "Échec du prétraitement (code retour $status)"
    exit "$status"
fi
