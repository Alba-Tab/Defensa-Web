const estadoPanel = {
  incidentes: [],
  ipPendiente: null,
  graficos: {},
  fuenteEventos: null,
};

const textosEstado = {
  activo: "Operativo",
  inactivo: "Degradado",
  no_aplica: "No aplica",
  no_configurado: "No configurado",
};

async function api(ruta, opciones = {}) {
  const respuesta = await fetch(ruta, { credentials: "same-origin", ...opciones });
  if (respuesta.status === 401) {
    window.location.replace("/login");
    throw new Error("La sesión venció");
  }
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    throw new Error(cuerpo.detail || `Error ${respuesta.status}`);
  }
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

function texto(elemento, valor) {
  if (elemento) elemento.textContent = valor;
}

function fechaLegible(valor) {
  if (!valor) return "—";
  const fecha = new Date(valor.endsWith?.("Z") ? valor : `${valor}Z`);
  return Number.isNaN(fecha.getTime())
    ? valor
    : new Intl.DateTimeFormat("es-BO", { dateStyle: "short", timeStyle: "short" }).format(fecha);
}

function nombreSeveridad(valor) {
  return ({ 1: "Baja", 2: "Media", 3: "Alta", 4: "Crítica" })[valor] || `Nivel ${valor}`;
}

function insignia(valor, tipo = "estado") {
  const elemento = document.createElement("span");
  const clase = String(valor).toLowerCase().replaceAll(" ", "-");
  elemento.className = `insignia insignia-${tipo}-${clase}`;
  elemento.textContent = tipo === "severidad" ? nombreSeveridad(valor) : valor;
  return elemento;
}

function mostrarError(contenedor, columnas, mensaje) {
  const fila = document.createElement("tr");
  const celda = document.createElement("td");
  celda.colSpan = columnas;
  celda.className = "estado-tabla estado-error";
  celda.textContent = mensaje;
  fila.append(celda);
  contenedor.replaceChildren(fila);
}

function celda(valor) {
  const elemento = document.createElement("td");
  if (valor instanceof Node) elemento.append(valor);
  else elemento.textContent = valor;
  return elemento;
}

async function cargarIncidentes() {
  const cuerpo = document.querySelector("#lista-incidentes");
  const formulario = document.querySelector("#filtros-incidentes");
  const parametros = new URLSearchParams({ limite: "50" });
  const datos = new FormData(formulario);
  for (const nombre of ["desde", "hasta", "ip_origen", "severidad"]) {
    let valor = String(datos.get(nombre) || "").trim();
    if ((nombre === "desde" || nombre === "hasta") && valor) valor = new Date(valor).toISOString();
    if (valor) parametros.set(nombre, valor);
  }
  try {
    estadoPanel.incidentes = await api(`/api/incidentes?${parametros}`);
    cuerpo.replaceChildren();
    if (!estadoPanel.incidentes.length) {
      mostrarError(cuerpo, 6, "No hay incidentes para los filtros seleccionados.");
      return;
    }
    for (const incidente of estadoPanel.incidentes) {
      const fila = document.createElement("tr");
      fila.append(celda(`#${incidente.id}`));
      fila.append(celda(incidente.ip_origen));
      fila.append(celda(incidente.tipo_ataque || incidente.categoria));
      fila.append(celda(insignia(incidente.severidad, "severidad")));
      fila.append(celda(insignia(incidente.estado)));
      const boton = document.createElement("button");
      boton.className = "boton-tabla";
      boton.type = "button";
      boton.textContent = "Ver detalle";
      boton.addEventListener("click", () => abrirDetalle(incidente.id));
      fila.append(celda(boton));
      cuerpo.append(fila);
    }
  } catch (error) {
    mostrarError(cuerpo, 6, error.message);
  }
}

function agregarDato(contenedor, etiqueta, valor) {
  const bloque = document.createElement("div");
  const termino = document.createElement("dt");
  const dato = document.createElement("dd");
  termino.textContent = etiqueta;
  dato.textContent = valor;
  bloque.append(termino, dato);
  contenedor.append(bloque);
}

