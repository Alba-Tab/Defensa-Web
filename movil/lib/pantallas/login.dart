import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../servicios/api_defensa.dart';

class PantallaLogin extends StatefulWidget {
  const PantallaLogin({super.key, required this.api, required this.alIngresar});

  final ApiDefensa api;
  final VoidCallback alIngresar;

  @override
  State<PantallaLogin> createState() => _PantallaLoginState();
}

class _PantallaLoginState extends State<PantallaLogin> {
  final _servidor = TextEditingController(text: 'http://10.0.2.2:8000');
  final _usuario = TextEditingController(text: 'admin');
  final _contrasena = TextEditingController();
  bool _enviando = false;
  String? _error;

  Future<void> _ingresar() async {
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await widget.api.iniciarSesion(
        _servidor.text.trim(),
        _usuario.text.trim(),
        _contrasena.text,
      );
      widget.alIngresar();
    } on DioException catch (error) {
      setState(
        () => _error = error.response?.data.toString() ?? 'No se pudo conectar',
      );
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  void dispose() {
    _servidor.dispose();
    _usuario.dispose();
    _contrasena.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Defensa web')),
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        TextField(
          controller: _servidor,
          decoration: const InputDecoration(labelText: 'Servidor'),
        ),
        TextField(
          controller: _usuario,
          decoration: const InputDecoration(labelText: 'Usuario'),
        ),
        TextField(
          controller: _contrasena,
          obscureText: true,
          decoration: const InputDecoration(labelText: 'Contraseña'),
        ),
        const SizedBox(height: 20),
        FilledButton(
          onPressed: _enviando ? null : _ingresar,
          child: Text(_enviando ? 'Conectando…' : 'Iniciar sesión'),
        ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
      ],
    ),
  );
}
