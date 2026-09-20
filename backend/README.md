# Servicio de defensa

API y lógica de dominio de la plataforma. Incluye modo simulado para desarrollo y modo real
para consumir `eve.json` y actuar mediante Fail2ban en Ubuntu. La configuración se recibe
mediante variables `DEFENSA_*`; consulta `.env.example`.

La persistencia nueva pasa por `app/repositorio.py`, con sesiones breves. Al iniciar, el
`Conciliador` compara los baneos vigentes de la base con el jail dedicado: restaura los que faltan,
expira los vencidos y libera bloqueos huérfanos. La decisión y sus límites están en
`docs/adr/ADR-001-repositorio-explicito.md`.

El modelo de demostración se carga con:

```bash
DEFENSA_MODELO_CLASIFICADOR=backend/modelos/clasificador.joblib make run
```