async function abrirDetalle(id) {
  const dialogo = document.querySelector("#detalle-incidente");
  const contenido = document.querySelector("#detalle-contenido");
  texto(document.querySelector("#detalle-titulo"), `Incidente #${id}`);
  contenido.replaceChildren();
  const cargando = document.createElement("p");
  cargando.className = "texto-secundario";
  cargando.textContent = "Cargando análisis…";
  contenido.append(cargando);
  dialogo.showModal();
  try {
    const incidente = await api(`/api/incidentes/${id}`);
    const resumen = document.createElement("dl");
    resumen.className = "detalle-resumen";
    agregarDato(resumen, "Origen", incidente.ip_origen);
    agregarDato(resumen, "Tipo", incidente.tipo_ataque || incidente.categoria);
    agregarDato(resumen, "Severidad", nombreSeveridad(incidente.severidad));
    agregarDato(resumen, "Estado", incidente.estado);
    agregarDato(resumen, "Inicio", fechaLegible(incidente.inicio));
    agregarDato(resumen, "Última actividad", fechaLegible(incidente.ultima_actividad));

    const informe = document.createElement("section");
    const cabeceraInforme = document.createElement("div");
    cabeceraInforme.className = "subcabecera";
    const tituloInforme = document.createElement("h3");
    tituloInforme.textContent = "Informe del incidente";
    const origen = insignia(incidente.origen_informe === "generado_ia" ? "Generado por IA" : "Plantilla");
    cabeceraInforme.append(tituloInforme, origen);
    const textoInforme = document.createElement("pre");
    textoInforme.className = "informe";
    textoInforme.textContent = incidente.informe || "El informe todavía se está generando.";
    informe.append(cabeceraInforme, textoInforme);

    const eventos = document.createElement("section");
    const tituloEventos = document.createElement("h3");
    tituloEventos.textContent = `Eventos relacionados (${incidente.eventos.length})`;
    const lista = document.createElement("ol");
    lista.className = "lista-eventos";
    for (const evento of incidente.eventos) {
      const item = document.createElement("li");
      const encabezado = document.createElement("strong");
      encabezado.textContent = `${fechaLegible(evento.fecha_utc)} · ${evento.firma}`;
      const peticion = document.createElement("code");
      peticion.textContent = [evento.metodo, evento.url || evento.uri_decodificada, evento.parametros]
        .filter(Boolean).join(" · ") || "Sin datos HTTP capturados";
      item.append(encabezado, peticion);
      lista.append(item);
    }
    if (!incidente.eventos.length) {
      const vacio = document.createElement("p");
      vacio.className = "texto-secundario";
      vacio.textContent = "Este incidente todavía no tiene eventos relacionados.";
      eventos.append(tituloEventos, vacio);
    } else eventos.append(tituloEventos, lista);
    contenido.replaceChildren(resumen, informe, eventos);
  } catch (error) {
    contenido.replaceChildren();
    const mensaje = document.createElement("p");
    mensaje.className = "mensaje-error";
    mensaje.textContent = error.message;
    contenido.append(mensaje);
  }
}

async function cargarSalud() {
  try {
    const salud = await api("/api/salud");
    let activos = 0;
    let configurados = 0;
    for (const clave of ["nginx", "suricata", "fail2ban", "ollama"]) {
      const fila = document.querySelector(`[data-componente='${clave}']`);
      const estado = salud[clave];
      fila.dataset.estado = estado;
      texto(fila.querySelector("span:last-child"), textosEstado[estado] || estado);
      if (estado !== "no_aplica" && estado !== "no_configurado") configurados += 1;
      if (estado === "activo") activos += 1;
    }
    texto(document.querySelector("#metrica-componentes"), configurados ? `${activos}/${configurados}` : "—");
    const plataforma = document.querySelector("#estado-plataforma");
    plataforma.className = `estado estado-${salud.estado}`;
    plataforma.lastChild.textContent = salud.estado === "operativo" ? " Plataforma operativa" : " Plataforma degradada";
    texto(document.querySelector("#ultima-salud"), `Actualizado ${new Date().toLocaleTimeString("es-BO")}`);
  } catch (error) {
    const plataforma = document.querySelector("#estado-plataforma");
    plataforma.className = "estado estado-degradado";
    plataforma.lastChild.textContent = " No se pudo comprobar";
    texto(document.querySelector("#ultima-salud"), error.message);
  }
}

