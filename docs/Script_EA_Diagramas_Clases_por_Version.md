/*
 * Clases - Modelo de datos POR VERSION (Grupo 13, IS2)
 *
 * Genera tres diagramas de clases, uno por migracion de Alembic, cada uno en su propio
 * paquete y con sus propios elementos (son fotos del modelo, no se pisan entre si):
 *
 *   0001 Inicial          7 clases, 3 enumeraciones   (la base tal como esta en defensa.db)
 *   0002 Sprint 1         + informe, contador de eventos, lista blanca predeterminada
 *   0003 Final (Sprint 2) + notificacion, modelo del informe y columnas del clasificador
 *
 * Las clases y atributos salen del esquema real de cada revision. Las claves foraneas no
 * se dibujan como atributos: las expresan las asociaciones con su multiplicidad
 * (clave obligatoria = 1, clave opcional = 0..1).
 *
 * Donde crea todo: dentro del paquete seleccionado en el Project Browser
 * (si no hay ninguno, en la raiz del modelo).
 * Es idempotente: se puede ejecutar varias veces sin duplicar nada.
 */

// ---------------------------------------------------------------------------
// DATOS DEL MODELO (editar aqui, no en la logica)
// ---------------------------------------------------------------------------

var PAQUETE_RAIZ = "Modelo de Datos por versión";
var GENERAR = ["0001", "0002", "0003"];   // quita alguna para generar solo las demas

var VERSIONES = [
    { id: "0001", paquete: "0001 Inicial",          diagrama: "Clases - 0001 Inicial" },
    { id: "0002", paquete: "0002 Sprint 1",         diagrama: "Clases - 0002 Sprint 1" },
    { id: "0003", paquete: "0003 Final (Sprint 2)", diagrama: "Clases - 0003 Final (Sprint 2)" }
];

var LINEA = 18, ANCHO_CLASE = 270, ANCHO_ENUM = 170;

// Enumeraciones: desde = primera version en que existen. Un literal puede llevar valor.
// El tipo de un atributo que coincide con una de estas enumeraciones queda enlazado a ella.
var ENUMS = [
    { id: "sev",  nombre: "Severidad",       desde: "0002", x: 40,   y: 22,
      lit: [["baja", "1"], ["media", "2"], ["alta", "3"], ["critica", "4"]] },
    { id: "tipo", nombre: "TipoAtaque",      desde: "0001", x: 40,   y: 196,
      lit: ["sqli", "xss", "traversal", "escaneo", "sondeoArchivos", "fuerzaBruta", "indeterminado"] },
    { id: "einc", nombre: "EstadoIncidente", desde: "0001", x: 40,   y: 424, lit: ["abierto", "cerrado"] },
    { id: "orig", nombre: "OrigenInforme",   desde: "0002", x: 40,   y: 562, lit: ["plantilla", "generadoIa"] },
    { id: "eban", nombre: "EstadoBaneo",     desde: "0001", x: 40,   y: 700, lit: ["vigente", "expirado", "liberado", "fallido"] },
    { id: "cia",  nombre: "ClaseIa",         desde: "0003", x: 1130, y: 200,
      lit: ["benigno", "sqli", "xss", "traversal", "escaneo", "fuerzaBruta", "indeterminado"] }
];

