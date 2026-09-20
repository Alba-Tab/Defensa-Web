#!/usr/bin/env bash
set -euo pipefail

MODELO="${DEFENSA_OLLAMA_MODELO:-llama3.2:1b}"
HOST_OLLAMA="${OLLAMA_HOST:-0.0.0.0:11434}"
URL_LOCAL="http://127.0.0.1:11434"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama no esta instalado. Ejecuta: brew install ollama" >&2
  exit 1
fi

# El servicio de Homebrew hereda esta variable del dominio launchd del usuario.
# Hay que ejecutar este script al iniciar la sesion de demostracion para exponer
# Ollama a la VM por la interfaz host-only.
launchctl setenv OLLAMA_HOST "$HOST_OLLAMA"
brew services restart ollama >/dev/null

for _ in {1..20}; do
  if curl --fail --silent "$URL_LOCAL/api/tags" >/dev/null; then
    break
  fi
  sleep 1
done

curl --fail --silent "$URL_LOCAL/api/tags" >/dev/null || {
  echo "Ollama no respondio en $URL_LOCAL" >&2
  exit 1
}

if ! ollama list | awk 'NR > 1 {print $1}' | grep -Fxq "$MODELO"; then
  ollama pull "$MODELO"
fi

echo "Ollama listo en $HOST_OLLAMA con $MODELO"
echo "Verifica desde la VM: curl http://<IP_ANFITRION>:11434/api/tags"