function crearGrafico(id, configuracion) {
  if (typeof Chart === "undefined") return;
  estadoPanel.graficos[id]?.destroy();
  const contexto = document.querySelector(`#${id}`);
  estadoPanel.graficos[id] = new Chart(contexto, configuracion);
}

async function cargarMetricas() {
  try {
    const metricas = await api("/api/metricas");
    texto(document.querySelector("#metrica-incidentes"), metricas.resumen.incidentes_hoy);
    texto(document.querySelector("#metrica-bloqueos"), metricas.resumen.bloqueos_vigentes);
    texto(document.querySelector("#metrica-tipos"), metricas.resumen.tipos_detectados);
    const comun = { color: "#9fb0c0", font: { family: "system-ui" } };
    crearGrafico("grafico-incidentes", {
      type: "line",
      data: {
        labels: metricas.incidentes_por_hora.map((punto) => punto.hora.slice(11, 16)),
        datasets: [{ label: "Incidentes", data: metricas.incidentes_por_hora.map((punto) => punto.total), borderColor: "#51e1c2", backgroundColor: "rgba(81,225,194,.12)", fill: true, tension: .35, pointRadius: 2 }],
      },
      options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: comun, grid: { display: false } }, y: { beginAtZero: true, ticks: { ...comun, precision: 0 }, grid: { color: "rgba(159,176,192,.08)" } } } },
    });
    const tipos = metricas.tipos_ataque.length ? metricas.tipos_ataque : [{ tipo: "Sin incidentes", total: 1 }];
    crearGrafico("grafico-tipos", {
      type: "doughnut",
      data: { labels: tipos.map((item) => item.tipo), datasets: [{ data: tipos.map((item) => item.total), backgroundColor: ["#51e1c2", "#7d9cff", "#f7bd65", "#ef7186", "#a982e8"], borderWidth: 0 }] },
      options: { maintainAspectRatio: false, cutout: "68%", plugins: { legend: { position: "bottom", labels: { ...comun, boxWidth: 10, usePointStyle: true } } } },
    });
    const ranking = document.querySelector("#top-ips");
    ranking.replaceChildren();
    for (const item of metricas.top_ips) {
      const fila = document.createElement("li");
      const ip = document.createElement("code");
      const total = document.createElement("strong");
      ip.textContent = item.ip;
      total.textContent = item.total;
      fila.append(ip, total);
      ranking.append(fila);
    }
    if (!metricas.top_ips.length) {
      const vacio = document.createElement("li");
      vacio.textContent = "Todavía no hay datos";
      ranking.append(vacio);
    }
  } catch (error) {
    texto(document.querySelector("#metrica-incidentes"), "!");
    console.error(error);
  }
}

async function cargarBloqueos() {
  const cuerpo = document.querySelector("#lista-bloqueos");
  try {
    const baneos = await api("/api/baneos?estado=vigente");
    cuerpo.replaceChildren();
    if (!baneos.length) {
      mostrarError(cuerpo, 6, "No hay bloqueos vigentes.");
      return;
    }
    for (const baneo of baneos) {
      const fila = document.createElement("tr");
      fila.append(celda(baneo.ip), celda(`#${baneo.incidente_id}`), celda(fechaLegible(baneo.inicio)), celda(fechaLegible(baneo.expira)), celda(String(baneo.nivel_reincidencia)));
      const boton = document.createElement("button");
      boton.className = "boton-peligro boton-compacto";
      boton.type = "button";
      boton.textContent = "Liberar";
      boton.addEventListener("click", () => pedirLiberacion(baneo.ip));
      fila.append(celda(boton));
      cuerpo.append(fila);
    }
  } catch (error) {
    mostrarError(cuerpo, 6, error.message);
  }
}

