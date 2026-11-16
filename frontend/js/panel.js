// Panel del personal: listado, detalle, acciones según rol y resumen consolidado.

const usuario = API.usuario();
if (!API.token() || !usuario) location.href = "login.html";

const esCoordinador = usuario?.rol === "COORDINADOR";
const alerta = document.getElementById("alerta");
const vistas = {
  lista: document.getElementById("vista-lista"),
  detalle: document.getElementById("vista-detalle"),
  resumen: document.getElementById("vista-resumen"),
};
let filtroEstado = "";

document.getElementById("nombre-usuario").textContent = usuario?.nombre || "";
document.getElementById("rol-usuario").textContent = esCoordinador ? "Coordinación" : "Encargado de atención";
document.getElementById("titulo-lista").textContent = esCoordinador ? "Todas las solicitudes" : "Mis solicitudes asignadas";
if (esCoordinador) document.getElementById("tab-resumen").classList.remove("oculto");

/** Ejecuta una petición y, si la sesión venció (401), vuelve al inicio de sesión. */
async function pedir(metodo, ruta, cuerpo) {
  try {
    return await API.pedir(metodo, ruta, cuerpo);
  } catch (e) {
    if (e.status === 401) {
      API.borrarSesion();
      location.href = "login.html";
    }
    throw e;
  }
}

function mostrarVista(nombre) {
  Object.entries(vistas).forEach(([clave, el]) => el.classList.toggle("oculto", clave !== nombre));
  document.querySelectorAll("#pestanas button").forEach((b) =>
    b.classList.toggle("activo", b.dataset.vista === (nombre === "detalle" ? "lista" : nombre))
  );
  ocultar(alerta);
}

/* ---------- Listado ---------- */
async function cargarLista() {
  mostrarVista("lista");
  const tabla = document.getElementById("tabla");
  tabla.innerHTML = `<tr><td colspan="8" class="vacio">Cargando…</td></tr>`;
  try {
    const consulta = filtroEstado ? `?estado=${filtroEstado}` : "";
    const filas = await pedir("GET", `/api/gestion/solicitudes${consulta}`);
    tabla.innerHTML = filas.length
      ? filas
          .map(
            (s) => `<tr>
              <td><strong>${esc(s.radicado)}</strong></td>
              <td>${esc(s.solicitante)}</td>
              <td>${esc(s.tipo)}</td>
              <td>${esc(s.asunto)}</td>
              <td>${etiquetaEstado(s.estado)}</td>
              <td>${esc(s.encargado || "Sin asignar")}</td>
              <td>${formatoFecha(s.fecha_creacion)}</td>
              <td><button class="boton secundario" style="padding:.25rem .7rem" data-id="${s.id}">Ver</button></td>
            </tr>`
          )
          .join("")
      : `<tr><td colspan="8" class="vacio">No hay solicitudes para mostrar.</td></tr>`;
  } catch (e) {
    tabla.innerHTML = "";
    mostrarAlerta(alerta, "error", esc(e.detalle));
  }
}

document.getElementById("tabla").addEventListener("click", (evento) => {
  const id = evento.target.dataset.id;
  if (id) verDetalle(id);
});

document.getElementById("filtros").addEventListener("click", (evento) => {
  if (evento.target.tagName !== "BUTTON") return;
  filtroEstado = evento.target.dataset.estado;
  document.querySelectorAll("#filtros button").forEach((b) => b.classList.toggle("activo", b === evento.target));
  cargarLista();
});

/* ---------- Detalle y acciones ---------- */
function bloqueTexto(id, titulo, ayuda, textoBoton, claseBoton = "") {
  return `<div class="accion-bloque">
      <h4>${titulo}</h4>
      <p class="ayuda">${ayuda}</p>
      <textarea id="${id}" maxlength="2000" placeholder="Mínimo 10 caracteres"></textarea>
      <div class="acciones-form"><button class="boton ${claseBoton}" data-accion="${id}">${textoBoton}</button></div>
    </div>`;
}

