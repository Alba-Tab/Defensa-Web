# Evidencia de Pb-13, Pb-14 y Pb-18

Rama: `feature/erick-Pb13-Pb14-Pb18` · VM de laboratorio: `192.168.56.20`.

Las comprobaciones descritas aquí se realizaron el 21 de septiembre de 2026.
Se distinguen las pruebas automatizadas del servicio y las verificaciones en la
VM. No se presenta un resultado esperado como si fuera un resultado observado.

| HU | Resultado | Evidencia |
| --- | --- | --- |
| Pb-13 | Implementada y probada | Suricata + `ffuf` real: 12 alertas y un incidente; prueba automatizada de 120 eventos y un baneo |
| Pb-14 | Implementada y probada | Cinco solicitudes HTTPS: cinco alertas y un incidente; prueba automatizada de baneo |
| Pb-18 | Implementada y probada | API, validación, auditoría, migración y protección probadas automáticamente y en VM |

## Pb-13 — Detección de escaneo

La firma local SID `1000004` detecta User-Agents de escáneres. Incluye
`Nikto` y el User-Agent predeterminado de `ffuf`, `Fuzz Faster U Fool`.
Suricata registra inicialmente la categoría genérica `Web Application Attack`;
`EveSource` la traduce a `escaneo` por SID. La firma tiene prioridad sobre una
predicción contradictoria del clasificador para el `tipo_ataque` del incidente.
Los eventos de la misma IP y categoría se correlacionan en la ventana de cinco
minutos. El motor de Pb-6 aplica el umbral de cinco alertas de severidad 1 o 2.

Pruebas automatizadas:

- Un PCAP procesado por Suricata detectó SID `1000004` con User-Agent `Nikto/2.5`
  y con `Fuzz Faster U Fool v2.1.0`.
- Veinte páginas de catálogo con User-Agent `Mozilla/5.0` no generaron alertas
  de las firmas locales.
- 120 alertas EVE de `ffuf` de una IP se procesaron como 120 eventos, un solo
  incidente de tipo `escaneo` y un solo baneo a partir del quinto evento.

Prueba en la VM después de `vagrant provision`:

```bash
vagrant ssh -c 'sudo apt-get install -y --no-install-recommends ffuf' # Si falta ffuf
vagrant ssh -c 'ffuf -noninteractive -s -rate 2 -t 1 \
  -w /vagrant/pruebas/ffuf-rutas-pb13.txt \
  -u https://127.0.0.1/FUZZ'
```

Se observaron 12 rutas procesadas, 12 eventos con SID `1000004` desde
`127.0.0.1` y un incidente con `categoria=escaneo` y `tipo_ataque=escaneo`.
No se esperaba un baneo en esta prueba porque el loopback está en la lista
blanca. La prueba automatizada usa una IP no protegida para validar el baneo.

Limitación: la firma identifica herramientas por User-Agent; un escáner que lo
suplante o lo aleatorice puede evadir esta firma. Una detección conductual
independiente del User-Agent queda fuera de esta implementación.

## Pb-14 — Sondeo de archivos sensibles

La firma SID `1000002` detecta rutas como `.env`, `.git/config`, `.htpasswd`,
`wp-config.php` y `database.sql`. La SID `1000003` detecta extensiones de copia
de respaldo como `.bak`, `.old`, `.orig`, `.save` y `.swp`. Ambas se traducen a
la categoría `sondeo_archivos` en `EveSource` y se correlacionan en un incidente
de `tipo_ataque=sondeo_archivos`.

Decisión sobre Pb-20: el modelo local actual no fue entrenado con la clase
`sondeo_archivos`. Su predicción se conserva en `evento.clase_ia`, pero una
firma local específica prevalece para `incidente.tipo_ataque`. Esto cumple la
categoría funcional sin atribuir al modelo una clase que todavía no conoce.

Pruebas automatizadas:

- El PCAP de Suricata generó SID `1000002` para `/.env` y SID `1000003` para
  `/settings.yml.bak`.
- Cinco alertas de una IP no protegida se agruparon en un incidente
  `sondeo_archivos` y dispararon un baneo.
- Una predicción de IA `escaneo` con confianza 0,99 no cambió el tipo
  `sondeo_archivos` derivado de la firma.

Prueba HTTPS en la VM:

```bash
for ruta_prueba in '/.env' '/.git/config' '/settings.yml.bak' \
  '/wp-config.php' '/database.sql'; do
  curl --noproxy '*' -k -sS -o /dev/null \
    "https://192.168.56.20$ruta_prueba"
done
```

Se observaron cuatro eventos SID `1000002`, uno SID `1000003` y un incidente
con `categoria=sondeo_archivos` y `tipo_ataque=sondeo_archivos`. La IP de la
laptop (`192.168.56.1`) está protegida por la lista blanca; por ello la prueba
en VM no debía banearla.

## Pb-18 — Gestión de lista blanca

La API autenticada permite `GET /api/lista-blanca`, `POST /api/lista-blanca` y
`DELETE /api/lista-blanca/{id}`. Las IP y CIDR se validan y normalizan antes de
guardarse. El alta duplicada responde 409; la entrada inválida, 422; y la baja
de una predeterminada, 403. Toda alta y baja realizada por la API crea una
entrada de auditoría con actor, fecha e IP/red afectada.

Al arrancar, el servicio siembra las redes configuradas como predeterminadas
y corrige el indicador `predeterminada` en una fila que ya existiera antes de
la migración. El motor de políticas combina siempre esas redes protegidas con
las entradas dinámicas de la base de datos; la mera existencia de una entrada
dinámica ya no desactiva la protección del loopback o de administración.

Pruebas automatizadas:

- GET sin token devuelve 401; GET autenticado marca `127.0.0.0/8` y `::1/128`
  como predeterminadas.
- POST inválido no modifica la base; POST válido normaliza CIDR; POST duplicado
  responde 409.
- DELETE de una entrada dinámica deja auditoría; DELETE de una predeterminada
  responde 403.
- Una fila predeterminada migrada con `predeterminada=false` vuelve a quedar
  protegida al sembrar.
- Una red configurada sigue excluida del baneo aun cuando la tabla contiene
  otras entradas.
- Una red dinámica excluye el baneo; tras eliminarla, el siguiente evento
  activa de nuevo la política y puede producir un baneo.

La VM tenía configuradas además las redes administrativas
`192.168.56.0/24` y `192.168.56.1/32`. Las solicitudes de comprobación desde
la laptop y desde el loopback generaron incidentes, sin banear esas IP. La
API en VM también pasó una prueba autenticada de consulta, protección de
predeterminadas, validación, alta, baja y auditoría. La entrada dinámica de
prueba se retiró al finalizar:

```bash
vagrant ssh -c 'sudo /opt/defensa/venv/bin/python /vagrant/pruebas/verificar_pb18_vm.py'
```

La verificación de infraestructura terminó con todos los servicios en estado OK:

```bash
vagrant ssh -c 'sudo bash /vagrant/infra/verificar.sh'
```

## Comprobación de calidad

```bash
make check PYTHON=.venv/bin/python
```

Resultado observado: Ruff, formato, mypy, 79 pruebas y configuración de
infraestructura correctos. Las únicas advertencias son deprecaciones de
dependencias usadas por las pruebas y Alembic.
