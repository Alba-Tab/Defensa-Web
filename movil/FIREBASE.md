# Configuración de Firebase Cloud Messaging

**Estado local verificado (2026-09-19):** cliente Android y cuenta de servicio configurados para
`defensaweb-cfc90`; APK de depuración compilado con FCM habilitado. Los JSON siguen fuera de Git.

La app Android ya tiene el plugin de Google Services y las dependencias de Firebase. El archivo
`android/app/google-services.json` no se versiona porque debe salir del proyecto Firebase real del
equipo; un archivo inventado permite compilar parcialmente, pero no demuestra Pb-9/Pb-10.

1. En Firebase Console, registrar una app Android con el paquete
   `bo.uagrm.grupo13.defensa_movil`.
2. Descargar su `google-services.json` y copiarlo en
   `movil/android/app/google-services.json`.
3. Para el backend, generar una cuenta de servicio distinta y guardarla fuera del repositorio,
   por ejemplo en `secrets/firebase-sa.json`. Configurar su ruta absoluta en
   `DEFENSA_FCM_CREDENCIALES`.
4. Ejecutar `bash movil/verificar_firebase.sh`.
5. Compilar o ejecutar la app con:

   ```bash
   cd movil
   flutter run --dart-define=FCM_HABILITADO=true
   ```

La clave de cuenta de servicio del backend sí es secreta. `google-services.json` identifica la app
cliente, pero también se mantiene fuera de Git para que cada integrante use el proyecto acordado y
para satisfacer la política del repositorio.
