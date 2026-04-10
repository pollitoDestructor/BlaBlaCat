// static/js/auth.js

const AUTH_API = "/api/auth"

// ─── Helpers ──────────────────────────────────────────────

function setToken(token) {
    localStorage.setItem("token", token)
}

function removeToken() {
    localStorage.removeItem("token")
}

function getToken() {
    return localStorage.getItem("token")
}

// Wrapper igual que en solicitudes.js
async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || "Error en la petición")
    }

    return data
}

// ─── Auth ─────────────────────────────────────────────────

async function login(data) {
    try {
        const res = await apiFetch(`${AUTH_API}/login`, {
            method: "POST",
            body: JSON.stringify(data),
        })

        setToken(res.access_token)

        // Redirigir a solicitudes
        navigate({ preventDefault: () => {} }, "/solicitudes")

    } catch (error) {
        mostrarErrorAuth(error.message)
    }
}

async function registro(data) {
    try {
        await apiFetch(`${AUTH_API}/registro`, {
            method: "POST",
            body: JSON.stringify(data),
        })

        // Tras registrarse → login automático
        await login({
            email: data.email,
            password: data.password
        })

    } catch (error) {
        mostrarErrorAuth(error.message)
    }
}

function logout() {
    removeToken()
    navigate(event, "/login")
}

// ─── UI ───────────────────────────────────────────────────

function mostrarErrorAuth(mensaje) {
    const form = document.querySelector("form")
    if (!form) return

    let error = form.querySelector(".error")

    if (!error) {
        error = document.createElement("p")
        error.className = "error"
        form.appendChild(error)
    }

    error.textContent = mensaje
}