/* -------- CARRUSEL -------- */
let slideIndex = 1;
mostrarSlide(slideIndex);

function cambiarSlide(n) {
    mostrarSlide(slideIndex = n);
}

function mostrarSlide(n) {
    let slides = document.getElementsByClassName("carrusel-slide");
    let puntos = document.getElementsByClassName("punto");

    if (n > slides.length) slideIndex = 1;
    if (n < 1) slideIndex = slides.length;

    for (let i = 0; i < slides.length; i++)
        slides[i].style.display = "none";

    for (let i = 0; i < puntos.length; i++)
        puntos[i].classList.remove("active");

    slides[slideIndex - 1].style.display = "block";
    puntos[slideIndex - 1].classList.add("active");
}

setInterval(() => {
    slideIndex++;
    mostrarSlide(slideIndex);
}, 5000);


/* -------- CONTROL DE SECCIONES -------- */
function mostrarSeccion(nombre) {
    document.querySelectorAll(".seccion").forEach(sec =>
        sec.classList.remove("activa")
    );

    document.getElementById(nombre).classList.add("activa");

    document.querySelector("nav ul").classList.remove("active");
}