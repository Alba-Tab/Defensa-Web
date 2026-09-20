import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../modelos.dart';

class ApiDefensa {
  ApiDefensa({Dio? cliente, FlutterSecureStorage? almacen})
    : _dio =
          cliente ??
          Dio(
            BaseOptions(
              connectTimeout: const Duration(seconds: 5),
              receiveTimeout: const Duration(seconds: 8),
            ),
          ),
      _almacen = almacen ?? const FlutterSecureStorage() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (opciones, siguiente) {
          if (_token != null && opciones.path != '/api/auth/login') {
            opciones.headers['Authorization'] = 'Bearer $_token';
          }
          siguiente.next(opciones);
        },
        onError: (error, siguiente) async {
          if (error.response?.statusCode == 401 &&
              error.requestOptions.path != '/api/auth/login') {
            await cerrarSesion();
            alSesionVencida?.call();
          }
          siguiente.next(error);
        },
      ),
    );
  }

  static const _claveServidor = 'servidor';
  static const _claveToken = 'token';
  final Dio _dio;
  final FlutterSecureStorage _almacen;
  String? _token;
  void Function()? alSesionVencida;

  Future<bool> inicializar() async {
    final servidor = await _almacen.read(key: _claveServidor);
    _token = await _almacen.read(key: _claveToken);
    if (servidor != null) _configurarServidor(servidor);
    return servidor != null && _token != null;
  }

  Future<String> servidor() async =>
      await _almacen.read(key: _claveServidor) ?? _dio.options.baseUrl;

  Future<void> actualizarServidor(String servidor) async {
    final normalizado = _normalizarServidor(servidor);
    _configurarServidor(normalizado);
    await _almacen.write(key: _claveServidor, value: normalizado);
  }

  String _normalizarServidor(String servidor) {
    final uri = Uri.tryParse(servidor);
    if (uri == null ||
        !uri.hasAuthority ||
        (uri.scheme != 'http' && uri.scheme != 'https')) {
      throw const FormatException('Use una URL http:// o https:// válida');
    }
    return servidor.replaceFirst(RegExp(r'/$'), '');
  }

  void _configurarServidor(String servidor) {
    _dio.options.baseUrl = servidor.replaceFirst(RegExp(r'/$'), '');
  }

  Future<void> iniciarSesion(
    String servidor,
    String usuario,
    String contrasena,
  ) async {
    final normalizado = _normalizarServidor(servidor);
    _configurarServidor(normalizado);
    final respuesta = await _dio.post<Map<String, dynamic>>(
      '/api/auth/login',
      data: {'usuario': usuario, 'contrasena': contrasena},
    );
    _token = respuesta.data!['access_token'] as String;
    await _almacen.write(key: _claveServidor, value: normalizado);
    await _almacen.write(key: _claveToken, value: _token);
  }

  Future<void> cerrarSesion() async {
    _token = null;
    await _almacen.delete(key: _claveToken);
  }

  Future<List<Incidente>> incidentes() async {
    final respuesta = await _dio.get<List<dynamic>>('/api/incidentes');
    return respuesta.data!
        .map((dato) => Incidente.fromJson(dato as Map<String, dynamic>))
        .toList();
  }

  Future<Incidente> incidente(int id) async {
    final respuesta = await _dio.get<Map<String, dynamic>>(
      '/api/incidentes/$id',
    );
    return Incidente.fromJson(respuesta.data!);
  }

  Future<List<Baneo>> baneos() async {
    final respuesta = await _dio.get<List<dynamic>>('/api/baneos');
    return respuesta.data!
        .map((dato) => Baneo.fromJson(dato as Map<String, dynamic>))
        .toList();
  }

  Future<void> liberar(String ip) async {
    await _dio.post<void>('/api/baneos/${Uri.encodeComponent(ip)}/liberar');
  }

  Future<void> registrarDispositivo(String token) async {
    await _dio.post<void>(
      '/api/dispositivos',
      data: {'token_fcm': token, 'plataforma': 'android'},
    );
  }

  Stream<(int, String)> eventos() async* {
    final respuesta = await _dio.get<ResponseBody>(
      '/api/eventos',
      options: Options(responseType: ResponseType.stream),
    );
    final cuerpo = respuesta.data;
    if (cuerpo == null) return;
    final lineas = cuerpo.stream
        .cast<List<int>>()
        .transform(utf8.decoder)
        .transform(const LineSplitter());
    await for (final linea in lineas) {
      if (!linea.startsWith('data: ')) continue;
      final dato = jsonDecode(linea.substring(6)) as Map<String, dynamic>;
      final id = dato['incidente_id'] as int?;
      if (id == null) continue;
      yield (
        id,
        '${dato['tipo_ataque']} · severidad ${dato['severidad']} · ${dato['ip_origen']}',
      );
    }
  }
}