async function formularioAcciones(s) {
  if (s.estado === "FINALIZADA" || s.estado === "CERRADA") {
    return `<p class="ayuda">La solicitud está ${esc(s.estado_etiqueta.toLowerCase())}: no admite más acciones.</p>`;
  }
  let html = "";
  if (esCoordinador) {
    if (["RECIBIDA", "ASIGNADA"].includes(s.estado)) {
      const encargados = await pedir("GET", "/api/usuarios/encargados");
      html += `<div class="accion-bloque">
          <h4>${s.encargado ? "Reasignar" : "Asignar"} encargado</h4>
          <p class="ayuda">La solicitud pasará a estado Asignada.</p>
          <select id="encargado">${encargados
            .map((e) => `<option value="${e.id}" ${s.encargado?.id === e.id ? "selected" : ""}>${esc(e.nombre)} (${e.solicitudes_activas} activas)</option>`)
            .join("")}</select>
          <div class="acciones-form"><button class="boton" data-accion="asignar">Asignar</button></div>
        </div>`;
    }
  } else {
    if (s.estado === "ASIGNADA") {
      html += bloqueTexto("evaluar", "Evaluar solicitud", "Registre el resultado de la revisión. La solicitud pasará a En gestión.", "Evaluar e iniciar gestión");
    }
    if (s.estado === "EN_GESTION") {
      html += bloqueTexto("seguimiento", "Agregar seguimiento", "Nota visible en el historial de la solicitud.", "Agregar seguimiento", "secundario");
      html += bloqueTexto("finalizar", "Responder y finalizar", "La respuesta será visible para el solicitante.", "Responder y finalizar", "exito");
    }
  }
  html += bloqueTexto("cerrar", "Cerrar solicitud", "Úselo cuando la solicitud no procede. El motivo es obligatorio y visible para el solicitante.", "Cerrar solicitud", "peligro");
  return html;
}

async function verDetalle(id) {
  mostrarVista("detalle");
  const vista = vistas.detalle;
  vista.innerHTML = `<div class="tarjeta">Cargando…</div>`;
  try {
    const s = await pedir("GET", `/api/gestion/solicitudes/${id}`);
    const final =
      s.estado === "FINALIZADA"
        ? `<div class="caja-respuesta"><strong>Respuesta</strong><p>${esc(s.respuesta)}</p></div>`
        : s.estado === "CERRADA"
          ? `<div class="caja-cierre"><strong>Motivo de cierre</strong><p>${esc(s.motivo_cierre)}</p></div>`
          : "";
    vista.innerHTML = `
      <button class="boton secundario" id="volver" style="margin-bottom:1rem">← Volver al listado</button>
      <div id="alerta-detalle" class="oculto"></div>
      <div class="dos-columnas">
        <div>
          <section class="tarjeta">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
              <h2>Radicado ${esc(s.radicado)}</h2>${etiquetaEstado(s.estado)}
            </div>
            ${lineaProgreso(s.estado)}
            <dl class="datos">
              <div><dt>Tipo de servicio</dt><dd>${esc(s.tipo)}</dd></div>
              <div><dt>Asunto</dt><dd>${esc(s.asunto)}</dd></div>
              <div><dt>Encargado</dt><dd>${esc(s.encargado?.nombre || "Sin asignar")}</dd></div>
              <div><dt>Radicada</dt><dd>${formatoFecha(s.fecha_creacion)}</dd></div>
            </dl>
            <h4 style="margin-top:1rem">Descripción</h4>
            <p>${esc(s.descripcion)}</p>
            ${final}
          </section>
          <section class="tarjeta">
            <h3>Solicitante</h3>
            <dl class="datos">
              <div><dt>Nombre</dt><dd>${esc(s.solicitante.nombre)}</dd></div>
              <div><dt>Cédula</dt><dd>${esc(s.solicitante.cedula)}</dd></div>
              <div><dt>Teléfono</dt><dd>${esc(s.solicitante.telefono)}</dd></div>
              <div><dt>Correo</dt><dd>${esc(s.solicitante.correo)}</dd></div>
              <div><dt>Dirección</dt><dd>${esc(s.solicitante.direccion)}</dd></div>
            </dl>
          </section>
          <section class="tarjeta">
            <h3>Historial de atención (trazabilidad)</h3>
            ${lineaTiempo(s.historial, true)}
          </section>
        </div>
        <aside class="tarjeta">
          <h3>Acciones</h3>
          ${await formularioAcciones(s)}
        </aside>
      </div>`;
    document.getElementById("volver").addEventListener("click", cargarLista);
    vista.querySelectorAll("[data-accion]").forEach((boton) =>
      boton.addEventListener("click", () => ejecutarAccion(s, boton.dataset.accion, boton))
    );
  } catch (e) {
    vista.innerHTML = `<button class="boton secundario" id="volver">← Volver al listado</button>
      <div class="alerta error" style="margin-top:1rem">${esc(e.detalle)}</div>`;
    document.getElementById("volver").addEventListener("click", cargarLista);
  }
}

const CAMPOS_ACCION = { evaluar: "observacion", seguimiento: "nota", finalizar: "respuesta", cerrar: "motivo" };
const MENSAJES_EXITO = {
  asignar: "Solicitud asignada correctamente.",
  evaluar: "Evaluación registrada. La solicitud está en gestión.",
  seguimiento: "Seguimiento registrado en el historial.",
  finalizar: "Solicitud respondida y finalizada.",
  cerrar: "Solicitud cerrada.",
};

