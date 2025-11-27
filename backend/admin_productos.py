from backend.database import get_connection
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os

class AdminProductosModel:
    """Clase para gestión administrativa de productos"""
    
    @staticmethod
    def crear_producto(nombre, id_categoria, descripcion, precio, existencias):
        """Crea un nuevo producto"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO productos (nombre, id_categoria, descripcion, precio, existencias, estado)
                VALUES (%s, %s, %s, %s, %s, 'activo')
            """
            
            cursor.execute(query, (nombre, id_categoria, descripcion, precio, existencias))
            connection.commit()
            
            id_producto = cursor.lastrowid
            
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Producto creado exitosamente', 'id_producto': id_producto}
            
        except Error as e:
            print(f"Error al crear producto: {e}")
            return {'status': 'error', 'msg': f'Error al crear producto: {str(e)}'}
    
    @staticmethod
    def actualizar_producto(id_producto, nombre, id_categoria, descripcion, precio, existencias, estado):
        """Actualiza un producto existente"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            query = """
                UPDATE productos 
                SET nombre = %s, id_categoria = %s, descripcion = %s, 
                    precio = %s, existencias = %s, estado = %s
                WHERE id_producto = %s
            """
            
            cursor.execute(query, (nombre, id_categoria, descripcion, precio, existencias, estado, id_producto))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Producto actualizado exitosamente'}
            
        except Error as e:
            print(f"Error al actualizar producto: {e}")
            return {'status': 'error', 'msg': f'Error al actualizar producto: {str(e)}'}
    
    @staticmethod
    def eliminar_producto(id_producto):
        """Marca un producto como descontinuado (soft delete)"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "UPDATE productos SET estado = 'descontinuado' WHERE id_producto = %s",
                (id_producto,)
            )
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Producto descontinuado exitosamente'}
            
        except Error as e:
            print(f"Error al eliminar producto: {e}")
            return {'status': 'error', 'msg': f'Error al eliminar producto: {str(e)}'}
    
    @staticmethod
    def obtener_producto_por_id(id_producto):
        """Obtiene un producto específico por ID"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT p.*, c.descripcion as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.id_producto = %s
            """
            
            cursor.execute(query, (id_producto,))
            producto = cursor.fetchone()
            
            if producto:
                producto['precio'] = float(producto['precio'])
            
            cursor.close()
            connection.close()
            
            return producto
            
        except Error as e:
            print(f"Error al obtener producto: {e}")
            return None
    
    @staticmethod
    def obtener_todas_categorias():
        """Obtiene todas las categorías disponibles"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM categorias ORDER BY descripcion")
            categorias = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return categorias
            
        except Error as e:
            print(f"Error al obtener categorías: {e}")
            return []
    
    @staticmethod
    def crear_categoria(id_categoria, descripcion):
        """Crea una nueva categoría"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "INSERT INTO categorias (id_categoria, descripcion) VALUES (%s, %s)",
                (id_categoria, descripcion)
            )
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Categoría creada exitosamente'}
            
        except Error as e:
            print(f"Error al crear categoría: {e}")
            return {'status': 'error', 'msg': f'Error al crear categoría: {str(e)}'}
    
    @staticmethod
    def actualizar_existencias(id_producto, cantidad):
        """Actualiza las existencias de un producto"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "UPDATE productos SET existencias = existencias + %s WHERE id_producto = %s",
                (cantidad, id_producto)
            )
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return {'status': 'ok', 'msg': 'Existencias actualizadas'}
            
        except Error as e:
            print(f"Error al actualizar existencias: {e}")
            return {'status': 'error', 'msg': 'Error al actualizar existencias'}
    
    @staticmethod
    def obtener_productos_bajo_stock(minimo=10):
        """Obtiene productos con stock bajo"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT p.*, c.descripcion as categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.existencias < %s AND p.estado = 'activo'
                ORDER BY p.existencias ASC
            """
            
            cursor.execute(query, (minimo,))
            productos = cursor.fetchall()
            
            for producto in productos:
                producto['precio'] = float(producto['precio'])
            
            cursor.close()
            connection.close()
            
            return productos
            
        except Error as e:
            print(f"Error al obtener productos bajo stock: {e}")
            return []
    
    @staticmethod
    def buscar_productos(termino):
        """Busca productos por nombre o descripción"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT p.*, c.descripcion as categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE (p.nombre LIKE %s OR p.descripcion LIKE %s)
                ORDER BY p.nombre
            """
            
            termino_busqueda = f"%{termino}%"
            cursor.execute(query, (termino_busqueda, termino_busqueda))
            productos = cursor.fetchall()
            
            for producto in productos:
                producto['precio'] = float(producto['precio'])
            
            cursor.close()
            connection.close()
            
            return productos
            
        except Error as e:
            print(f"Error al buscar productos: {e}")
            return []