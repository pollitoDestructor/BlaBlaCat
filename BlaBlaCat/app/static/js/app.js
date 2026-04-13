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
    const logueado = !!localStorage.getItem("usuario_id")
    document.getElementById("nav-login").style.display  = logueado ? "none"   : "inline"
    document.getElementById("nav-logout").style.display = logueado ? "inline" : "none"
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
    if (localStorage.getItem("usuario_id")) {
        window.history.pushState({}, "", "/solicitudes")
        render("/solicitudes")
        return
    }

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-login"))

    document.getElementById("form-login").addEventListener("submit", async (e) => {
        e.preventDefault()
        const data = Object.fromEntries(new FormData(e.target))
        await login(data)
    })
}

function renderRegistro() {
    if (localStorage.getItem("usuario_id")) {
        window.history.pushState({}, "", "/solicitudes")
        render("/solicitudes")
        return
    }

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-registro"))

    document.getElementById("form-registro").addEventListener("submit", async (e) => {
        e.preventDefault()
        const data = Object.fromEntries(new FormData(e.target))
        await registro(data)
    })
}

function renderSolicitudes() {
    if (!localStorage.getItem("usuario_id")) {
        window.history.pushState({}, "", "/login")
        render("/login")
        return
    }

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-solicitudes"))

    const form = document.getElementById("form-nueva-solicitud")
    console.log("Formulario encontrado:", form)  // debe mostrar el elemento, no null

    form.addEventListener("submit", async (e) => {
        e.preventDefault()
        const datos = Object.fromEntries(new FormData(e.target))
        datos.usuario_id = localStorage.getItem("usuario_id")
        await crearSolicitud(datos)
        e.target.reset()
    });
    cargarSolicitudes()
}

// ─── Arranque ─────────────────────────────────────────────

render(window.location.pathname)