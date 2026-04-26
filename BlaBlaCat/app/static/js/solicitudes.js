// static/js/solicitudes.js

const API = "/api/solicitudes"

// ─── Helpers ──────────────────────────────────────────────

function getToken() {
    return localStorage.getItem("token")
}

async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${getToken()}`,
            ...options.headers,
        },
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || "Error en la petición")
    }

    return data
}

// ─── CRUD ─────────────────────────────────────────────────

async function cargarSolicitudes() {
    await Promise.all([cargarMisSolicitudes(), cargarSolicitudesDisponibles()])
}

async function cargarMisSolicitudes() {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        const url = usuario_id ? `${API}?usuario_id=${usuario_id}` : API
        const solicitudes = await apiFetch(url)
        renderListaSolicitudes(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function cargarSolicitudesDisponibles() {
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        const url = usuario_id
            ? `${API}?exclude_usuario_id=${usuario_id}&current_usuario_id=${usuario_id}`
            : API
        const solicitudes = await apiFetch(url)
        renderListaSolicitudesAbiertas(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function crearSolicitud(datos) {
    try {
        datos.usuario_id = localStorage.getItem("usuario_id")
        await apiFetch(API, {
            method: "POST",
            body: JSON.stringify({
                usuario_id: datos.usuario_id,
                nombre:     datos.nombre,
                especie:    datos.especie,
                raza:       datos.raza,
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

// ─── Render ───────────────────────────────────────────────

function renderListaSolicitudes(solicitudes) {
    const lista = document.getElementById("lista-solicitudes")

    if (!lista) return

    if (solicitudes.length === 0) {
        lista.innerHTML = "<li>No tienes solicitudes todavía.</li>"
        return
    }

    lista.innerHTML = solicitudes.map(s => `
        <li>
            <strong>${s.nombre}</strong> — ${s.especie} (${s.raza})
            <button onclick="modificarSolicitud(${s.id})">Modificar</button>
            <button onclick="eliminarSolicitud(${s.id})">Eliminar</button>
        </li>
    `).join("")
}

function renderListaSolicitudesAbiertas(solicitudes) {
    const lista = document.getElementById("lista-solicitudes-abiertas")

    if (!lista) return

    if (solicitudes.length === 0) {
        lista.innerHTML = "<li>No hay solicitudes disponibles por el momento.</li>"
        return
    }

    lista.innerHTML = solicitudes.map(s => `
        <li>
            <strong>${s.nombre}</strong> — ${s.especie} (${s.raza})
            ${s.registrado
                ? `<button onclick="cancelarRegistroSolicitud(${s.id})">Cancelar registro</button>`
                : `<button onclick="registrarseSolicitud(${s.id})">Registrarse</button>`}
        </li>
    `).join("")
}

function mostrarError(mensaje) {
    const lista = document.getElementById("lista-solicitudes") || document.getElementById("lista-solicitudes-abiertas")
    if (lista) {
        const errorLi = document.createElement("li")
        errorLi.className = "error"
        errorLi.textContent = mensaje
        lista.appendChild(errorLi)
        setTimeout(() => {
            errorLi.remove()
        }, 3000)
    }
}





async function modificarSolicitud(id) {
    const usuario_id = localStorage.getItem('usuario_id')
    const nombre = prompt('Nuevo nombre:')
    const especie = prompt('Nueva especie:')
    const raza = prompt('Nueva raza:')

    if (nombre === null && especie === null && raza === null) {
        return
    }

    const payload = {
        usuario_id,
    }
    if (nombre && nombre !== '') payload.nombre = nombre
    if (especie && especie !== '') payload.especie = especie
    if (raza && raza !== '') payload.raza = raza

    try {
        await apiFetch(`${API}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(payload),
        })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}
