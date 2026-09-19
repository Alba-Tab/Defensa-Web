import 'package:flutter/material.dart';

import '../modelos.dart';

class PantallaDetalleIncidente extends StatelessWidget {
  const PantallaDetalleIncidente({super.key, required this.incidente});

  final Incidente incidente;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text('Incidente #${incidente.id}')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          incidente.tipoAtaque,
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 12),
        Text('Origen: ${incidente.ipOrigen}'),
        Text('Severidad: ${incidente.severidad}'),
        Text('Estado: ${incidente.estado}'),
        Text('OWASP: ${incidente.categoriaOwasp ?? 'pendiente'}'),
        const Divider(height: 32),
        Text(incidente.informe ?? 'El informe todavía se está generando.'),
        if (incidente.origenInforme != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Text('Origen del informe: ${incidente.origenInforme}'),
          ),
      ],
    ),
  );
}
