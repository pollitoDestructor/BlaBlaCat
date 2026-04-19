// static/js/auth.js

const AUTH_API = "/api/auth"

// ─── Helpers ──────────────────────────────────────────────

async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || "Error en la petición")
    return data
}

// ─── Auth ─────────────────────────────────────────────────

async function login(data) {
    try {
        const res = await apiFetch(`${AUTH_API}/login`, {
            method: "POST",
            body:   JSON.stringify(data),
        })
        // Guardar sesión en localStorage
        localStorage.setItem("usuario_id", res.usuario_id)
        localStorage.setItem("rol",        res.rol)       // "estandar" | "administrador"
        localStorage.setItem("username",   res.username)

        // Redirigir según rol
        const destino = res.rol === "administrador" ? "/admin/usuarios" : "/solicitudes"
        window.history.pushState({}, "", destino)
        render(destino)

    } catch (error) {
        mostrarErrorAuth(error.message)
    }
}

async function registro(data) {
    try {
        await apiFetch(`${AUTH_API}/registro`, {
            method: "POST",
            body:   JSON.stringify(data),
        })
        // Login automático tras registro
        await login({ email: data.email, password: data.password })

    } catch (error) {
        mostrarErrorAuth(error.message)
    }
}

function logout() {
    localStorage.removeItem("usuario_id")
    localStorage.removeItem("rol")
    localStorage.removeItem("username")
    window.history.pushState({}, "", "/login")
    render("/login")
}

// ─── UI ───────────────────────────────────────────────────

function mostrarErrorAuth(mensaje) {
    const form = document.querySelector("form")
    if (!form) return

    let errorEl = form.querySelector(".error-msg")
    if (!errorEl) {
        errorEl = document.createElement("p")
        errorEl.className = "error-msg"
        errorEl.style.color = "red"
        form.appendChild(errorEl)
    }
    errorEl.textContent = mensaje
}