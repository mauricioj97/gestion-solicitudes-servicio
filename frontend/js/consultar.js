// Consulta pública por número de radicado (GET /api/solicitudes/consulta/{radicado}).

const campoRadicado = document.getElementById("radicado");
const alerta = document.getElementById("alerta");
const resultado = document.getElementById("resultado");

async function consultar(radicado) {
  ocultar(alerta);
  resultado.innerHTML = "";
  if (!/^\d{8}$/.test(radicado)) {
    mostrarAlerta(alerta, "error", "El número de radicado tiene 8 dígitos.");
    return;
  }
  try {
    const s = await API.pedir("GET", `/api/solicitudes/consulta/${encodeURIComponent(radicado)}`);
    history.replaceState(null, "", `?radicado=${encodeURIComponent(radicado)}`);
    let final = "";
    if (s.estado === "FINALIZADA") {
      final = `<div class="caja-respuesta"><strong>Respuesta de la organización</strong><p>${esc(s.respuesta)}</p>
               <span class="ayuda">Finalizada el ${formatoFecha(s.fecha_cierre)}</span></div>`;
    } else if (s.estado === "CERRADA") {
      final = `<div class="caja-cierre"><strong>Solicitud cerrada</strong><p>Motivo: ${esc(s.motivo_cierre)}</p>
               <span class="ayuda">Cerrada el ${formatoFecha(s.fecha_cierre)}</span></div>`;
    } else {
      final = `<div class="alerta info" style="margin-top:1rem">Su solicitud está en proceso. Vuelva a consultar más adelante.</div>`;
    }
    resultado.innerHTML = `
      <section class="tarjeta">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
          <h2>Radicado ${esc(s.radicado)}</h2>${etiquetaEstado(s.estado)}
        </div>
        ${lineaProgreso(s.estado)}
        <dl class="datos">
          <div><dt>Solicitante</dt><dd>${esc(s.solicitante)}</dd></div>
          <div><dt>Tipo de servicio</dt><dd>${esc(s.tipo)}</dd></div>
          <div><dt>Asunto</dt><dd>${esc(s.asunto)}</dd></div>
          <div><dt>Radicada</dt><dd>${formatoFecha(s.fecha_creacion)}</dd></div>
          <div><dt>Última actualización</dt><dd>${formatoFecha(s.fecha_actualizacion)}</dd></div>
        </dl>
        ${final}
      </section>
      <section class="tarjeta">
        <h3>Historial de atención</h3>
        ${lineaTiempo(s.historial, false)}
      </section>`;
  } catch (e) {
    mostrarAlerta(alerta, "error", esc(e.detalle));
  }
}

document.getElementById("buscar").addEventListener("submit", (evento) => {
  evento.preventDefault();
  consultar(campoRadicado.value.trim());
});

const radicadoUrl = new URLSearchParams(location.search).get("radicado");
if (radicadoUrl) {
  campoRadicado.value = radicadoUrl;
  consultar(radicadoUrl);
}
