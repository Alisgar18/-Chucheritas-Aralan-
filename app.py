from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import logging


from backend.models import ProductoModel, UsuarioModel
from backend.config import Config
from backend.database import is_database_available

from backend.models import CarritoModel, PedidoModel, AdminModel

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = Config.SECRET_KEY

# Context processor para inyectar estado de BD en todos los templates
@app.context_processor
def inject_database_status():
    return {
        'database_available': is_database_available(),
        'current_user': get_current_user()
    }

def get_current_user():
    """Obtiene información del usuario actual desde la sesión"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'name': session.get('user_name', 'Usuario'),
            'email': session.get('user_email', ''),
            'type': session.get('user_type', 'cliente')
        }
    return None

# ==================== RUTAS PÚBLICAS ====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/catalogo")
def catalogo():
    try:
        productos = ProductoModel.obtener_todos()
        return render_template("catalogo.html", productos=productos)
    except Exception as e:
        logger.error(f"Error en catálogo: {e}")
        flash("Error al cargar el catálogo", "error")
        return render_template("catalogo.html", productos=[])

@app.route("/login", methods=['GET', 'POST'])
def login():
    if get_current_user():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if not is_database_available():
            flash("Base de datos no disponible. Intenta más tarde.", "error")
            return render_template("auth/login.html")
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = UsuarioModel.iniciar_sesion(email, password)
        
        if usuario:
            session['user_id'] = usuario['id']
            session['user_type'] = usuario['tipo']
            session['user_name'] = usuario['nombre']
            session['user_email'] = usuario['correo']
            
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template("auth/login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if get_current_user():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if not is_database_available():
            flash("Base de datos no disponible. Intenta más tarde.", "error")
            return render_template("auth/register.html")
        
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        
        resultado = UsuarioModel.registrar_cliente(nombre, email, password, telefono)
        
        if resultado['status'] == 'ok':
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(resultado['msg'], 'error')
    
    return render_template("auth/register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('home'))

@app.route("/perfil")
def perfil():
    if not get_current_user():
        flash('Debes iniciar sesión para ver tu perfil', 'error')
        return redirect(url_for('login'))
    
    return render_template("auth/perfil.html")

@app.route("/status")
def status():
    """Página para verificar el estado del sistema"""
    status_info = {
        'database': '✅ Conectado' if is_database_available() else '❌ Desconectado',
        'app': '✅ Funcionando'
    }
    return status_info

# ==================== MIDDLEWARE PARA ROLES ====================
def requiere_rol(rol):
    """Decorator para verificar roles de usuario"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session:
                flash('Debes iniciar sesión', 'error')
                return redirect(url_for('login'))
            
            if session['user_type'] != rol:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def requiere_rol_o(roles):
    """Decorator para verificar múltiples roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session:
                flash('Debes iniciar sesión', 'error')
                return redirect(url_for('login'))
            
            if session['user_type'] not in roles:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== RUTAS CLIENTE ====================

@app.route("/carrito")
@requiere_rol('cliente')
def carrito():
    carrito_items = CarritoModel.obtener_carrito(session['user_id'])
    return render_template("cliente/carrito.html", carrito=carrito_items)

@app.route("/agregar-carrito/<int:id_producto>", methods=['POST'])
@requiere_rol('cliente')
def agregar_carrito(id_producto):
    cantidad = request.form.get('cantidad', 1)
    resultado = CarritoModel.agregar_producto(session['user_id'], id_producto, cantidad)
    
    if resultado['status'] == 'ok':
        flash('Producto agregado al carrito', 'success')
    else:
        flash(resultado['msg'], 'error')
    
    return redirect(request.referrer or url_for('catalogo'))

@app.route("/cliente/pedidos")
@requiere_rol('cliente')
def cliente_pedidos():
    pedidos = PedidoModel.obtener_por_cliente(session['user_id'])
    return render_template("cliente/pedidos.html", pedidos=pedidos)

@app.route("/checkout")
@requiere_rol('cliente')
def checkout():
    carrito_items = CarritoModel.obtener_carrito(session['user_id'])
    return render_template("cliente/checkout.html", carrito=carrito_items)

# ==================== RUTAS ADMIN ====================

@app.route("/admin")
@requiere_rol('admin')
def admin_dashboard():
    estadisticas = AdminModel.obtener_estadisticas()
    return render_template("admin/dashboard.html", stats=estadisticas)

@app.route("/admin/productos")
@requiere_rol('admin')
def admin_productos():
    productos = ProductoModel.obtener_todos()
    return render_template("admin/productos/listar.html", productos=productos)

@app.route("/admin/productos/agregar", methods=['GET', 'POST'])
@requiere_rol('admin')
def admin_agregar_producto():
    if request.method == 'POST':
        # Procesar formulario de agregar producto
        pass
    return render_template("admin/productos/agregar.html")

@app.route("/admin/pedidos")
@requiere_rol('admin')
def admin_pedidos():
    # Obtener todos los pedidos
    return render_template("admin/pedidos/listar.html")

@app.route("/admin/empleados")
@requiere_rol('admin')
def admin_empleados():
    # Listar empleados
    return render_template("admin/empleados/listar.html")

# ==================== RUTAS REPARTIDOR ====================

@app.route("/repartidor")
@requiere_rol('repartidor')
def repartidor_dashboard():
    pedidos = PedidoModel.obtener_para_repartidor()
    return render_template("repartidor/dashboard.html", pedidos=pedidos)

@app.route("/repartidor/pedidos")
@requiere_rol('repartidor')
def repartidor_pedidos():
    pedidos = PedidoModel.obtener_para_repartidor()
    return render_template("repartidor/pedidos.html", pedidos=pedidos)

@app.route("/actualizar-estado/<int:id_pedido>", methods=['POST'])
@requiere_rol_o(['repartidor', 'admin'])
def actualizar_estado_pedido(id_pedido):
    nuevo_estado = request.form.get('estado')
    resultado = PedidoModel.actualizar_estado(id_pedido, nuevo_estado)
    
    if resultado['status'] == 'ok':
        flash('Estado del pedido actualizado', 'success')
    else:
        flash(resultado['msg'], 'error')
    
    return redirect(request.referrer or url_for('repartidor_dashboard'))


# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('errors/500.html'), 500





if __name__ == "__main__":
    app.run(debug=True)