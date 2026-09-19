import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../modelos.dart';

class ApiDefensa {
  ApiDefensa()
    : _dio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 5))),
      _almacen = const FlutterSecureStorage();

  static const _claveServidor = 'servidor';
  static const _claveToken = 'token';
  final Dio _dio;
  final FlutterSecureStorage _almacen;
  String? _token;

  Future<bool> inicializar() async {
    final servidor = await _almacen.read(key: _claveServidor);
    _token = await _almacen.read(key: _claveToken);
    if (servidor != null) _configurarServidor(servidor);
    return servidor != null && _token != null;
  }

  void _configurarServidor(String servidor) {
    _dio.options.baseUrl = servidor.replaceFirst(RegExp(r'/$'), '');
  }

  Options get _autorizacion =>
      Options(headers: {'Authorization': 'Bearer $_token'});

  Future<void> iniciarSesion(
    String servidor,
    String usuario,
    String contrasena,
  ) async {
    _configurarServidor(servidor);
    final respuesta = await _dio.post<Map<String, dynamic>>(
      '/api/auth/login',
      data: {'usuario': usuario, 'contrasena': contrasena},
    );
    _token = respuesta.data!['access_token'] as String;
    await _almacen.write(key: _claveServidor, value: servidor);
    await _almacen.write(key: _claveToken, value: _token);
  }

  Future<void> cerrarSesion() async {
    _token = null;
    await _almacen.delete(key: _claveToken);
  }

  Future<List<Incidente>> incidentes() async {
    final respuesta = await _dio.get<List<dynamic>>(
      '/api/incidentes',
      options: _autorizacion,
    );
    return respuesta.data!
        .map((dato) => Incidente.fromJson(dato as Map<String, dynamic>))
        .toList();
  }

  Future<Incidente> incidente(int id) async {
    final respuesta = await _dio.get<Map<String, dynamic>>(
      '/api/incidentes/$id',
      options: _autorizacion,
    );
    return Incidente.fromJson(respuesta.data!);
  }

  Future<List<Baneo>> baneos() async {
    final respuesta = await _dio.get<List<dynamic>>(
      '/api/baneos',
      options: _autorizacion,
    );
    return respuesta.data!
        .map((dato) => Baneo.fromJson(dato as Map<String, dynamic>))
        .toList();
  }

  Future<void> liberar(String ip) async {
    await _dio.post<void>(
      '/api/baneos/${Uri.encodeComponent(ip)}/liberar',
      options: _autorizacion,
    );
  }

  Future<void> registrarDispositivo(String token) async {
    await _dio.post<void>(
      '/api/dispositivos',
      data: {'token_fcm': token, 'plataforma': 'android'},
      options: _autorizacion,
    );
  }
}
