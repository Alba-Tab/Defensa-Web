import 'dart:typed_data';

import 'package:defensa_movil/modelos.dart';
import 'package:defensa_movil/pantallas/configuracion.dart';
import 'package:defensa_movil/servicios/api_defensa.dart';
import 'package:defensa_movil/servicios/notificaciones.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';

class AdaptadorPrueba implements HttpClientAdapter {
  AdaptadorPrueba(this.responder);

  final ResponseBody Function(RequestOptions opciones) responder;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async => responder(options);

  @override
  void close({bool force = false}) {}
}

void main() {
  test('parsea un incidente recibido desde la API', () {
    final incidente = Incidente.fromJson({
      'id': 7,
      'ip_origen': '192.0.2.10',
      'tipo_ataque': 'sqli',
      'severidad': 1,
      'estado': 'abierto',
      'inicio': '2026-09-19T12:00:00',
      'categoria_owasp': 'A05:2025 - Injection',
      'informe': 'Informe',
      'origen_informe': 'plantilla',
      'eventos': [
        {
          'metodo': 'GET',
          'url': "/buscar?q=' OR 1=1--",
          'parametros': "q=' OR 1=1--",
          'cuerpo_fragmento': null,
        },
      ],
    });

    expect(incidente.id, 7);
    expect(incidente.tipoAtaque, 'sqli');
    expect(incidente.eventos.single.parametros, "q=' OR 1=1--");
  });

  testWidgets(
    'la ruta de configuración muestra y permite guardar el servidor',
    (tester) async {
      FlutterSecureStorage.setMockInitialValues({
        'servidor': 'http://192.168.56.10:8000',
        'token': 'token-de-prueba',
      });
      await tester.pumpWidget(
        MaterialApp(
          routes: {
            PantallaConfiguracion.ruta: (_) => PantallaConfiguracion(
              api: ApiDefensa(),
              activarNotificaciones: () async => EstadoNotificaciones.activadas,
            ),
          },
          initialRoute: PantallaConfiguracion.ruta,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Configuración'), findsOneWidget);
      expect(find.text('http://192.168.56.10:8000'), findsOneWidget);
      expect(find.text('Guardar servidor'), findsOneWidget);
    },
  );

  test(
    'guarda servidor y token y agrega Bearer mediante interceptor',
    () async {
      FlutterSecureStorage.setMockInitialValues({});
      String? autorizacion;
      final dio = Dio()
        ..httpClientAdapter = AdaptadorPrueba((opciones) {
          if (opciones.path == '/api/auth/login') {
            return ResponseBody.fromString(
              '{"access_token":"token-seguro"}',
              200,
              headers: {
                Headers.contentTypeHeader: [Headers.jsonContentType],
              },
            );
          }
          autorizacion = opciones.headers['Authorization'] as String?;
          return ResponseBody.fromString(
            '[]',
            200,
            headers: {
              Headers.contentTypeHeader: [Headers.jsonContentType],
            },
          );
        });
      final api = ApiDefensa(cliente: dio);

      await api.iniciarSesion('http://192.168.56.10:8000/', 'admin', 'secreto');
      await api.incidentes();
      final almacen = const FlutterSecureStorage();

      expect(await almacen.read(key: 'servidor'), 'http://192.168.56.10:8000');
      expect(await almacen.read(key: 'token'), 'token-seguro');
      expect(autorizacion, 'Bearer token-seguro');
    },
  );

  test('un 401 elimina la sesión y avisa a la aplicación', () async {
    FlutterSecureStorage.setMockInitialValues({
      'servidor': 'http://192.168.56.10:8000',
      'token': 'vencido',
    });
    final dio = Dio()
      ..httpClientAdapter = AdaptadorPrueba(
        (_) => ResponseBody.fromString(
          '{"detail":"Credenciales inválidas o vencidas"}',
          401,
          headers: {
            Headers.contentTypeHeader: [Headers.jsonContentType],
          },
        ),
      );
    final api = ApiDefensa(cliente: dio);
    var sesionVencida = false;
    api.alSesionVencida = () => sesionVencida = true;
    await api.inicializar();

    await expectLater(api.incidentes(), throwsA(isA<DioException>()));

    expect(sesionVencida, isTrue);
    expect(await const FlutterSecureStorage().read(key: 'token'), isNull);
  });

  test('interpreta una alerta recibida por SSE', () async {
    FlutterSecureStorage.setMockInitialValues({
      'servidor': 'http://192.168.56.10:8000',
      'token': 'vigente',
    });
    final dio = Dio()
      ..httpClientAdapter = AdaptadorPrueba(
        (_) => ResponseBody.fromString(
          'event: incidente\n'
          'data: {"incidente_id":9,"tipo_ataque":"sqli",'
          '"severidad":3,"ip_origen":"192.0.2.90"}\n\n',
          200,
          headers: {
            Headers.contentTypeHeader: ['text/event-stream'],
          },
        ),
      );
    final api = ApiDefensa(cliente: dio);
    await api.inicializar();

    final alerta = await api.eventos().first;

    expect(alerta.$1, 9);
    expect(alerta.$2, 'sqli · severidad 3 · 192.0.2.90');
  });
}
