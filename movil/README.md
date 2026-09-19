# Aplicación móvil

Cliente Android para iniciar sesión, consultar incidentes, leer informes, ver bloqueos,
liberarlos y registrar el token FCM.

```bash
flutter pub get
flutter run
```

El servidor es editable en la pantalla de acceso. Para habilitar FCM, agrega la configuración
oficial de Firebase para Android y ejecuta:

```bash
flutter run --dart-define=FCM_HABILITADO=true
```

HTTP plano está permitido únicamente para la red del laboratorio. La entrega productiva debe
usar HTTPS y retirar `usesCleartextTraffic`.
