// static/js/solicitudes.js

const API = "/api/solicitudes"

// ─── CRUD ─────────────────────────────────────────────────

async function cargarSolicitudes() {
    await Promise.all([cargarMisSolicitudes(), cargarSolicitudesDisponibles()])
}

async function cargarMisSolicitudes() {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        const solicitudes = await apiFetch(`${API}?usuario_id=${usuario_id}`)
        renderListaSolicitudes(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function cargarSolicitudesDisponibles() {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        const solicitudes = await apiFetch(
            `${API}?exclude_usuario_id=${usuario_id}&current_usuario_id=${usuario_id}`
        )
        renderListaSolicitudesAbiertas(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function crearSolicitud(datos) {
    try {
        await apiFetch(API, {
            method: "POST",
            body: JSON.stringify({
                usuario_id:       datos.usuario_id,
                nombre:           datos.nombre,
                especie:          datos.especie,
                raza:             datos.raza,
                foto_url:         datos.foto_url,
                horario_inicio:   datos.horario_inicio,
                horario_fin:      datos.horario_fin,
                especificaciones: datos.especificaciones,
            })
        })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

async function eliminarSolicitud(id) {
    try {
        await apiFetch(`${API}/${id}`, { method: "DELETE" })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

async function modificarSolicitud(id) {
    const usuario_id = localStorage.getItem("usuario_id")
    const nombre  = prompt("Nuevo nombre:")
    const especie = prompt("Nueva especie:")
    const raza    = prompt("Nueva raza:")
    if (nombre === null && especie === null && raza === null) return
    const payload = { usuario_id }
    if (nombre  && nombre  !== "") payload.nombre  = nombre
    if (especie && especie !== "") payload.especie = especie
    if (raza    && raza    !== "") payload.raza    = raza
    try {
        await apiFetch(`${API}/${id}`, { method: "PUT", body: JSON.stringify(payload) })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

async function registrarseSolicitud(id) {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        await apiFetch(`${API}/${id}/registrarse`, {
            method: "POST",
            body: JSON.stringify({ usuario_id }),
        })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

async function cancelarRegistroSolicitud(id) {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        await apiFetch(`${API}/${id}/registrarse`, {
            method: "DELETE",
            body: JSON.stringify({ usuario_id }),
        })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

async function verInscritos(solicitudId) {
    try {
        const inscritos  = await apiFetch(`${API}/${solicitudId}/inscritos`)
        renderModalInscritos(solicitudId, inscritos)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function aceptarCuidador(solicitudId, cuidadorId) {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        await apiFetch(`${API}/${solicitudId}/aceptar`, {
            method: "POST",
            body: JSON.stringify({ usuario_id, cuidador_id: cuidadorId }),
        })
        cerrarModal()
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

// ─── Render ───────────────────────────────────────────────

function formatFecha(iso) {
    if (!iso) return "—"
    return iso.replace("T", " ").slice(0, 16)
}

function renderListaSolicitudes(solicitudes) {
    const lista = document.getElementById("lista-solicitudes")
    if (!lista) return
    if (solicitudes.length === 0) {
        lista.innerHTML = "<li class='vacio'>No tienes solicitudes todavía.</li>"
        return
    }
    lista.innerHTML = solicitudes.map(s => `
        <li class="solicitud-item">
            <div class="solicitud-info">
                <strong>${s.nombre}</strong> — ${s.especie}${s.raza ? ` (${s.raza})` : ""}
                ${s.horario_inicio ? `<small>📅 ${formatFecha(s.horario_inicio)} → ${formatFecha(s.horario_fin)}</small>` : ""}
                ${s.cuidador_id
                    ? `<span class="badge badge-aceptado">✅ Cuidador asignado</span>`
                    : `<span class="badge badge-pendiente">⏳ Sin cuidador</span>`}
            </div>
            <div class="solicitud-acciones">
                ${s.cuidador_id
                    ? `<button onclick="navigate(event, '/perfil/${s.cuidador_id}?solicitud=${s.id}')">Ver cuidador</button>`
                    : `<button onclick="verInscritos(${s.id})">Ver inscritos</button>`}
                <button onclick="modificarSolicitud(${s.id})">Modificar</button>
                <button class="btn-eliminar" onclick="eliminarSolicitud(${s.id})">Eliminar</button>
            </div>
        </li>
    `).join("")
}

function renderListaSolicitudesAbiertas(solicitudes) {
    const lista = document.getElementById("lista-solicitudes-abiertas")
    if (!lista) return
    if (solicitudes.length === 0) {
        lista.innerHTML = "<li class='vacio'>No hay solicitudes disponibles.</li>"
        return
    }
    lista.innerHTML = solicitudes.map(s => `
        <li class="solicitud-item">
            <div class="solicitud-info">
                <strong>${s.nombre}</strong> — ${s.especie}${s.raza ? ` (${s.raza})` : ""}
                ${s.horario_inicio ? `<small>📅 ${formatFecha(s.horario_inicio)} → ${formatFecha(s.horario_fin)}</small>` : ""}
                ${s.cuidador_id ? `<span class="badge badge-aceptado">✅ Cuidador asignado</span>` : ""}
            </div>
            <div class="solicitud-acciones">
                ${!s.cuidador_id
                    ? s.registrado
                        ? `<button class="btn-secundario" onclick="cancelarRegistroSolicitud(${s.id})">Cancelar</button>`
                        : `<button onclick="registrarseSolicitud(${s.id})">Ofrecerse</button>`
                    : ""}
            </div>
        </li>
    `).join("")
}

function renderModalInscritos(solicitudId, inscritos) {
    let modal = document.getElementById("modal-inscritos")
    if (modal) modal.remove()
    modal = document.createElement("div")
    modal.id = "modal-inscritos"
    modal.className = "modal-overlay"
    const cuerpo = inscritos.length === 0
        ? "<p class='vacio'>Nadie se ha inscrito todavía.</p>"
        : `<ul class="lista-inscritos">${inscritos.map(i => `
            <li>
                <span>${i.username}</span>
                <button onclick="aceptarCuidador(${solicitudId}, ${i.usuario_id})">Aceptar</button>
            </li>`).join("")}</ul>`
    modal.innerHTML = `
        <div class="modal">
            <h3>Candidatos inscritos</h3>
            ${cuerpo}
            <button class="btn-secundario" onclick="cerrarModal()" style="margin-top:1rem">Cerrar</button>
        </div>`
    document.body.appendChild(modal)
}

function cerrarModal() {
    const modal = document.getElementById("modal-inscritos")
    if (modal) modal.remove()
}

// ─── Próximas (vista pública) ─────────────────────────────

async function cargarProximas() {
    try {
        const solicitudes = await apiFetch(`${API}/proximas`)
        const lista = document.getElementById("lista-proximas")
        if (!lista) return
        if (solicitudes.length === 0) {
            lista.innerHTML = "<li class='vacio'>No hay solicitudes próximas.</li>"
            return
        }
        lista.innerHTML = solicitudes.map(s => `
            <li class="solicitud-item">
                <div class="solicitud-info">
                    <strong>${s.nombre}</strong> — ${s.especie}${s.raza ? ` (${s.raza})` : ""}
                    ${s.horario_inicio ? `<small>📅 ${formatFecha(s.horario_inicio)} → ${formatFecha(s.horario_fin)}</small>` : ""}
                    ${s.especificaciones ? `<small>${s.especificaciones}</small>` : ""}
                </div>
            </li>
        `).join("")
    } catch (error) {
        console.error("Error cargando próximas:", error.message)
    }
}

function mostrarError(mensaje) {
    const lista = document.getElementById("lista-solicitudes")
        || document.getElementById("lista-solicitudes-abiertas")
    if (!lista) return
    const li = document.createElement("li")
    li.className = "error-msg"
    li.textContent = mensaje
    lista.appendChild(li)
    setTimeout(() => li.remove(), 3000)
}
