from backend.database import get_db_cursor, is_database_available, logger
from backend import encryption


class ProductoModel:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los productos con sus fotos"""
        if not is_database_available():
            return []

        try:
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
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []

    @staticmethod
    def agregar(nombre, id_categoria, descripcion, precio, existencias, estado="activo", fotos=None):
        """Agrega un nuevo producto y sus fotos (si las hay)"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO productos (nombre, id_categoria, descripcion, precio, existencias, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, id_categoria, descripcion, precio, existencias, estado))

                id_producto = cursor.lastrowid

                if fotos:
                    for foto in fotos:
                        cursor.execute("""
                            INSERT INTO fotos_productos (id_producto, foto)
                            VALUES (%s, %s)
                        """, (id_producto, foto))

                return {"status": "ok", "msg": "Producto registrado", "id_producto": id_producto}
        except Exception as e:
            logger.error(f"Error agregando producto: {e}")
            return {"status": "error", "msg": str(e)}

    @staticmethod
    def modificar(id_producto, **campos):
        """Modifica un producto existente"""
        if not campos:
            return {"status": "error", "msg": "No se recibió ningún campo para modificar"}

        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        set_clause = ", ".join([f"{key} = %s" for key in campos.keys()])
        valores = list(campos.values())
        valores.append(id_producto)

        try:
            with get_db_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE productos 
                    SET {set_clause} 
                    WHERE id_producto = %s
                """, valores)

                return {"status": "ok", "msg": "Producto actualizado"}
        except Exception as e:
            logger.error(f"Error modificando producto: {e}")
            return {"status": "error", "msg": str(e)}


class UsuarioModel:
    @staticmethod
    def iniciar_sesion(correo, contrasena):
        """Inicia sesión para empleado o cliente"""
        if not is_database_available():
            return None

        try:
            with get_db_cursor() as cursor:
                # 1. Buscar como empleado
                cursor.execute("""
                    SELECT 
                        e.id_empleado AS id, 
                        e.nombre, 
                        e.correo, 
                        e.contrasena_hash, 
                        e.estado, 
                        e.id_puesto,
                        p.descripcion as puesto_descripcion,
                        p.privilegios,
                        'empleado' AS tipo
                    FROM empleados e
                    LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
                    WHERE e.correo = %s
                    LIMIT 1
                """, (correo,))

                empleado = cursor.fetchone()
                if empleado:
                    print(f"DEBUG: Empleado encontrado - {empleado}")  # DEBUG
                    if empleado.get("estado") != "activo":
                        return None
                    if encryption.verify_password(contrasena, empleado.get("contrasena_hash")):
                        # LÓGICA TEMPORAL - usa privilegios para determinar admin
                        if empleado.get("privilegios") == 1:  # Si privilegios = 1 = admin
                            empleado['rol'] = 'administrador'
                        else:
                            empleado['rol'] = 'repartidor'  # Por defecto repartidor
                        print(f"DEBUG: Rol asignado - {empleado['rol']}")  # DEBUG
                        return empleado
                    return None

                # 2. Buscar como cliente
                cursor.execute("""
                    SELECT 
                        id_cliente AS id, 
                        nombre, 
                        correo, 
                        contrasena_hash,
                        'cliente' AS tipo
                    FROM clientes
                    WHERE correo = %s
                    LIMIT 1
                """, (correo,))

                cliente = cursor.fetchone()
                if cliente and encryption.verify_password(contrasena, cliente.get("contrasena_hash")):
                    return cliente

                return None
        except Exception as e:
            logger.error(f"Error iniciando sesión: {e}")
            return None

    @staticmethod
    def registrar_cliente(nombre, correo, contrasena, telefono):
        """Registra un nuevo cliente"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        contrasena_hash = encryption.hash_password(contrasena)

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO clientes (nombre, correo, contrasena_hash, telefono)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, correo, contrasena_hash, telefono))

                return {"status": "ok", "msg": "Cliente registrado correctamente"}
        except Exception as e:
            logger.error(f"Error registrando cliente: {e}")
            return {"status": "error", "msg": str(e)}

    @staticmethod
    def registrar_empleado(id_puesto, nombre, telefono, correo, contrasena, estado="activo"):
        """Registra un nuevo empleado"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        contrasena_hash = encryption.hash_password(contrasena)

        try:
            with get_db_cursor() as cursor:
                # Verificar que el puesto existe
                cursor.execute("SELECT id_puesto FROM puestos WHERE id_puesto = %s", (id_puesto,))
                if not cursor.fetchone():
                    return {"status": "error", "msg": "El puesto especificado no existe"}

                cursor.execute("""
                    INSERT INTO empleados (id_puesto, nombre, telefono, correo, contrasena_hash, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_puesto, nombre, telefono, correo, contrasena_hash, estado))

                return {"status": "ok", "msg": "Empleado registrado correctamente"}
        except Exception as e:
            logger.error(f"Error registrando empleado: {e}")
            if "Duplicate entry" in str(e) and "correo" in str(e):
                return {"status": "error", "msg": "Ese correo ya está registrado"}
            return {"status": "error", "msg": str(e)}


