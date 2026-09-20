document.addEventListener("DOMContentLoaded", () => {
  const formulario = document.querySelector("#formulario-login");
  const error = document.querySelector("#error-login");
  if (!formulario || !error) return;

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const boton = formulario.querySelector("button[type='submit']");
    const datos = new FormData(formulario);
    boton.disabled = true;
    boton.textContent = "Verificando…";
    error.hidden = true;
    try {
      const respuesta = await fetch("/api/auth/sesion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          usuario: datos.get("usuario"),
          contrasena: datos.get("contrasena"),
        }),
      });
      if (!respuesta.ok) {
        const detalle = await respuesta.json().catch(() => ({}));
        throw new Error(detalle.detail || "No se pudo iniciar sesión");
      }
      window.location.replace("/");
    } catch (fallo) {
      error.textContent = fallo.message;
      error.hidden = false;
      boton.disabled = false;
      boton.textContent = "Entrar al panel";
    }
  });
});
