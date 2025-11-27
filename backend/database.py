import mysql.connector
from contextlib import contextmanager
from backend.config import Config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """Obtiene una conexión a la base de datos con manejo de errores"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            port=Config.MYSQL_PORT,
            connection_timeout=10  # Timeout de 10 segundos
        )
        logger.info("✅ Conexión a BD establecida correctamente")
        return connection
    except mysql.connector.Error as e:
        logger.error(f"❌ Error conectando a la BD: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return None

@contextmanager
def get_db_connection():
    """Context manager para manejo automático de conexiones"""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            raise Exception("No se pudo establecer conexión con la base de datos")
        yield conn
    except Exception as e:
        logger.error(f"Error en conexión: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.info("🔌 Conexión a BD cerrada")

@contextmanager
def get_db_cursor(dictionary=True):
    """Context manager para manejo automático de cursor"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error en transacción: {e}")
                raise
            finally:
                cursor.close()
    except Exception as e:
        logger.error(f"No se pudo obtener cursor: {e}")
        raise

# Función para verificar si la BD está disponible
def is_database_available():
    """Verifica si la base de datos está disponible"""
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            conn.close()
            return True
        return False
    except:
        return False