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
        const solicitudes = await apiFetch(API)
        renderListaSolicitudes(solicitudes)
    } catch (error) {
        mostrarError(error.message)
    }
}

async function crearSolicitud() {
    try {
        await apiFetch(API, { method: "POST", body: JSON.stringify({}) })
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
            <span>Solicitud #${s.id} — ${s.created_at}</span>
            <button onclick="eliminarSolicitud(${s.id})">Eliminar</button>
        </li>
    `).join("")
}

function mostrarError(mensaje) {
    const lista = document.getElementById("lista-solicitudes")
    if (lista) lista.innerHTML = `<li class="error">${mensaje}</li>`
}