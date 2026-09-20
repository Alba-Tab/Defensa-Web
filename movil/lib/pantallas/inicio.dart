import 'package:flutter/material.dart';

import '../modelos.dart';
import '../servicios/api_defensa.dart';
import 'configuracion.dart';
import 'detalle_incidente.dart';

class PantallaInicio extends StatefulWidget {
  const PantallaInicio({super.key, required this.api, required this.alSalir});

  final ApiDefensa api;
  final VoidCallback alSalir;

  @override
  State<PantallaInicio> createState() => _PantallaInicioState();
}

class _PantallaInicioState extends State<PantallaInicio> {
  late Future<(List<Incidente>, List<Baneo>)> _datos = _cargar();

  Future<(List<Incidente>, List<Baneo>)> _cargar() async =>
      (await widget.api.incidentes(), await widget.api.baneos());

  void _recargar() => setState(() => _datos = _cargar());

  Future<void> _liberar(Baneo baneo) async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Liberar bloqueo'),
        content: Text('¿Liberar ${baneo.ip}? La acción quedará auditada.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Liberar'),
          ),
        ],
      ),
    );
    if (confirmar == true) {
      await widget.api.liberar(baneo.ip);
      _recargar();
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Defensa web'),
      actions: [
        IconButton(onPressed: _recargar, icon: const Icon(Icons.refresh)),
        IconButton(
          tooltip: 'Configuración',
          onPressed: () =>
              Navigator.pushNamed(context, PantallaConfiguracion.ruta),
          icon: const Icon(Icons.settings),
        ),
        IconButton(
          onPressed: () async {
            await widget.api.cerrarSesion();
            widget.alSalir();
          },
          icon: const Icon(Icons.logout),
        ),
      ],
    ),
    body: FutureBuilder<(List<Incidente>, List<Baneo>)>(
      future: _datos,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }
        final (incidentes, baneos) = snapshot.data!;
        return ListView(
          children: [
            const ListTile(title: Text('Incidentes')),
            ...incidentes.map(
              (incidente) => ListTile(
                leading: CircleAvatar(child: Text('${incidente.severidad}')),
                title: Text(incidente.tipoAtaque),
                subtitle: Text('${incidente.ipOrigen} · ${incidente.estado}'),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        PantallaDetalleIncidente(incidente: incidente),
                  ),
                ),
              ),
            ),
            const Divider(),
            const ListTile(title: Text('Bloqueos vigentes')),
            ...baneos
                .where((baneo) => baneo.estado == 'vigente')
                .map(
                  (baneo) => ListTile(
                    title: Text(baneo.ip),
                    subtitle: Text('Expira: ${baneo.expira.toLocal()}'),
                    trailing: TextButton(
                      onPressed: () => _liberar(baneo),
                      child: const Text('Liberar'),
                    ),
                  ),
                ),
          ],
        );
      },
    ),
  );
}
