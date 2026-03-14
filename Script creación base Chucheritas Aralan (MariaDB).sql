CREATE DATABASE IF NOT EXISTS CHUCHERITAS_ARALAN;
USE CHUCHERITAS_ARALAN;


CREATE TABLE puestos (
    id_puesto INT NOT NULL AUTO_INCREMENT,
    descripcion VARCHAR(100) NOT NULL,
    privilegios BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT puestos_id_pk PRIMARY KEY (id_puesto)
);

CREATE TABLE empleados (
    id_empleado INT NOT NULL AUTO_INCREMENT,
    id_puesto INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',

    CONSTRAINT empleados_id_pk PRIMARY KEY (id_empleado),
    CONSTRAINT empleados_correo_uq UNIQUE (correo),
    CONSTRAINT empleados_puesto_fk FOREIGN KEY (id_puesto)
        REFERENCES puestos(id_puesto)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE categorias (
    id_categoria CHAR(3) NOT NULL,
    descripcion VARCHAR(100) NOT NULL,

    CONSTRAINT categorias_id_pk PRIMARY KEY (id_categoria)
);


CREATE TABLE productos (
    id_producto INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    id_categoria CHAR(3) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    existencias INT NOT NULL DEFAULT 0,
    estado ENUM('activo','descontinuado') NOT NULL DEFAULT 'activo',

    CONSTRAINT productos_id_pk PRIMARY KEY (id_producto),

    CONSTRAINT productos_categoria_fk FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE fotos_productos (
    id_foto INT NOT NULL AUTO_INCREMENT,
    id_producto INT NOT NULL,
    foto BLOB NOT NULL,

    CONSTRAINT fotos_id_pk PRIMARY KEY (id_foto),

    CONSTRAINT fotos_producto_fk FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE clientes (
    id_cliente INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,

    CONSTRAINT clientes_id_pk PRIMARY KEY (id_cliente),
    CONSTRAINT clientes_correo_uq UNIQUE (correo)
);


CREATE TABLE lugares_entrega (
    id_lugar INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    calle VARCHAR(100) NOT NULL,
    codigo_postal CHAR(5) NOT NULL,

    CONSTRAINT lugares_id_pk PRIMARY KEY (id_lugar)
);


CREATE TABLE pedidos (
    id_pedido INT NOT NULL AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    id_lugar INT NOT NULL,
    id_repartidor INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    estado ENUM('en_proceso','en_camino','entregado','cancelado') NOT NULL DEFAULT 'en_proceso',

    CONSTRAINT pedidos_id_pk PRIMARY KEY (id_pedido),

    CONSTRAINT pedidos_cliente_fk FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT pedidos_lugar_fk FOREIGN KEY (id_lugar)
        REFERENCES lugares_entrega(id_lugar)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT pedidos_repartidor_fk FOREIGN KEY (id_repartidor)
        REFERENCES empleados(id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);



CREATE TABLE detalles_pedido (
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    CONSTRAINT detalles_pedido_pk PRIMARY KEY (id_pedido, id_producto),

    CONSTRAINT detalles_pedido_pedido_fk FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT detalles_pedido_producto_fk FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);



CREATE TABLE historial_pedidos (
    id_cliente INT NOT NULL,
    id_pedido INT NOT NULL,

    CONSTRAINT historial_pedidos_pk PRIMARY KEY (id_cliente, id_pedido),

    CONSTRAINT historial_cliente_fk FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT historial_pedido_fk FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);






