// Formulario de radicación: validación en el navegador + envío a la API (POST /api/solicitudes).

const formulario = document.getElementById("formulario");
const alerta = document.getElementById("alerta");
const exito = document.getElementById("exito");
const botonEnviar = document.getElementById("enviar");

// Mismas reglas que valida el servidor (docs/requisitos.md, sección 9)
const REGLAS = {
  nombre: (v) => (v.length < 3 || v.length > 100 || !/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$/.test(v) ? "Solo letras y espacios, entre 3 y 100 caracteres" : ""),
  cedula: (v) => (!/^\d{6,10}$/.test(v) ? "Solo números, entre 6 y 10 dígitos" : ""),
  telefono: (v) => (!/^\d{7,10}$/.test(v) ? "Solo números, entre 7 y 10 dígitos" : ""),
  correo: (v) => (!/^[\w.+-]+@[\w-]+(\.[\w-]+)+$/.test(v) ? "Correo no válido (ejemplo: nombre@dominio.com)" : ""),
  direccion: (v) => (v.length < 5 ? "Mínimo 5 caracteres" : ""),
  tipo_id: (v) => (!v ? "Seleccione un tipo de servicio" : ""),
  asunto: (v) => (v.length < 5 ? "Mínimo 5 caracteres" : ""),
  descripcion: (v) => (v.length < 10 ? "Mínimo 10 caracteres" : ""),
};

function marcarError(campo, mensaje) {
  const contenedor = document.getElementById(campo)?.closest(".campo");
  if (!contenedor) return;
  contenedor.classList.toggle("invalido", Boolean(mensaje));
  contenedor.querySelector(".error-campo").textContent = mensaje;
}

async function cargarTipos() {
  try {
    const tipos = await API.pedir("GET", "/api/tipos-servicio");
    const select = document.getElementById("tipo_id");
    tipos.forEach((t) => select.insertAdjacentHTML("beforeend", `<option value="${t.id}">${esc(t.nombre)}</option>`));
  } catch (e) {
    mostrarAlerta(alerta, "error", esc(e.detalle));
  }
}

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultar(alerta);

  const datos = {};
  let hayErrores = false;
  for (const campo of Object.keys(REGLAS)) {
    const valor = document.getElementById(campo).value.trim();
    const mensaje = REGLAS[campo](valor);
    marcarError(campo, mensaje);
    if (mensaje) hayErrores = true;
    datos[campo] = valor;
  }
  if (hayErrores) {
    mostrarAlerta(alerta, "error", "Revise los campos marcados en rojo.");
    return;
  }
  datos.tipo_id = Number(datos.tipo_id);

  botonEnviar.disabled = true;
  try {
    const r = await API.pedir("POST", "/api/solicitudes", datos);
    formulario.classList.add("oculto");
    exito.className = "tarjeta";
    exito.innerHTML = `
      <div class="alerta exito">✅ ${esc(r.mensaje)}</div>
      <p>Su número de radicado es:</p>
      <div class="radicado-grande">${esc(r.radicado)}</div>
      <p class="ayuda">Anótelo: lo necesitará para consultar el estado y la respuesta de su solicitud.</p>
      <p>Estado actual: ${etiquetaEstado(r.estado)}</p>
      <div class="acciones-form">
        <a class="boton" href="consultar.html?radicado=${encodeURIComponent(r.radicado)}">Consultar esta solicitud</a>
	<button type="button" class="boton secundario" onclick="navigator.clipboard.writeText('${r.radicado}'); this.textContent='✔ Copiado'">📋 Copiar número</button>
        <button type="button" class="boton secundario" onclick="window.print()">🖨️ Imprimir comprobante</button>
        <a class="boton secundario" href="radicar.html">Radicar otra</a>
      </div>`;
  } catch (e) {
    // Errores devueltos por el servidor (validación del backend)
    (e.errores || []).forEach((err) => marcarError(err.campo, err.mensaje));
    mostrarAlerta(alerta, "error", esc(e.detalle));
  } finally {
    botonEnviar.disabled = false;
  }
});

cargarTipos();
