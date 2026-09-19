# Changelog

Este proyecto sigue [Semantic Versioning](https://semver.org/) y mantiene los cambios
relevantes con el formato de [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- Estructura inicial del monorepo.
- Servicio FastAPI en modo simulado.
- Persistencia SQLite con migración inicial.
- Correlación de eventos y política de bloqueo con actuador simulado.
- Aprovisionamiento reproducible de nginx, Suricata, nftables y Fail2ban.
- Ingesta real de `eve.json` y actuación idempotente mediante Fail2ban.
- Autenticación, API móvil, clasificador local, informes Ollama con respaldo y FCM.
- Aplicación Android para incidentes y liberación de bloqueos.
