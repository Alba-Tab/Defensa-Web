import 'package:flutter/material.dart';

import 'pantallas/detalle_incidente.dart';
import 'pantallas/inicio.dart';
import 'pantallas/login.dart';
import 'servicios/api_defensa.dart';
import 'servicios/notificaciones.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AplicacionDefensa());
}

class AplicacionDefensa extends StatefulWidget {
  const AplicacionDefensa({super.key});

  @override
  State<AplicacionDefensa> createState() => _AplicacionDefensaState();
}

class _AplicacionDefensaState extends State<AplicacionDefensa> {
  final _api = ApiDefensa();
  final _navegador = GlobalKey<NavigatorState>();
  late final Future<bool> _sesionInicial = _api.inicializar();
  bool? _autenticado;

  Future<void> _activarNotificaciones() =>
      Notificaciones().inicializar(_api, (id) async {
        final incidente = await _api.incidente(id);
        _navegador.currentState?.push(
          MaterialPageRoute(
            builder: (_) => PantallaDetalleIncidente(incidente: incidente),
          ),
        );
      });

  void _ingresoCorrecto() {
    setState(() => _autenticado = true);
    _activarNotificaciones();
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    navigatorKey: _navegador,
    title: 'Defensa web',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0B5D4B)),
      useMaterial3: true,
    ),
    home: FutureBuilder<bool>(
      future: _sesionInicial,
      builder: (context, snapshot) {
        if (!snapshot.hasData && _autenticado == null) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final autenticado = _autenticado ?? snapshot.data ?? false;
        if (!autenticado) {
          return PantallaLogin(api: _api, alIngresar: _ingresoCorrecto);
        }
        return PantallaInicio(
          api: _api,
          alSalir: () => setState(() => _autenticado = false),
        );
      },
    ),
  );
}
