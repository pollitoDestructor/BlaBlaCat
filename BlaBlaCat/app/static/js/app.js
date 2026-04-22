// static/js/app.js

const app = document.getElementById("app")

// ─── Router ───────────────────────────────────────────────

const routes = {
    "/":                  renderHome,
    "/login":             renderLogin,
    "/registro":          renderRegistro,
    "/solicitudes":       renderSolicitudes,
    "/admin/usuarios":    renderAdminUsuarios,    // #276 / #298
    "/admin/solicitudes": renderAdminSolicitudes, // #300
    "/proximas":          renderProximas,
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
    const esAdmin  = localStorage.getItem("rol") === "administrador"

    document.getElementById("nav-login").style.display     = logueado              ? "none"   : "inline"
    document.getElementById("nav-logout").style.display    = logueado              ? "inline" : "none"
    document.getElementById("nav-admin").style.display     = esAdmin               ? "inline" : "none"
    document.getElementById("nav-solicitudes").style.display = (logueado && !esAdmin) ? "inline" : "none"

    if (logueado) {
        const label = document.getElementById("nav-username")
        if (label) label.textContent = localStorage.getItem("username") || ""
    }
}

// ─── Vistas públicas ──────────────────────────────────────

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
        const destino = localStorage.getItem("rol") === "administrador" ? "/admin/usuarios" : "/solicitudes"
        window.history.pushState({}, "", destino)
        render(destino)
        return
    }

    app.innerHTML = ""
    app.appendChild(cloneTemplate("tpl-login"))

    document.getElementById("form-login").addEventListener("submit", async (e) => {
        e.preventDefault()
        await login(Object.fromEntries(new FormData(e.target)))
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
        await registro(Object.fromEntries(new FormData(e.target)))
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
    console.log("Formulario:", form)

    form.addEventListener("submit", async (e) => {
        e.preventDefault()
        const datos = Object.fromEntries(new FormData(e.target))
        datos.usuario_id = localStorage.getItem("usuario_id")
        await crearSolicitud(datos)
        e.target.reset()
    })

    cargarSolicitudes()
}

// ─── Arranque ─────────────────────────────────────────────

render(window.location.pathname)