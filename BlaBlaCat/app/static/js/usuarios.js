// static/js/usuarios.js

const USUARIOS_API = "/api/usuarios"

// ─── Lista de todos los usuarios ──────────────────────────

async function cargarUsuarios() {
    try {
        const usuarios = await apiFetch(USUARIOS_API)
        renderListaUsuarios(usuarios)
    } catch (error) {
        document.getElementById("app").innerHTML = `<p class="error">${error.message}</p>`
    }
}

function renderListaUsuarios(usuarios) {
    const lista = document.getElementById("lista-usuarios")
    if (!lista) return

    if (usuarios.length === 0) {
        lista.innerHTML = "<li class='vacio'>No hay usuarios registrados.</li>"
        return
    }

    lista.innerHTML = usuarios.map(u => `
        <li class="usuario-item">
            <div class="usuario-info">
                <strong>${u.username}</strong>
                <span class="usuario-media">
                    ${u.media !== null
                        ? `⭐ ${u.media} <small>(${u.num_valoraciones} valoración${u.num_valoraciones !== 1 ? "es" : ""})</small>`
                        : `<small>Sin valoraciones aún</small>`
                    }
                </span>
            </div>
            <button onclick="navigate(event, '/perfil/${u.id}')">Ver perfil</button>
        </li>
    `).join("")
}

// ─── Perfil de un usuario ─────────────────────────────────

async function cargarPerfil(id) {
    try {
        const perfil = await apiFetch(`${USUARIOS_API}/${id}`)
        renderPerfil(perfil)
    } catch (error) {
        document.getElementById("app").innerHTML = `<p class="error">${error.message}</p>`
    }
}

function renderPerfil(perfil) {
    const appEl = document.getElementById("app")
    appEl.innerHTML = ""

    const tpl = document.getElementById("tpl-perfil").content.cloneNode(true)

    tpl.querySelector("#perfil-username").textContent = perfil.username
    tpl.querySelector("#perfil-media").textContent =
        perfil.media !== null ? `⭐ ${perfil.media} / 5` : "Sin valoraciones aún"

    const lista = tpl.querySelector("#lista-valoraciones")
    if (perfil.valoraciones.length === 0) {
        lista.innerHTML = "<li class='vacio'>Este cuidador aún no tiene valoraciones.</li>"
    } else {
        lista.innerHTML = perfil.valoraciones.map(v => `
            <li class="valoracion-item">
                <div class="valoracion-estrellas">${"⭐".repeat(v.puntuacion)} (${v.puntuacion}/5)</div>
                <p class="valoracion-comentario">${v.comentario}</p>
                <small>Por <strong>${v.autor}</strong></small>
            </li>
        `).join("")
    }

    const usuarioActual = parseInt(localStorage.getItem("usuario_id"))
    const formSection   = tpl.querySelector("#seccion-valorar")
    const solicitudId   = new URLSearchParams(window.location.search).get("solicitud")

    if (!usuarioActual || usuarioActual === perfil.id || !solicitudId) {
        formSection.style.display = "none"
    } else {
        const yaValorada = perfil.valoraciones.some(v => v.solicitud_id === parseInt(solicitudId))
        if (yaValorada) {
            formSection.innerHTML = "<p class='ya-valorada'>✅ Ya has valorado esta solicitud.</p>"
        } else {
            const form = tpl.querySelector("#form-valoracion")
            form.addEventListener("submit", async (e) => {
                e.preventDefault()
                const datos = Object.fromEntries(new FormData(e.target))
                await enviarValoracion(perfil.id, {
                    autor_id:     usuarioActual,
                    solicitud_id: parseInt(solicitudId),
                    puntuacion:   parseInt(datos.puntuacion),
                    comentario:   datos.comentario,
                })
                await cargarPerfil(perfil.id)
            })
        }
    }

    appEl.appendChild(tpl)
}

async function enviarValoracion(destinatarioId, datos) {
    try {
        await apiFetch(`${USUARIOS_API}/${destinatarioId}/valoraciones`, {
            method: "POST",
            body: JSON.stringify(datos),
        })
    } catch (error) {
        alert(error.message)
    }
}