// Atributos: [nombre, tipo, marca, desde]. marca: "?" = opcional (0..1), "u" = unico.
// Si un mismo nombre aparece dos veces, la entrada de la version mas reciente reemplaza a
// la anterior en su misma posicion (por ejemplo severidad: Integer -> Severidad).
var CLASES = [
    { id: "inc", nombre: "Incidente", x: 330, y: 200,
      nota: "Agrupa los eventos de una misma IP y categoría. Permanente. Desde 0002, un índice único parcial garantiza un solo incidente abierto por IP y categoría. severidad: mayor = más grave (1 baja, 2 media, 3 alta, 4 crítica).",
      attrs: [ ["id", "Integer", "", "0001"], ["ipOrigen", "String", "", "0001"], ["categoria", "String", "", "0001"],
               ["tipoAtaque", "TipoAtaque", "", "0001"], ["severidad", "Integer", "", "0001"], ["severidad", "Severidad", "", "0002"],
               ["estado", "EstadoIncidente", "", "0001"], ["inicio", "DateTime", "", "0001"], ["ultimaActividad", "DateTime", "", "0001"],
               ["totalEventos", "Integer", "", "0002"], ["informe", "String", "?", "0002"], ["origenInforme", "OrigenInforme", "?", "0002"],
               ["severidadNotificada", "Severidad", "?", "0003"], ["modeloInforme", "String", "?", "0003"] ] },
    { id: "ev", nombre: "Evento", x: 760, y: 200,
      nota: "Alerta de Suricata. Se purga a los 30 días. Desde 0003 guarda lo que consume y produce el clasificador local. severidadFirma es el valor crudo de Suricata (1 alta, 2 media, 3 baja).",
      attrs: [ ["id", "Integer", "", "0001"], ["fechaUtc", "DateTime", "", "0001"], ["ipOrigen", "String", "", "0001"], ["sid", "Integer", "", "0001"],
               ["firma", "String", "", "0001"], ["categoria", "String", "", "0001"], ["severidadFirma", "Integer", "", "0001"],
               ["metodo", "String", "?", "0001"], ["url", "String", "?", "0001"],
               ["userAgent", "String", "?", "0003"], ["cuerpoTruncado", "String", "?", "0003"],
               ["claseIa", "ClaseIa", "?", "0003"], ["confianzaIa", "Float", "?", "0003"] ] },
    { id: "ban", nombre: "Baneo", x: 330, y: 590,
      nota: "Bloqueo temporal de una IP en el firewall. Todo baneo pertenece a un incidente. Duración: 10 min x 2^nivelReincidencia, con tope de 24 h.",
      attrs: [ ["id", "Integer", "", "0001"], ["ip", "String", "", "0001"], ["inicio", "DateTime", "", "0001"], ["expira", "DateTime", "", "0001"],
               ["estado", "EstadoBaneo", "", "0001"], ["nivelReincidencia", "Integer", "", "0001"] ] },
    { id: "lb", nombre: "ListaBlanca", x: 760, y: 590,
      nota: "Direcciones o redes que nunca se bloquean. Sin claves foráneas: la regla la aplica el código antes de banear. Desde 0002, las predeterminadas (loopback, red de administración, gateway) se marcan y no se pueden quitar.",
      attrs: [ ["id", "Integer", "", "0001"], ["ipORed", "String", "u", "0001"], ["descripcion", "String", "?", "0001"],
               ["predeterminada", "Boolean", "", "0002"] ] },
    { id: "usu", nombre: "Usuario", x: 330, y: 880,
      nota: "Administrador de seguridad. En el MVP hay un único usuario, sembrado desde una variable de entorno. Se desactiva (activo) en vez de borrarse.",
      attrs: [ ["id", "Integer", "", "0001"], ["nombre", "String", "u", "0001"], ["hashContrasena", "String", "", "0001"],
               ["activo", "Boolean", "", "0001"], ["creadoEn", "DateTime", "", "0001"] ] },
    { id: "dis", nombre: "Dispositivo", x: 760, y: 880,
      nota: "Dispositivo móvil con la app Flutter, registrado para recibir notificaciones push por FCM. El token rota: se actualiza sin duplicar y se elimina si FCM responde UNREGISTERED.",
      attrs: [ ["id", "Integer", "", "0001"], ["tokenFcm", "String", "u", "0001"], ["plataforma", "String", "", "0001"],
               ["alta", "DateTime", "", "0001"], ["actualizadoEn", "DateTime", "", "0001"] ] },
    { id: "aud", nombre: "Auditoria", x: 1130, y: 880,
      nota: "Registro de solo agregar de las acciones que modifican el firewall. Guarda el actor como texto ('sistema' en las acciones automáticas), por eso no tiene claves foráneas.",
      attrs: [ ["id", "Integer", "", "0001"], ["fechaUtc", "DateTime", "", "0001"], ["actor", "String", "", "0001"],
               ["accion", "String", "", "0001"], ["ipAfectada", "String", "?", "0001"], ["detalle", "String", "?", "0001"] ] }
];

