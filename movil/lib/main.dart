import 'package:flutter/material.dart';

import 'pantallas/detalle_incidente.dart';
import 'pantallas/configuracion.dart';
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
  final _notificaciones = Notificaciones();
  final _navegador = GlobalKey<NavigatorState>();
  late final Future<bool> _sesionInicial = _api.inicializar();
  bool? _autenticado;

  @override
  void initState() {
    super.initState();
    _api.alSesionVencida = () {
      if (!mounted) return;
      _navegador.currentState?.popUntil((ruta) => ruta.isFirst);
      setState(() => _autenticado = false);
    };
    _sesionInicial.then((autenticado) {
      if (autenticado && mounted) _activarNotificaciones();
    });
  }

  Future<EstadoNotificaciones> _activarNotificaciones() async {
    final estado = await _notificaciones.inicializar(
      _api,
      _abrirIncidente,
      alertarIncidente: _mostrarAlerta,
    );
    if (!mounted) return estado;
    final contexto = _navegador.currentContext;
    if (estado == EstadoNotificaciones.permisoDenegado &&
        contexto != null &&
        contexto.mounted) {
      ScaffoldMessenger.of(contexto).showSnackBar(
        const SnackBar(
          content: Text(
            'Sin permiso de notificaciones no recibirá alertas push.',
          ),
        ),
      );
    }
    return estado;
  }

  Future<void> _abrirIncidente(int id) async {
    final incidente = await _api.incidente(id);
    if (!mounted) return;
    _navegador.currentState?.push(
      MaterialPageRoute(
        builder: (_) => PantallaDetalleIncidente(incidente: incidente),
      ),
    );
  }

  void _mostrarAlerta(int id, String resumen) {
    final contexto = _navegador.currentContext;
    if (contexto == null || !contexto.mounted) return;
    ScaffoldMessenger.of(contexto).showSnackBar(
      SnackBar(
        content: Text(resumen),
        action: SnackBarAction(
          label: 'Ver',
          onPressed: () => _abrirIncidente(id),
        ),
      ),
    );
  }

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
    routes: {
      PantallaConfiguracion.ruta: (_) => PantallaConfiguracion(
        api: _api,
        activarNotificaciones: _activarNotificaciones,
      ),
    },
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