function pedirLiberacion(ip) {
  estadoPanel.ipPendiente = ip;
  texto(document.querySelector("#ip-a-liberar"), ip);
  document.querySelector("#confirmar-liberacion").showModal();
}

async function liberarIp() {
  if (!estadoPanel.ipPendiente) return;
  const boton = document.querySelector("#confirmar-liberar");
  boton.disabled = true;
  try {
    await api(`/api/baneos/${encodeURIComponent(estadoPanel.ipPendiente)}/liberar`, { method: "POST" });
    document.querySelector("#confirmar-liberacion").close();
    mostrarAlerta({ ip_origen: estadoPanel.ipPendiente, tipo_ataque: "Bloqueo liberado", severidad: 1 });
    estadoPanel.ipPendiente = null;
    await Promise.all([cargarBloqueos(), cargarMetricas()]);
  } catch (error) {
    window.alert(error.message);
  } finally {
    boton.disabled = false;
  }
}

function mostrarAlerta(alerta) {
  const contenedor = document.querySelector("#alertas-vivas");
  const aviso = document.createElement("div");
  aviso.className = `alerta-viva alerta-severidad-${alerta.severidad}`;
  const titulo = document.createElement("strong");
  const detalle = document.createElement("span");
  titulo.textContent = alerta.tipo_ataque || "Nuevo incidente";
  detalle.textContent = `${alerta.ip_origen} · ${nombreSeveridad(alerta.severidad)}`;
  aviso.append(titulo, detalle);
  contenedor.replaceChildren(aviso);
  window.setTimeout(() => aviso.remove(), 6500);
}

function conectarTiempoReal() {
  estadoPanel.fuenteEventos?.close();
  const ultimo = Math.max(0, ...estadoPanel.incidentes.map((incidente) => incidente.id));
  const fuente = new EventSource(`/api/eventos?ultimo_id=${ultimo}`);
  estadoPanel.fuenteEventos = fuente;
  const indicador = document.querySelector("#estado-tiempo-real");
  fuente.onopen = () => {
    indicador.className = "estado estado-operativo";
    indicador.lastChild.textContent = " En tiempo real";
  };
  fuente.addEventListener("incidente", async (evento) => {
    const alerta = JSON.parse(evento.data);
    mostrarAlerta(alerta);
    await Promise.all([cargarIncidentes(), cargarMetricas(), cargarBloqueos()]);
  });
  fuente.addEventListener("sesion_expirada", () => window.location.replace("/login"));
  fuente.onerror = () => {
    indicador.className = "estado estado-cargando";
    indicador.lastChild.textContent = " Reconectando";
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  document.querySelector("#filtros-incidentes")?.addEventListener("submit", (evento) => { evento.preventDefault(); cargarIncidentes(); });
  document.querySelector("#limpiar-filtros")?.addEventListener("click", () => { document.querySelector("#filtros-incidentes").reset(); cargarIncidentes(); });
  document.querySelector("#actualizar-salud")?.addEventListener("click", cargarSalud);
  document.querySelector("#actualizar-bloqueos")?.addEventListener("click", cargarBloqueos);
  document.querySelector("[data-cerrar-dialogo]")?.addEventListener("click", () => document.querySelector("#detalle-incidente").close());
  document.querySelector("[data-cancelar-liberacion]")?.addEventListener("click", () => document.querySelector("#confirmar-liberacion").close());
  document.querySelector("#confirmar-liberar")?.addEventListener("click", liberarIp);
  document.body.addEventListener("htmx:afterRequest", (evento) => {
    if (evento.detail.elt?.id === "cerrar-sesion" && evento.detail.successful) {
      window.location.replace("/login");
    }
  });

  await Promise.all([cargarIncidentes(), cargarSalud(), cargarMetricas(), cargarBloqueos()]);
  conectarTiempoReal();
  window.setInterval(() => Promise.all([cargarSalud(), cargarMetricas(), cargarBloqueos()]), 30000);
});
