import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'api_defensa.dart';

class Notificaciones {
  static const habilitadas = bool.fromEnvironment('FCM_HABILITADO');
  bool _inicializadas = false;

  Future<void> inicializar(
    ApiDefensa api,
    void Function(int) abrirIncidente,
  ) async {
    if (!habilitadas || _inicializadas) return;
    await Firebase.initializeApp();
    final mensajeria = FirebaseMessaging.instance;
    await mensajeria.requestPermission();
    final token = await mensajeria.getToken();
    if (token != null) await api.registrarDispositivo(token);
    mensajeria.onTokenRefresh.listen(api.registrarDispositivo);
    FirebaseMessaging.onMessageOpenedApp.listen((mensaje) {
      final id = int.tryParse(mensaje.data['incidente_id'] ?? '');
      if (id != null) abrirIncidente(id);
    });
    final inicial = await mensajeria.getInitialMessage();
    final idInicial = int.tryParse(inicial?.data['incidente_id'] ?? '');
    if (idInicial != null) abrirIncidente(idInicial);
    _inicializadas = true;
  }
}
