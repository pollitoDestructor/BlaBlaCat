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
    try {
        const usuario_id = localStorage.getItem("usuario_id")
        const url = usuario_id ? `${API}?usuario_id=${usuario_id}` : API
        const solicitudes = await apiFetch(url)
        renderListaSolicitudes(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function crearSolicitud(datos) {
    // solicitudes.js — en crearSolicitud

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

function mostrarError(mensaje) {
    const lista = document.getElementById("lista-solicitudes")
    if (lista) lista.innerHTML = `<li class="error">${mensaje}</li>`
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
