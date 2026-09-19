import 'package:defensa_movil/modelos.dart';
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
}
