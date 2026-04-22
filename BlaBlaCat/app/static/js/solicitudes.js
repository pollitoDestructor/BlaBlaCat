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

async function crearSolicitud(datos) {
    try {
        datos.usuario_id = localStorage.getItem("usuario_id")
        await apiFetch(API, {
            method: "POST",
            body: JSON.stringify({
                usuario_id:       datos.usuario_id,
                nombre:           datos.nombre,
                especie:          datos.especie,
                raza:             datos.raza,
                especificaciones: datos.especificaciones,
                horario_inicio:   datos.horario_inicio,
                horario_fin:      datos.horario_fin,
            })
        })
        await cargarSolicitudes()
    } catch (error) {
        mostrarError(error.message)
    }
}

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
            <button onclick="eliminarSolicitud">Eliminar</button>
        </li>
    `).join("")
}

function mostrarError(mensaje) {
    const lista = document.getElementById("lista-solicitudes")
    if (lista) lista.innerHTML = `<li class="error">${mensaje}</li>`
}

function renderProximas() {
    app.innerHTML = ""
    const contenido = cloneTemplate("tpl-proximas")
    app.appendChild(contenido)
    cargarProximas()
}

async function cargarProximas() {
    try {
        const solicitudes = await apiFetch(`${API}/proximas`)
        const lista = document.getElementById("lista-proximas")
        if (!lista) return
        if (solicitudes.length === 0) {
            lista.innerHTML = "<li>No hay solicitudes próximas.</li>"
            return
        }
        lista.innerHTML = solicitudes.map(s => `
            <li>
                <strong>${s.nombre}</strong> — ${s.especie} (${s.raza})
                <p>Inicio: ${s.horario_inicio}</p>
                <p>Fin: ${s.horario_fin}</p>
            </li>
        `).join("")
    } catch (error) {
        console.error("Error:", error.message)
    }
}