// [cliente, multiplicidad junto al cliente, proveedor, multiplicidad junto al proveedor, nombre, compuesto]
// compuesto: el rombo relleno queda en el proveedor (el "todo"). Cada una es una clave foranea:
// obligatoria (NOT NULL) = 1, opcional = 0..1.
var ASOCIACIONES = [
    ["ev",  "0..*", "inc", "1",    "agrupa",   true],
    ["ban", "0..*", "inc", "1",    "origina",  false],
    ["dis", "0..*", "usu", "0..1", "registra", false]
];

// [cliente, proveedor, estereotipo]. Las dependencias hacia enumeraciones se deducen solas
// de los tipos de los atributos; aqui solo va lo que no es un tipo.
var DEPENDENCIAS = [
    ["ban", "lb", "consulta"]
];

// ---------------------------------------------------------------------------
// HELPERS IDEMPOTENTES (buscar por nombre; si no existe, crear)
// ---------------------------------------------------------------------------

function mismoNombre(a, b) {
    return String(a).toLowerCase() == String(b).toLowerCase();
}

function paqueteBase() {
    try {
        var sel = Repository.GetTreeSelectedPackage();
        if (sel != null) { return sel; }
    } catch (e) { /* sin seleccion: se usa la raiz */ }
    return Repository.Models.GetAt(0);
}

function buscarOCrearPaquete(padre, nombre) {
    var col = padre.Packages;
    for (var i = 0; i < col.Count; i++) {
        if (mismoNombre(col.GetAt(i).Name, nombre)) { return col.GetAt(i); }
    }
    var nuevo = col.AddNew(nombre, "");
    nuevo.Update();
    col.Refresh();
    return nuevo;
}

function buscarOCrearDiagrama(paquete, nombre, tipo) {
    var col = paquete.Diagrams;
    for (var i = 0; i < col.Count; i++) {
        if (mismoNombre(col.GetAt(i).Name, nombre)) { return col.GetAt(i); }
    }
    var nuevo = col.AddNew(nombre, tipo);
    nuevo.Update();
    col.Refresh();
    return nuevo;
}

// La nota solo se escribe al crear (no pisa ediciones manuales); el estereotipo se
// corrige siempre, porque de el depende como se dibuja el elemento
function buscarOCrearElemento(paquete, nombre, metatipo, nota, estereotipo) {
    var col = paquete.Elements;
    for (var i = 0; i < col.Count; i++) {
        var e = col.GetAt(i);
        if (e.Type == metatipo && mismoNombre(e.Name, nombre)) {
            if (estereotipo && e.Stereotype != estereotipo) { e.Stereotype = estereotipo; e.Update(); }
            return e;
        }
    }
    var nuevo = col.AddNew(nombre, metatipo);
    if (estereotipo) { nuevo.Stereotype = estereotipo; }
    if (nota)        { nuevo.Notes = nota; }
    nuevo.Update();
    col.Refresh();
    return nuevo;
}

// Si ya esta en el diagrama no se mueve (respeta la posicion que hayas ajustado a mano)
function agregarADiagrama(diagrama, elemento, x, y, ancho, alto) {
    var objs = diagrama.DiagramObjects;
    for (var i = 0; i < objs.Count; i++) {
        if (objs.GetAt(i).ElementID == elemento.ElementID) { return; }
    }
    var pos = "l=" + x + ";r=" + (x + ancho) + ";t=" + y + ";b=" + (y + alto) + ";";
    var obj = objs.AddNew(pos, "");
    obj.ElementID = elemento.ElementID;
    obj.Update();
    objs.Refresh();
}