class CarritoModel:
    @staticmethod
    def agregar_producto(id_usuario, id_producto, cantidad):
        """Agrega o actualiza un producto en el carrito del usuario"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        try:
            with get_db_cursor() as cursor:
                # Intentar actualizar si ya existe
                cursor.execute("""
                    SELECT cantidad FROM carritos
                    WHERE id_usuario = %s AND id_producto = %s
                    LIMIT 1
                """, (id_usuario, id_producto))
                existente = cursor.fetchone()
                if existente:
                    nuevo = existente.get("cantidad", 0) + cantidad
                    cursor.execute("""
                        UPDATE carritos SET cantidad = %s
                        WHERE id_usuario = %s AND id_producto = %s
                    """, (nuevo, id_usuario, id_producto))
                else:
                    cursor.execute("""
                        INSERT INTO carritos (id_usuario, id_producto, cantidad)
                        VALUES (%s, %s, %s)
                    """, (id_usuario, id_producto, cantidad))

                return {"status": "ok", "msg": "Producto agregado al carrito"}
        except Exception as e:
            logger.error(f"Error en carrito.agregar_producto: {e}")
            return {"status": "error", "msg": str(e)}

    @staticmethod
    def obtener_carrito(id_usuario):
        """Obtiene el carrito del usuario con datos de producto"""
        if not is_database_available():
            return []

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT c.id_producto, c.cantidad, p.nombre, p.precio, p.descripcion, p.foto
                    FROM carritos c
                    JOIN productos p ON c.id_producto = p.id_producto
                    WHERE c.id_usuario = %s
                """, (id_usuario,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo carrito: {e}")
            return []


class PedidoModel:
    @staticmethod
    def crear(id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total, detalles):
        """Crea un nuevo pedido y sus detalles"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pedidos (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_cliente, id_lugar, id_repartidor, fecha_entrega, monto_total))

                id_pedido = cursor.lastrowid

                for detalle in detalles:
                    cursor.execute("""
                        INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s)
                    """, (id_pedido, detalle["id_producto"], detalle["cantidad"], detalle["subtotal"]))

                return {"status": "ok", "msg": "Pedido creado", "id_pedido": id_pedido}
        except Exception as e:
            logger.error(f"Error creando pedido: {e}")
            return {"status": "error", "msg": str(e)}

    @staticmethod
    def obtener_por_cliente(id_cliente):
        """Obtiene pedidos de un cliente"""
        if not is_database_available():
            return []

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pedidos 
                    WHERE id_cliente = %s 
                    ORDER BY fecha_pedido DESC
                """, (id_cliente,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo pedidos: {e}")
            return []

    @staticmethod
    def obtener_para_repartidor():
        """Obtiene pedidos listos para repartidores"""
        if not is_database_available():
            return []

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pedidos 
                    WHERE estado IN ('pendiente', 'en_camino')
                    ORDER BY fecha_entrega
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo pedidos repartidor: {e}")
            return []

    @staticmethod
    def actualizar_estado(id_pedido, estado):
        """Actualiza estado de un pedido"""
        if not is_database_available():
            return {"status": "error", "msg": "BD no disponible"}

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE pedidos SET estado = %s 
                    WHERE id_pedido = %s
                """, (estado, id_pedido))
                return {"status": "ok", "msg": "Estado actualizado"}
        except Exception as e:
            logger.error(f"Error actualizando pedido: {e}")
            return {"status": "error", "msg": str(e)}


class AdminModel:
    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas para el dashboard admin"""
        if not is_database_available():
            return {
                'total_productos': 0,
                'total_pedidos': 0,
                'total_clientes': 0,
                'ventas_mes': 0
            }

        try:
            with get_db_cursor() as cursor:
                # Productos
                cursor.execute("SELECT COUNT(*) as total FROM productos")
                total_productos = cursor.fetchone().get('total', 0)

                # Pedidos
                cursor.execute("SELECT COUNT(*) as total FROM pedidos")
                total_pedidos = cursor.fetchone().get('total', 0)

                # Clientes
                cursor.execute("SELECT COUNT(*) as total FROM clientes")
                total_clientes = cursor.fetchone().get('total', 0)

                # Ventas del mes
                cursor.execute("""
                    SELECT COALESCE(SUM(monto_total), 0) as ventas 
                    FROM pedidos 
                    WHERE MONTH(fecha_pedido) = MONTH(CURRENT_DATE)
                """)
                ventas_mes = cursor.fetchone().get('ventas', 0)

                return {
                    'total_productos': total_productos,
                    'total_pedidos': total_pedidos,
                    'total_clientes': total_clientes,
                    'ventas_mes': ventas_mes
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_productos': 0,
                'total_pedidos': 0,
                'total_clientes': 0,
                'ventas_mes': 0
            }