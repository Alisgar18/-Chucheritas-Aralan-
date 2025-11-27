from backend.database import get_connection
from mysql.connector import Error
from decimal import Decimal

class CarritoModel:
    """Clase para manejar operaciones del carrito de compras"""
    
    @staticmethod
    def obtener_o_crear_carrito(id_cliente):
        """Obtiene el carrito del cliente o crea uno nuevo si no existe"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT id_carrito FROM carrito WHERE id_cliente = %s",
                (id_cliente,)
            )
            carrito = cursor.fetchone()
            
            if carrito:
                id_carrito = carrito['id_carrito']
            else:
                cursor.execute(
                    "INSERT INTO carrito (id_cliente) VALUES (%s)",
                    (id_cliente,)
                )
                connection.commit()
                id_carrito = cursor.lastrowid
            
            cursor.close()
            connection.close()
            return id_carrito
            
        except Error as e:
            print(f"Error al obtener/crear carrito: {e}")
            return None
    
    @staticmethod
    def obtener_carrito(id_cliente):
        """Obtiene todos los items del carrito con información del producto"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ic.id_item,
                    ic.id_producto,
                    ic.cantidad,
                    ic.precio_unitario,
                    p.nombre,
                    p.descripcion,
                    p.existencias,
                    p.estado,
                    c.descripcion as categoria,
                    (ic.cantidad * ic.precio_unitario) as subtotal
                FROM carrito ca
                INNER JOIN items_carrito ic ON ca.id_carrito = ic.id_carrito
                INNER JOIN productos p ON ic.id_producto = p.id_producto
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE ca.id_cliente = %s AND p.estado = 'activo'
                ORDER BY ic.fecha_agregado DESC
            """
            
            cursor.execute(query, (id_cliente,))
            items = cursor.fetchall()
            
            # Calcular total
            total = sum(float(item['subtotal']) for item in items)
            
            # Convertir Decimal a float para templates
            for item in items:
                item['precio_unitario'] = float(item['precio_unitario'])
                item['subtotal'] = float(item['subtotal'])
            
            cursor.close()
            connection.close()
            
            return {
                'items': items,
                'total': round(total, 2),
                'cantidad_items': len(items)
            }
            
        except Error as e:
            print(f"Error al obtener items del carrito: {e}")
            return {'items': [], 'total': 0, 'cantidad_items': 0}
    
    @staticmethod
    def agregar_producto(id_cliente, id_producto, cantidad=1):
        """Agrega un producto al carrito o actualiza la cantidad si ya existe"""
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return {'status': 'error', 'msg': 'Cantidad inválida'}
            
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Obtener o crear carrito
            id_carrito = CarritoModel.obtener_o_crear_carrito(id_cliente)
            if not id_carrito:
                return {'status': 'error', 'msg': 'Error al obtener el carrito'}
            
            # Verificar que el producto existe y está activo
            cursor.execute(
                "SELECT precio, existencias, estado FROM productos WHERE id_producto = %s",
                (id_producto,)
            )
            producto = cursor.fetchone()
            
            if not producto:
                return {'status': 'error', 'msg': 'Producto no encontrado'}
            
            if producto['estado'] != 'activo':
                return {'status': 'error', 'msg': 'Producto no disponible'}
            
            if producto['existencias'] < cantidad:
                return {'status': 'error', 'msg': f'Stock insuficiente. Disponibles: {producto["existencias"]}'}
            
            # Verificar si el item ya existe en el carrito
            cursor.execute(
                "SELECT id_item, cantidad FROM items_carrito WHERE id_carrito = %s AND id_producto = %s",
                (id_carrito, id_producto)
            )
            item_existente = cursor.fetchone()
            
            if item_existente:
                # Actualizar cantidad
                nueva_cantidad = item_existente['cantidad'] + cantidad
                
                if nueva_cantidad > producto['existencias']:
                    return {'status': 'error', 'msg': f'Stock insuficiente. Disponibles: {producto["existencias"]}'}
                
                cursor.execute(
                    "UPDATE items_carrito SET cantidad = %s WHERE id_item = %s",
                    (nueva_cantidad, item_existente['id_item'])
                )
            else:
                # Insertar nuevo item
                cursor.execute(
                    """INSERT INTO items_carrito (id_carrito, id_producto, cantidad, precio_unitario) 
                       VALUES (%s, %s, %s, %s)""",
                    (id_carrito, id_producto, cantidad, producto['precio'])
                )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Producto agregado al carrito'}
            
        except Error as e:
            print(f"Error al agregar producto al carrito: {e}")
            return {'status': 'error', 'msg': 'Error al agregar producto al carrito'}
    
    @staticmethod
    def actualizar_cantidad(id_cliente, id_producto, cantidad):
        """Actualiza la cantidad de un producto en el carrito"""
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return CarritoModel.eliminar_item(id_cliente, id_producto)
            
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Verificar stock disponible
            cursor.execute(
                "SELECT existencias FROM productos WHERE id_producto = %s AND estado = 'activo'",
                (id_producto,)
            )
            producto = cursor.fetchone()
            
            if not producto:
                return {'status': 'error', 'msg': 'Producto no encontrado'}
            
            if cantidad > producto['existencias']:
                return {'status': 'error', 'msg': f'Stock insuficiente. Disponibles: {producto["existencias"]}'}
            
            # Actualizar cantidad
            cursor.execute(
                """UPDATE items_carrito ic
                   INNER JOIN carrito c ON ic.id_carrito = c.id_carrito
                   SET ic.cantidad = %s
                   WHERE c.id_cliente = %s AND ic.id_producto = %s""",
                (cantidad, id_cliente, id_producto)
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Cantidad actualizada'}
            
        except Error as e:
            print(f"Error al actualizar cantidad: {e}")
            return {'status': 'error', 'msg': 'Error al actualizar cantidad'}
    
    @staticmethod
    def eliminar_item(id_cliente, id_producto):
        """Elimina un producto del carrito"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """DELETE ic FROM items_carrito ic
                   INNER JOIN carrito c ON ic.id_carrito = c.id_carrito
                   WHERE c.id_cliente = %s AND ic.id_producto = %s""",
                (id_cliente, id_producto)
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Producto eliminado del carrito'}
            
        except Error as e:
            print(f"Error al eliminar item: {e}")
            return {'status': 'error', 'msg': 'Error al eliminar producto'}
    
    @staticmethod
    def vaciar_carrito(id_cliente):
        """Vacía todo el carrito del cliente"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """DELETE ic FROM items_carrito ic
                   INNER JOIN carrito c ON ic.id_carrito = c.id_carrito
                   WHERE c.id_cliente = %s""",
                (id_cliente,)
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Carrito vaciado'}
            
        except Error as e:
            print(f"Error al vaciar carrito: {e}")
            return {'status': 'error', 'msg': 'Error al vaciar carrito'}
    
    @staticmethod
    def contar_items(id_cliente):
        """Cuenta el número total de items en el carrito"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(
                """SELECT COUNT(*) as total
                   FROM items_carrito ic
                   INNER JOIN carrito c ON ic.id_carrito = c.id_carrito
                   WHERE c.id_cliente = %s""",
                (id_cliente,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            return result['total'] if result else 0
            
        except Error as e:
            print(f"Error al contar items: {e}")
            return 0