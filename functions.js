/* Menú hamburguesa */
function toggleMenu() {
    document.querySelector("nav ul").classList.toggle("active");
}

function enviarFormulario(event) {
    event.preventDefault(); // Evita que se recargue la página

    const nombre = document.getElementById("nombre").value;
    const correo = document.getElementById("correo").value;
    const mensaje = document.getElementById("mensaje").value;

    const mensajeDiv = document.getElementById("mensaje-confirmacion");
    mensajeDiv.innerHTML = `Gracias <b>${nombre}</b>, tu mensaje ha sido enviado correctamente ❤️`;
    mensajeDiv.style.display = "block";

    document.querySelector(".form-contacto").reset();
}
