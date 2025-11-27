// -------- CATÁLOGO DINÁMICO --------

const productos = [
    { img: "caliente-reds.png", nombre: 'Set De Labiales "Caliente Reds"', precio: 150, descripcion: "Set de 5 labiales mousse matte en tonos rojos intensos." },
    { img: "gloss1.png", nombre: 'Kit De Lip Gloss - Italia Deluxe', precio: 150, descripcion: "Brillo labial efecto cristal con aroma dulce." },
    { img: "fijador.png", nombre: "Fijador De Maquillaje - Pink Up", precio: 95, descripcion: "Hidrata y refresca la piel." },
    { img: "delineador.png", nombre: "Delineador Plumón Negro - Italia Deluxe", precio: 55, descripcion: "Punta fina y resistente al agua, acabado matte." },
    { img: "blush.png", nombre: 'Rubor “Amor Eterno” - Italia Deluxe', precio: 60, descripcion: "Rubor mágico." },
    { img: "crema-manos.png", nombre: "Crema Corporal - Yuya", precio: 95, descripcion: "Crema hidratante aroma frutal." },
    { img: "esponjas.png", nombre: "Set De Esponjas Para Maquillaje", precio: 40, descripcion: "Set de esponjas para aplicar maquillaje." },
    { img: "sombras.png", nombre: "Paleta De Sombras - Yuya", precio: 230, descripcion: "Paleta de sombras para ojos en tonos cálidos." },
    { img: "brochas.png", nombre: "Set De Brochas Para Maquillaje - Intensamente", precio: 240, descripcion: "Set de 9 brochas para maquillaje." },
    { img: "primer.png", nombre: "Primer Facial - Yuya", precio: 99, descripcion: "Fija el maquillaje y suaviza la piel." }
];

// --------- CARGAR AL HTML ---------
function cargarCatalogo() {
    const contenedor = document.getElementById("catalogo-contenedor");
    contenedor.innerHTML = "";

    productos.forEach(prod => {
        contenedor.innerHTML += `
            <div class="producto-card">
                <img src="${prod.img}" alt="${prod.nombre}">
                <h3>${prod.nombre}</h3>
                <p class="precio">$${prod.precio} MXN</p>
                <p class="descripcion">${prod.descripcion}</p>
                <button class="btn-comprar" onclick="agregarCarrito('${prod.nombre}')">Agregar al carrito</button>
            </div>
        `;
    });
}

function agregarCarrito(nombre) {
    alert(`${nombre} se agregó al carrito 🛒`);
}

window.onload = cargarCatalogo;
