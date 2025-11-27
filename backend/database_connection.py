import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="user",
        password="th1s_1s_4_cl13nt",
        database="tienda"
    )

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nombre, precio, descripcion, imagen FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos
