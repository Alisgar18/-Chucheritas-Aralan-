from backend.database import get_db_cursor
from backend import encryption

class ProductoModel:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los productos con sus fotos"""
        with get_db_cursor() as cursor:
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
            return cursor.fetchall()

    @staticmethod
    def agregar(nombre, id_categoria, descripcion, precio, existencias, estado="activo", fotos=None):
        """Agrega un nuevo producto"""
        with get_db_cursor() as cursor:
            # Insertar producto
            cursor.execute("""
                INSERT INTO productos (nombre, id_categoria, descripcion, precio, existencias, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, id_categoria, descripcion, precio, existencias, estado))

            id_producto = cursor.lastrowid

            # Insertar fotos si existen
            if fotos:
                for foto in fotos:
                    cursor.execute("""
                        INSERT INTO fotos_productos (id_producto, foto)
                        VALUES (%s, %s)
                    """, (id_producto, foto))

            return {"status": "ok", "msg": "Producto registrado", "id_producto": id_producto}

    @staticmethod
    def modificar(id_producto, **campos):
        """Modifica un producto existente"""
        if not campos:
            return {"status": "error", "msg": "No se recibió ningún campo para modificar"}

        set_clause = ", ".join([f"{key} = %s" for key in campos.keys()])
        valores = list(campos.values())
        valores.append(id_producto)

        with get_db_cursor() as cursor:
            cursor.execute(f"""
                UPDATE productos 
                SET {set_clause} 
                WHERE id_producto = %s
            """, valores)

            return {"status": "ok", "msg": "Producto actualizado"}

class UsuarioModel:
    @staticmethod
    def iniciar_sesion(correo, contrasena):
        """Inicia sesión para empleado o cliente"""
        with get_db_cursor() as cursor:
            # 1. Buscar como empleado
            cursor.execute("""
                SELECT id_empleado AS id, nombre, correo, contrasena_hash, estado, id_puesto,
                       'empleado' AS tipo
                FROM empleados
                WHERE correo = %s
                LIMIT 1
            """, (correo,))

            empleado = cursor.fetchone()
            if empleado:
                if empleado["estado"] != "activo":
                    return None
                if encryption.verify_password(contrasena, empleado["contrasena_hash"]):
                    return empleado
                return None

            # 2. Buscar como cliente
            cursor.execute("""
                SELECT id_cliente AS id, nombre, correo, contrasena_hash,
                       'cliente' AS tipo
                FROM clientes
                WHERE correo = %s
                LIMIT 1
            """, (correo,))

            cliente = cursor.fetchone()
            if cliente and encryption.verify_password(contrasena, cliente["contrasena_hash"]):
                return cliente

            return None

    @staticmethod
    def registrar_cliente(nombre, correo, contrasena, telefono):
        """Registra un nuevo cliente"""
        contrasena_hash = encryption.hash_password(contrasena)
        
        with get_db_cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO clientes (nombre, correo, contrasena_hash, telefono)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, correo, contrasena_hash, telefono))

                return {"status": "ok", "msg": "Cliente registrado correctamente"}

            except Exception as e:
                return {"status": "error", "msg": str(e)}

    @staticmethod
    def registrar_empleado(id_puesto, nombre, telefono, correo, contrasena, estado="activo"):
        """Registra un nuevo empleado"""
        contrasena_hash = encryption.hash_password(contrasena)
        
        with get_db_cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO empleados (id_puesto, nombre, telefono, correo, contrasena_hash, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_puesto, nombre, telefono, correo, contrasena_hash, estado))

                return {"status": "ok", "msg": "Empleado registrado correctamente"}

            except Exception as e:
                if "Duplicate entry" in str(e) and "correo" in str(e):
                    return {"status": "error", "msg": "Ese correo ya está registrado"}
                return {"status": "error", "msg": str(e)}

class PedidoModel:
    @staticmethod
    def crear(id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total, detalles):
        """Crea un nuevo pedido"""
        with get_db_cursor() as cursor:
            try:
                # Insertar el pedido
                cursor.execute("""
                    INSERT INTO pedidos (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total))

                id_pedido = cursor.lastrowid

                # Insertar detalles
                for detalle in detalles:
                    cursor.execute("""
                        INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s)
                    """, (id_pedido, detalle["id_producto"], detalle["cantidad"], detalle["subtotal"]))

                return {"status": "ok", "msg": "Pedido creado", "id_pedido": id_pedido}

            except Exception as e:
                return {"status": "error", "msg": str(e)}