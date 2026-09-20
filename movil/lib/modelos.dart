class Incidente {
  const Incidente({
    required this.id,
    required this.ipOrigen,
    required this.tipoAtaque,
    required this.severidad,
    required this.estado,
    required this.inicio,
    this.categoriaOwasp,
    this.informe,
    this.origenInforme,
    this.eventos = const [],
  });

  factory Incidente.fromJson(Map<String, dynamic> json) => Incidente(
    id: json['id'] as int,
    ipOrigen: json['ip_origen'] as String,
    tipoAtaque: json['tipo_ataque'] as String,
    severidad: json['severidad'] as int,
    estado: json['estado'] as String,
    inicio: DateTime.parse(json['inicio'] as String),
    categoriaOwasp: json['categoria_owasp'] as String?,
    informe: json['informe'] as String?,
    origenInforme: json['origen_informe'] as String?,
    eventos: (json['eventos'] as List<dynamic>? ?? const [])
        .map((dato) => EventoIncidente.fromJson(dato as Map<String, dynamic>))
        .toList(),
  );

  final int id;
  final String ipOrigen;
  final String tipoAtaque;
  final int severidad;
  final String estado;
  final DateTime inicio;
  final String? categoriaOwasp;
  final String? informe;
  final String? origenInforme;
  final List<EventoIncidente> eventos;
}

class EventoIncidente {
  const EventoIncidente({
    this.metodo,
    this.url,
    this.parametros,
    this.cuerpoFragmento,
  });

  factory EventoIncidente.fromJson(Map<String, dynamic> json) =>
      EventoIncidente(
        metodo: json['metodo'] as String?,
        url: json['url'] as String?,
        parametros: json['parametros'] as String?,
        cuerpoFragmento: json['cuerpo_fragmento'] as String?,
      );

  final String? metodo;
  final String? url;
  final String? parametros;
  final String? cuerpoFragmento;
}

class Baneo {
  const Baneo({
    required this.ip,
    required this.estado,
    required this.expira,
    required this.incidenteId,
  });

  factory Baneo.fromJson(Map<String, dynamic> json) => Baneo(
    ip: json['ip'] as String,
    estado: json['estado'] as String,
    expira: DateTime.parse(json['expira'] as String),
    incidenteId: json['incidente_id'] as int,
  );

  final String ip;
  final String estado;
  final DateTime expira;
  final int incidenteId;
}