// origen = cliente, destino = proveedor. Una composicion es una asociacion con el
// extremo del "todo" marcado como compuesto; EA puede guardarla como Aggregation,
// por eso al buscar se aceptan ambos tipos.
function crearRelacion(origen, destino, tipo, estereotipo, nombre) {
    var col = origen.Connectors;
    var esAsoc = (tipo == "Association" || tipo == "Aggregation");
    for (var i = 0; i < col.Count; i++) {
        var c = col.GetAt(i);
        var mismoTipo = (c.Type == tipo) || (esAsoc && (c.Type == "Association" || c.Type == "Aggregation"));
        if (mismoTipo && c.ClientID == origen.ElementID &&
            c.SupplierID == destino.ElementID && c.Stereotype == (estereotipo || "")) {
            return c;
        }
    }
    var nueva = col.AddNew(nombre || "", tipo);
    nueva.ClientID = origen.ElementID;
    nueva.SupplierID = destino.ElementID;
    if (estereotipo) { nueva.Stereotype = estereotipo; }
    nueva.Update();
    col.Refresh();
    return nueva;
}

// Asociacion con multiplicidad en ambos extremos. Los extremos se fijan despues del
// primer Update() del conector, que es cuando EA los crea.
function crearAsociacion(cliente, multCliente, proveedor, multProveedor, nombre, compuesto) {
    var c = crearRelacion(cliente, proveedor, compuesto ? "Aggregation" : "Association", "", nombre);
    c.ClientEnd.Cardinality = multCliente;
    c.SupplierEnd.Cardinality = multProveedor;
    if (compuesto) { c.SupplierEnd.Aggregation = 2; }   // 0 ninguno, 1 compartido, 2 compuesto
    c.ClientEnd.Update();
    c.SupplierEnd.Update();
    c.Update();
    return c;
}

// ---------------------------------------------------------------------------
// ATRIBUTOS Y LITERALES
// ---------------------------------------------------------------------------

function tieneAtributo(elemento, nombre) {
    var col = elemento.Attributes;
    for (var i = 0; i < col.Count; i++) {
        if (mismoNombre(col.GetAt(i).Name, nombre)) { return true; }
    }
    return false;
}

function agregarAtributo(elemento, a, pos, enums) {
    if (tieneAtributo(elemento, a[0])) { return; }
    var t = elemento.Attributes.AddNew(a[0], "");
    t.Type = a[1];
    t.Visibility = "Private";
    t.Pos = pos;
    if (a[2] == "?") { t.LowerBound = "0"; t.UpperBound = "1"; }
    if (a[2] == "u") { t.Stereotype = "unique"; }
    if (enums[a[1]]) {
        try { t.ClassifierID = enums[a[1]].ElementID; } catch (e) { /* queda como texto */ }
    }
    t.Update();
}

function agregarLiteral(enumeracion, literal, pos) {
    var nombre = (typeof literal == "string") ? literal : literal[0];
    if (tieneAtributo(enumeracion, nombre)) { return; }
    var t = enumeracion.Attributes.AddNew(nombre, "");
    try { t.StyleEx = "IsLiteral=1;"; } catch (e) { /* si falla, se ve como atributo */ }
    if (typeof literal != "string") {
        try { t.Default = literal[1]; } catch (e2) { /* sin valor visible */ }
    }
    t.Pos = pos;
    t.Update();
}

// Alto de una caja: cabecera + una linea por miembro (+ linea del keyword o estereotipo)
function altoCaja(miembros, conKeyword) {
    return 34 + (conKeyword ? 14 : 0) + miembros * LINEA + 14;
}

// Muestra cada etapa en System Output y devuelve su nombre. Si el script no imprime ni
// "Iniciando", no se esta ejecutando (lenguaje, tipo de script o grupo equivocado);
// si se detiene en una etapa, esa es la que falla.
function etapa(nombre) {
    Session.Output("  - " + nombre);
    return nombre;
}

// Atributos de una clase en una version: los que ya existen, con el tipo vigente
function atributosDe(clase, version) {
    var res = [], pos = {}, i, a;
    for (i = 0; i < clase.attrs.length; i++) {
        a = clase.attrs[i];
        if (a[3] > version) { continue; }              // todavia no existe en esta version
        if (pos[a[0]] === undefined) { pos[a[0]] = res.length; res.push(a); }
        else { res[pos[a[0]]] = a; }                   // cambio de tipo en una version posterior
    }
    return res;
}

