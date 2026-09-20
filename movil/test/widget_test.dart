import 'package:defensa_movil/modelos.dart';
import 'package:defensa_movil/pantallas/configuracion.dart';
import 'package:defensa_movil/servicios/api_defensa.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

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
    });

    expect(incidente.id, 7);
    expect(incidente.tipoAtaque, 'sqli');
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
              activarNotificaciones: () async {},
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
}
