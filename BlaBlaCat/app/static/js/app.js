// static/js/app.js

const app = document.getElementById("app")

// ─── Router ───────────────────────────────────────────────

const routes = {
    "/":            renderHome,
    "/login":       renderLogin,
    "/registro":    renderRegistro,
    "/solicitudes": renderSolicitudes,
}

function navigate(event, path) {
    event.preventDefault()
    window.history.pushState({}, "", path)
    render(path)
}

function render(path) {
    const handler = routes[path] || renderNotFound
    handler()
    actualizarNav()
}

window.addEventListener("popstate", () => render(window.location.pathname))

// ─── Utilidades ───────────────────────────────────────────

function cloneTemplate(id) {
    return document.getElementById(id).content.cloneNode(true)
}

function actualizarNav() {
    const logueado = !!localStorage.getItem("token")
    document.getElementById("nav-login").style.display  = logueado ? "none"  : "inline"
    document.getElementById("nav-logout").style.display = logueado ? "inline": "none"
}

// ─── Vistas ───────────────────────────────────────────────

function renderHome() {
    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-home"))
}

function renderNotFound() {
    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-404"))
}

function renderLogin() {
    if (localStorage.getItem("token")) return navigate(event, "/solicitudes")

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-login"))

    document.getElementById("form-login").addEventListener("submit", async (e) => {
        e.preventDefault()
        const data = Object.fromEntries(new FormData(e.target))
        await login(data)
    })
}

function renderRegistro() {
    if (localStorage.getItem("token")) return navigate(event, "/solicitudes")

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-registro"))

    document.getElementById("form-registro").addEventListener("submit", async (e) => {
        e.preventDefault()
        const data = Object.fromEntries(new FormData(e.target))
        await registro(data)
    })
}

function renderSolicitudes() {
    if (!localStorage.getItem("token")) return navigate(event, "/login")

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-solicitudes"))

    document.getElementById("form-solicitud").addEventListener("submit", async (e) => {
        e.preventDefault()
        const data = Object.fromEntries(new FormData(e.target))
        await crear_solicitud(data)
    })

    cargarSolicitudes()
}

// ─── Arranque ─────────────────────────────────────────────

render(window.location.pathname)