// Genera el diagrama de una version; devuelve el diagrama para poder abrirlo al final
function generarVersion(raiz, v) {
    var i, j, c, e, r, attrs, tipoDe;
    var el = {};       // id -> elemento de EA
    var enums = {};    // nombre de la enumeracion -> elemento (para tipar atributos)

    var paq  = buscarOCrearPaquete(raiz, v.paquete);
    var diag = buscarOCrearDiagrama(paq, v.diagrama, "Class");

    for (i = 0; i < ENUMS.length; i++) {
        e = ENUMS[i];
        if (e.desde > v.id) { continue; }
        el[e.id] = buscarOCrearElemento(paq, e.nombre, "Enumeration", "", "");
        enums[e.nombre] = el[e.id];
        for (j = 0; j < e.lit.length; j++) { agregarLiteral(el[e.id], e.lit[j], j); }
        el[e.id].Attributes.Refresh();
        agregarADiagrama(diag, el[e.id], e.x, e.y, ANCHO_ENUM, altoCaja(e.lit.length, true));
    }

    for (i = 0; i < CLASES.length; i++) {
        c = CLASES[i];
        attrs = atributosDe(c, v.id);
        el[c.id] = buscarOCrearElemento(paq, c.nombre, "Class", c.nota, "");
        for (j = 0; j < attrs.length; j++) { agregarAtributo(el[c.id], attrs[j], j, enums); }
        el[c.id].Attributes.Refresh();
        agregarADiagrama(diag, el[c.id], c.x, c.y, ANCHO_CLASE, altoCaja(attrs.length, false));
    }

    for (i = 0; i < ASOCIACIONES.length; i++) {
        r = ASOCIACIONES[i];
        crearAsociacion(el[r[0]], r[1], el[r[2]], r[3], r[4], r[5]);
    }

    // Una dependencia por cada enumeracion que la clase usa como tipo
    for (i = 0; i < CLASES.length; i++) {
        c = CLASES[i];
        attrs = atributosDe(c, v.id);
        tipoDe = {};
        for (j = 0; j < attrs.length; j++) {
            if (enums[attrs[j][1]] && !tipoDe[attrs[j][1]]) {
                tipoDe[attrs[j][1]] = true;
                crearRelacion(el[c.id], enums[attrs[j][1]], "Dependency", "", "");
            }
        }
    }
    for (i = 0; i < DEPENDENCIAS.length; i++) {
        r = DEPENDENCIAS[i];
        crearRelacion(el[r[0]], el[r[1]], "Dependency", r[2], "");
    }

    Repository.ReloadDiagram(diag.DiagramID);
    return diag;
}

// ---------------------------------------------------------------------------
// PROGRAMA PRINCIPAL
// ---------------------------------------------------------------------------

function main() {
    var paso = "inicio";
    Session.Output("Iniciando: modelo de datos por versión");
    try {
        var i, j, v, ultimo = null, hechas = 0;

        paso = etapa("paquete raíz");
        var raiz = buscarOCrearPaquete(paqueteBase(), PAQUETE_RAIZ);

        for (i = 0; i < VERSIONES.length; i++) {
            v = VERSIONES[i];
            for (j = 0; j < GENERAR.length; j++) {
                if (GENERAR[j] == v.id) {
                    paso = etapa("versión " + v.id + " (" + v.paquete + ")");
                    ultimo = generarVersion(raiz, v);
                    hechas++;
                }
            }
        }

        paso = etapa("refrescar vista");
        Repository.RefreshModelView(0);
        if (ultimo != null) { Repository.OpenDiagram(ultimo.DiagramID); }

        Session.Output("Listo: " + hechas + " diagrama(s) de clases en '" + PAQUETE_RAIZ + "'.");
    } catch (ex) {
        Session.Output("ERROR en el paso [" + paso + "]: " + (ex.description || ex.message));
    }
}

main();
