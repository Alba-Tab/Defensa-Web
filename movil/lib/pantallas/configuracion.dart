import 'package:flutter/material.dart';

import '../servicios/api_defensa.dart';
import '../servicios/notificaciones.dart';

class PantallaConfiguracion extends StatefulWidget {
  const PantallaConfiguracion({
    super.key,
    required this.api,
    required this.activarNotificaciones,
  });

  static const ruta = '/configuracion';

  final ApiDefensa api;
  final Future<void> Function() activarNotificaciones;

  @override
  State<PantallaConfiguracion> createState() => _PantallaConfiguracionState();
}

class _PantallaConfiguracionState extends State<PantallaConfiguracion> {
  final _servidor = TextEditingController();
  bool _cargando = true;
  bool _guardando = false;
  String? _mensaje;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    _servidor.text = await widget.api.servidor();
    if (mounted) setState(() => _cargando = false);
  }

  Future<void> _guardar() async {
    setState(() {
      _guardando = true;
      _mensaje = null;
    });
    try {
      await widget.api.actualizarServidor(_servidor.text.trim());
      setState(() => _mensaje = 'Configuración guardada');
    } on FormatException catch (error) {
      setState(() => _mensaje = error.message);
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  Future<void> _activarNotificaciones() async {
    setState(() => _mensaje = null);
    try {
      await widget.activarNotificaciones();
      setState(() => _mensaje = 'Dispositivo registrado para notificaciones');
    } catch (error) {
      setState(() => _mensaje = 'No se pudo activar Firebase: $error');
    }
  }

  @override
  void dispose() {
    _servidor.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Configuración')),
    body: _cargando
        ? const Center(child: CircularProgressIndicator())
        : ListView(
            padding: const EdgeInsets.all(24),
            children: [
              TextField(
                controller: _servidor,
                keyboardType: TextInputType.url,
                decoration: const InputDecoration(
                  labelText: 'Servidor de defensa',
                  hintText: 'http://192.168.1.20:8000',
                ),
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: _guardando ? null : _guardar,
                child: Text(_guardando ? 'Guardando…' : 'Guardar servidor'),
              ),
              const Divider(height: 40),
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.notifications),
                title: const Text('Notificaciones de incidentes'),
                subtitle: Text(
                  Notificaciones.habilitadas
                      ? 'Firebase habilitado en esta compilación'
                      : 'Compile con --dart-define=FCM_HABILITADO=true',
                ),
                trailing: Notificaciones.habilitadas
                    ? FilledButton.tonal(
                        onPressed: _activarNotificaciones,
                        child: const Text('Activar'),
                      )
                    : null,
              ),
              if (_mensaje != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(_mensaje!),
                ),
            ],
          ),
  );
}
