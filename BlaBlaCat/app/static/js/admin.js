// static/js/admin.js

const ADMIN_API = "/api/admin"

// ─── Guard ────────────────────────────────────────────────
// Redirige si el usuario no es admin. Llamar al inicio de cada renderAdmin*

function requireAdminFrontend() {
    if (localStorage.getItem("rol") !== "administrador") {
        window.history.pushState({}, "", "/")
        render("/")
        return false
    }
    return true
}

// ─── Helpers ──────────────────────────────────────────────

function adminFetch(url, options = {}) {
    const uid = localStorage.getItem("usuario_id")
    const sep = url.includes("?") ? "&" : "?"
    return apiFetch(`${url}${sep}usuario_id=${uid}`, options)
}

// ─── Vista: lista de usuarios (#276 / #298) ───────────────

async function renderAdminUsuarios() {
    if (!requireAdminFrontend()) return

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-admin-usuarios"))

    await cargarListaUsuarios()
}

async function cargarListaUsuarios() {
    try {
        const usuarios = await adminFetch(`${ADMIN_API}/usuarios`)
        const lista    = document.getElementById("lista-admin-usuarios")
        if (!lista) return

        if (usuarios.length === 0) {
            lista.innerHTML = "<tr><td colspan='5'>No hay usuarios registrados.</td></tr>"
            return
        }

        lista.innerHTML = usuarios.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.username}</td>
                <td>${u.email}</td>
                <td><span class="badge badge-${u.rol}">${u.rol}</span></td>
                <td>
                    <button
                        onclick="confirmarEliminarUsuario(${u.id}, '${u.username}')"
                        ${u.id == localStorage.getItem("usuario_id") ? "disabled title='No puedes eliminarte a ti mismo'" : ""}
                        class="btn-danger">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join("")

    } catch (error) {
        document.getElementById("lista-admin-usuarios").innerHTML =
            `<tr><td colspan='5' class="error-msg">${error.message}</td></tr>`
    }
}

function confirmarEliminarUsuario(id, username) {
    if (!confirm(`¿Eliminar al usuario "${username}" y todos sus datos? Esta acción no se puede deshacer.`)) return
    eliminarUsuario(id)
}

async function eliminarUsuario(id) {
    try {
        const uid = localStorage.getItem("usuario_id")
        await apiFetch(`${ADMIN_API}/usuarios/${id}?usuario_id=${uid}`, { method: "DELETE" })
        await cargarListaUsuarios()   // refresca la tabla
    } catch (error) {
        alert("Error al eliminar: " + error.message)
    }
}

// ─── Vista: catálogo de mascotas/solicitudes (#300) ───────

async function renderAdminSolicitudes() {
    if (!requireAdminFrontend()) return

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-admin-solicitudes"))

    await cargarCatalogoSolicitudes()
}

async function cargarCatalogoSolicitudes() {
    try {
        const solicitudes = await adminFetch(`${ADMIN_API}/solicitudes`)
        const lista       = document.getElementById("lista-admin-solicitudes")
        if (!lista) return

        if (solicitudes.length === 0) {
            lista.innerHTML = "<tr><td colspan='7'>No hay solicitudes en el sistema.</td></tr>"
            return
        }

        lista.innerHTML = solicitudes.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>
                    ${s.foto_url
                        ? `<img src="${s.foto_url}" alt="${s.nombre}" class="mascota-thumb">`
                        : "—"}
                </td>
                <td><strong>${s.nombre}</strong></td>
                <td>${s.especie}${s.raza ? ` / ${s.raza}` : ""}</td>
                <td>${s.usuario_username || s.usuario_id}</td>
                <td>${s.horario_inicio ? s.horario_inicio.replace("T", " ").slice(0, 16) : "—"}</td>
                <td>${s.horario_fin    ? s.horario_fin.replace("T",    " ").slice(0, 16) : "—"}</td>
            </tr>
        `).join("")

    } catch (error) {
        document.getElementById("lista-admin-solicitudes").innerHTML =
            `<tr><td colspan='7' class="error-msg">${error.message}</td></tr>`
    }
}