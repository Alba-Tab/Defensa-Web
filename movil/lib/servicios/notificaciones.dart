import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'api_defensa.dart';

enum EstadoNotificaciones { activadas, permisoDenegado, noDisponibles }

class Notificaciones {
  static const habilitadas = bool.fromEnvironment('FCM_HABILITADO');
  bool _inicializadas = false;
  bool _sseInicializado = false;
  final Set<int> _avisadosEnPrimerPlano = {};

  Future<EstadoNotificaciones> inicializar(
    ApiDefensa api,
    void Function(int) abrirIncidente, {
    void Function(int, String)? alertarIncidente,
  }) async {
    if (!_sseInicializado) {
      api.eventos().listen(
        (alerta) => _alertarUnaVez(alerta.$1, alerta.$2, alertarIncidente),
        onError: (_) {},
      );
      _sseInicializado = true;
    }
    if (!habilitadas) return EstadoNotificaciones.noDisponibles;
    if (_inicializadas) return EstadoNotificaciones.activadas;
    await Firebase.initializeApp();
    final mensajeria = FirebaseMessaging.instance;
    final permiso = await mensajeria.requestPermission();
    if (permiso.authorizationStatus == AuthorizationStatus.denied) {
      return EstadoNotificaciones.permisoDenegado;
    }
    final token = await mensajeria.getToken();
    if (token != null) await api.registrarDispositivo(token);
    mensajeria.onTokenRefresh.listen(api.registrarDispositivo);
    FirebaseMessaging.onMessage.listen((mensaje) {
      final id = int.tryParse(mensaje.data['incidente_id'] ?? '');
      if (id != null) {
        _alertarUnaVez(id, _resumen(mensaje.data), alertarIncidente);
      }
    });
    FirebaseMessaging.onMessageOpenedApp.listen((mensaje) {
      final id = int.tryParse(mensaje.data['incidente_id'] ?? '');
      if (id != null) abrirIncidente(id);
    });
    final inicial = await mensajeria.getInitialMessage();
    final idInicial = int.tryParse(inicial?.data['incidente_id'] ?? '');
    if (idInicial != null) abrirIncidente(idInicial);
    _inicializadas = true;
    return EstadoNotificaciones.activadas;
  }

  void _alertarUnaVez(
    int id,
    String resumen,
    void Function(int, String)? alertar,
  ) {
    if (_avisadosEnPrimerPlano.add(id)) alertar?.call(id, resumen);
  }

  String _resumen(Map<String, dynamic> datos) =>
      '${datos['tipo_ataque'] ?? 'Incidente'} · severidad '
      '${datos['severidad'] ?? '?'} · ${datos['ip_origen'] ?? ''}';
}
