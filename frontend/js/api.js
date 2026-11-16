// Funciones compartidas: comunicación con la API y utilidades de la interfaz.

const API = {
  token() {
    return sessionStorage.getItem("token");
  },
  usuario() {
    return JSON.parse(sessionStorage.getItem("usuario") || "null");
  },
  guardarSesion(datos) {
    sessionStorage.setItem("token", datos.token);
    sessionStorage.setItem("usuario", JSON.stringify(datos.usuario));
  },
  borrarSesion() {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");
  },

  /** Envía una petición HTTP a la API. Si falla, lanza {status, detalle, errores}. */
  async pedir(metodo, ruta, cuerpo) {
    const opciones = { method: metodo, headers: {} };
    if (cuerpo !== undefined) {
      opciones.headers["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(cuerpo);
    }
    const token = this.token();
    if (token) opciones.headers["Authorization"] = `Bearer ${token}`;

    let respuesta;
    try {
      respuesta = await fetch(ruta, opciones);
    } catch {
      throw { status: 0, detalle: "No hay conexión con el servidor. Verifique que la aplicación esté en ejecución." };
    }
    if (respuesta.status === 204) return null;
    const datos = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) {
      throw { status: respuesta.status, detalle: datos.detalle || "Ocurrió un error inesperado", errores: datos.errores || [] };
    }
    return datos;
  },
};

/** Escapa texto para insertarlo de forma segura en HTML. */
function esc(texto) {
  return String(texto ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

const ETIQUETAS_ESTADO = {
  RECIBIDA: "Recibida",
  ASIGNADA: "Asignada",
  EN_GESTION: "En gestión",
  FINALIZADA: "Finalizada",
  CERRADA: "Cerrada",
};

function etiquetaEstado(estado) {
  return `<span class="estado ${esc(estado)}">${esc(ETIQUETAS_ESTADO[estado] || estado)}</span>`;
}

function formatoFecha(texto) {
  if (!texto) return "—";
  const fecha = new Date(texto.replace(" ", "T"));
  return fecha.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}

function mostrarAlerta(elemento, tipo, mensaje) {
  elemento.className = `alerta ${tipo}`;
  elemento.innerHTML = mensaje;
}

function ocultar(elemento) {
  elemento.className = "oculto";
  elemento.innerHTML = "";
}

/** Barra de progreso del flujo: Recibida → Asignada → En gestión → Finalizada. */
function lineaProgreso(estado) {
  const pasos = ["RECIBIDA", "ASIGNADA", "EN_GESTION", "FINALIZADA"];
  if (estado === "CERRADA") {
    return `<div class="progreso"><div class="paso hecho cerrado">Cerrada con motivo</div></div>`;
  }
  const actual = pasos.indexOf(estado);
  return `<div class="progreso">${pasos
    .map((p, i) => `<div class="paso ${i <= actual ? "hecho" : ""}">${ETIQUETAS_ESTADO[p]}</div>`)
    .join("")}</div>`;
}

/** Historial de acciones en forma de línea de tiempo. */
function lineaTiempo(historial, mostrarResponsable) {
  if (!historial.length) return `<p class="ayuda">Sin acciones registradas.</p>`;
  return `<ol class="historial">${historial
    .map(
      (h) => `<li>
        <div class="cabecera"><strong>${esc(h.accion_etiqueta)}</strong> ${etiquetaEstado(h.estado_nuevo)}
          <span class="fecha">${formatoFecha(h.fecha)}${mostrarResponsable ? " · " + esc(h.responsable) : ""}</span></div>
        <p>${esc(h.descripcion)}</p>
      </li>`
    )
    .join("")}</ol>`;
}
