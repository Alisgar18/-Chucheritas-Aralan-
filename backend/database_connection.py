import mysql.connector
import encyption

def get_connection():
    return mysql.connector.connect(
        host="centerbeam.proxy.rlwy.net",
        user="APP_USER",
        password="4l1Sl4m4s",
        database="CHUCHERITAS_ARALAN"
    )

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            p.id_producto,
            p.nombre,
            p.precio,
            p.descripcion,
            p.existencias,
            p.estado,
            f.foto
        FROM productos p
        LEFT JOIN fotos_productos f 
            ON p.id_producto = f.id_producto
        GROUP BY p.id_producto
    """)

    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos

def iniciar_sesion(correo, contrasena):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ============================================================
    # 1. Buscar como empleado
    # ============================================================
    cursor.execute("""
        SELECT id_empleado AS id, nombre, correo, contrasena_hash, estado, id_puesto,
               'empleado' AS tipo
        FROM empleados
        WHERE correo = %s
        LIMIT 1
    """, (correo,))

    empleado = cursor.fetchone()

    if empleado:
        # Validar estado
        if empleado["estado"] != "activo":
            cursor.close()
            conn.close()
            return None
        
        # Verificar contraseña
        if encyption.verify_password(contrasena, empleado["contrasena_hash"]):
            cursor.close()
            conn.close()
            return empleado
        else:
            cursor.close()
            conn.close()
            return None

    # ============================================================
    # 2. Buscar como cliente
    # ============================================================
    cursor.execute("""
        SELECT id_cliente AS id, nombre, correo, contrasena_hash,
               'cliente' AS tipo
        FROM clientes
        WHERE correo = %s
        LIMIT 1
    """, (correo,))

    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    if not cliente:
        return None

    # Verificar contraseña
    if encyption.verify_password(contrasena, cliente["contrasena_hash"]):
        return cliente
    else:
        return None



def registrar_cliente(nombre, correo, contrasena, telefono):
    conn = get_connection()
    cursor = conn.cursor()

    contrasena_hash = encyption.hash_password(contrasena)

    try:
        cursor.execute("""
            INSERT INTO clientes (nombre, correo, contrasena_hash, telefono)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, contrasena_hash, telefono))

        conn.commit()
        return {"status": "ok", "msg": "Cliente registrado correctamente"}

    except Exception as e:
        return {"status": "error", "msg": str(e)}

    finally:
        cursor.close()
        conn.close()


def registrar_empleado(id_puesto, nombre, telefono, correo, contrasena, estado="activo"):
    conn = get_connection()
    cursor = conn.cursor()

    contrasena_hash = encyption.hash_password(contrasena)

    try:
        cursor.execute("""
            INSERT INTO empleados (id_puesto, nombre, telefono, correo, contrasena_hash, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_puesto, nombre, telefono, correo, contrasena_hash, estado))

        conn.commit()

        return {
            "status": "ok",
            "msg": "Empleado registrado correctamente"
        }

    except Exception as e:
        # detectamos UNIQUE email duplicado de forma elegante
        if "Duplicate entry" in str(e) and "correo" in str(e):
            return {
                "status": "error",
                "msg": "Ese correo ya está registrado"
            }

        return {
            "status": "error",
            "msg": str(e)
        }

    finally:
        cursor.close()
        conn.close()



def agregar_producto(nombre, id_categoria, descripcion, precio, existencias, estado="activo", fotos=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insertar producto
        cursor.execute("""
            INSERT INTO productos (nombre, id_categoria, descripcion, precio, existencias, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, id_categoria, descripcion, precio, existencias, estado))

        id_producto = cursor.lastrowid

        # Insertar fotos (si vienen)
        if fotos:
            for foto in fotos:
                cursor.execute("""
                    INSERT INTO fotos_productos (id_producto, foto)
                    VALUES (%s, %s)
                """, (id_producto, foto))

        conn.commit()
        return {"status": "ok", "msg": "Producto registrado", "id_producto": id_producto}

    except Exception as e:
        return {"status": "error", "msg": str(e)}

    finally:
        cursor.close()
        conn.close()



def modificar_producto(id_producto, nombre=None, id_categoria=None, descripcion=None,
                       precio=None, existencias=None, estado=None):
    conn = get_connection()
    cursor = conn.cursor()

    campos = []
    valores = []

    if nombre is not None:
        campos.append("nombre = %s")
        valores.append(nombre)

    if id_categoria is not None:
        campos.append("id_categoria = %s")
        valores.append(id_categoria)

    if descripcion is not None:
        campos.append("descripcion = %s")
        valores.append(descripcion)

    if precio is not None:
        campos.append("precio = %s")
        valores.append(precio)

    if existencias is not None:
        campos.append("existencias = %s")
        valores.append(existencias)

    if estado is not None:
        campos.append("estado = %s")
        valores.append(estado)

    if not campos:
        return {"status": "error", "msg": "No se recibió ningún campo para modificar"}

    valores.append(id_producto)

    query = f"UPDATE productos SET {', '.join(campos)} WHERE id_producto = %s"

    try:
        cursor.execute(query, valores)
        conn.commit()
        return {"status": "ok", "msg": "Producto actualizado"}

    except Exception as e:
        return {"status": "error", "msg": str(e)}

    finally:
        cursor.close()
        conn.close()


def crear_pedido(id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total, detalles):
    """
    detalles = [
        {"id_producto": 1, "cantidad": 2, "subtotal": 150.00},
        {"id_producto": 5, "cantidad": 1, "subtotal": 80.00}
    ]
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insertar el pedido
        cursor.execute("""
            INSERT INTO pedidos (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total))

        id_pedido = cursor.lastrowid

        # Insertar detalles
        for d in detalles:
            cursor.execute("""
                INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, subtotal)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, d["id_producto"], d["cantidad"], d["subtotal"]))

        conn.commit()

        return {"status": "ok", "msg": "Pedido creado", "id_pedido": id_pedido}

    except Exception as e:
        return {"status": "error", "msg": str(e)}

    finally:
        cursor.close()
        conn.close()


