// static/js/auth.js

const AUTH_API = "/api/auth"

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

async function login(data) {
    try {
        const res = await apiFetch(`${AUTH_API}/login`, {
            method: "POST",
            body: JSON.stringify(data),
        })
        localStorage.setItem("usuario_id", res.usuario_id)
        window.history.pushState({}, "", "/solicitudes")
        render("/solicitudes")
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
        await login({ email: data.email, password: data.password })
    } catch (error) {
        mostrarErrorAuth(error.message)
    }
}

function logout() {
    localStorage.removeItem("usuario_id")
    window.history.pushState({}, "", "/login")
    render("/login")
}

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