async function ejecutarAccion(s, accion, boton) {
  const alertaDetalle = document.getElementById("alerta-detalle");
  let cuerpo;
  if (accion === "asignar") {
    cuerpo = { encargado_id: Number(document.getElementById("encargado").value) };
  } else {
    const texto = document.getElementById(accion).value.trim();
    if (texto.length < 10) {
      mostrarAlerta(alertaDetalle, "error", "El texto debe tener al menos 10 caracteres.");
      return;
    }
    if (accion === "cerrar" && !confirm("¿Confirma que desea cerrar la solicitud? Esta acción no se puede deshacer.")) return;
    if (accion === "finalizar" && !confirm("¿Confirma la respuesta? La solicitud quedará finalizada.")) return;
    cuerpo = { [CAMPOS_ACCION[accion]]: texto };
  }
  boton.disabled = true;
  try {
    await pedir("POST", `/api/gestion/solicitudes/${s.id}/${accion}`, cuerpo);
    await verDetalle(s.id);
    mostrarAlerta(document.getElementById("alerta-detalle"), "exito", MENSAJES_EXITO[accion]);
  } catch (e) {
    const extra = (e.errores || []).map((x) => esc(x.mensaje)).join("<br>");
    mostrarAlerta(alertaDetalle, "error", esc(e.detalle) + (extra ? `<br>${extra}` : ""));
    boton.disabled = false;
  }
}

/* ---------- Resumen consolidado (coordinación) ---------- */
function barras(filas, clave, etiqueta) {
  const maximo = Math.max(1, ...filas.map((f) => f[clave]));
  return `<div class="barras">${filas
    .map(
      (f) => `<div class="barra-fila"><span>${esc(f[etiqueta])}</span>
        <div class="barra-fondo"><div class="barra-relleno" style="width:${(f[clave] / maximo) * 100}%"></div></div>
        <strong>${f[clave]}</strong></div>`
    )
    .join("")}</div>`;
}

async function cargarResumen() {
  mostrarVista("resumen");
  const vista = vistas.resumen;
  vista.innerHTML = `<div class="tarjeta">Cargando…</div>`;
  try {
    const r = await pedir("GET", "/api/reportes/resumen");
    const kpi = (valor, texto) => `<div class="kpi"><div class="valor">${valor}</div><div class="etiqueta">${texto}</div></div>`;
    vista.innerHTML = `
      <div class="kpis">
        ${kpi(r.total, "Solicitudes totales")}
        ${kpi(r.pendientes, "Pendientes de atención")}
        ${kpi(r.sin_asignar, "Sin asignar")}
        ${kpi(r.finalizadas, "Finalizadas")}
        ${kpi(r.cerradas, "Cerradas")}
        ${kpi(r.tiempo_promedio_atencion_horas ?? "—", "Horas promedio de atención")}
      </div>
      <div class="dos-columnas" style="grid-template-columns:1fr 1fr">
        <section class="tarjeta"><h3>Solicitudes por estado</h3>${barras(r.por_estado, "cantidad", "etiqueta")}</section>
        <section class="tarjeta"><h3>Solicitudes por tipo de servicio</h3>${barras(r.por_tipo, "cantidad", "tipo")}</section>
      </div>
      <section class="tarjeta">
        <h3>Carga por encargado</h3>
        <div class="tabla-contenedor"><table>
          <thead><tr><th>Encargado</th><th>Activas</th><th>Finalizadas</th><th>Cerradas</th><th>Total asignadas</th></tr></thead>
          <tbody>${r.por_encargado
            .map((e) => `<tr><td>${esc(e.encargado)}</td><td>${e.activas}</td><td>${e.finalizadas}</td><td>${e.cerradas}</td><td>${e.total}</td></tr>`)
            .join("")}</tbody>
        </table></div>
      </section>`;
  } catch (e) {
    vista.innerHTML = "";
    mostrarAlerta(alerta, "error", esc(e.detalle));
  }
}

document.getElementById("pestanas").addEventListener("click", (evento) => {
  const vista = evento.target.dataset.vista;
  if (vista === "lista") cargarLista();
  if (vista === "resumen") cargarResumen();
});

document.getElementById("salir").addEventListener("click", async () => {
  try {
    await API.pedir("POST", "/api/auth/logout");
  } catch {
    /* si la sesión ya venció, igual se sale */
  }
  API.borrarSesion();
  location.href = "login.html";
});

cargarLista();
