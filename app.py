from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import logging

from backend.models import ProductoModel, UsuarioModel, CarritoModel, PedidoModel, AdminModel
from backend.admin_productos import AdminProductosModel
from backend.config import Config
from backend.database import is_database_available

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = Config.SECRET_KEY

# ==================== CONTEXT PROCESSORS ====================
@app.context_processor
def inject_database_status():
    return {
        'database_available': is_database_available(),
        'current_user': get_current_user()
    }

def get_current_user():
    """Obtiene información del usuario actual desde la sesión"""
    if 'user_id' in session:
        user_data = {
            'id': session['user_id'],
            'name': session.get('user_name', 'Usuario'),
            'email': session.get('user_email', ''),
            'type': session.get('user_type', 'cliente')
        }
        # Si es empleado, agregar el rol
        if user_data['type'] == 'empleado':
            user_data['rol'] = session.get('user_rol', 'empleado')
        return user_data
    return None

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
        print(f"DEBUG: Intentando login con {email}")  # DEBUG
        
        usuario = UsuarioModel.iniciar_sesion(email, password)
        if usuario:
            print(f"DEBUG: Usuario autenticado - {usuario}")  # DEBUG
            session_data = {
                'user_id': usuario['id'],
                'user_type': usuario['tipo'],
                'user_name': usuario['nombre'],
                'user_email': usuario['correo']
            }
            
            # Si es empleado, guardar el rol
            if usuario['tipo'] == 'empleado':
                session_data['user_rol'] = usuario.get('rol', 'empleado')
                print(f"DEBUG: Rol de sesión - {session_data['user_rol']}")  # DEBUG
            
            session.update(session_data)
            flash('¡Inicio de sesión exitoso!', 'success')
            
            # Redirigir según el tipo de usuario
            if usuario['tipo'] == 'empleado' and usuario.get('rol') in ['administrador','admin']:
                print("DEBUG: Deberia redirigir a admin/dashboard")
                return redirect(url_for('admin_dashboard'))
            elif usuario['tipo'] == 'empleado' and usuario.get('rol') == 'repartidor':
                print("DEBUG: Deberia redirigir a repartidor/dashboard")
                return redirect(url_for('repartidor_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            print("DEBUG: Login fallido")  # DEBUG
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
    return {
        'database': '✅ Conectado' if is_database_available() else '❌ Desconectado',
        'app': '✅ Funcionando'
    }

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
    flash('Producto agregado al carrito' if resultado['status'] == 'ok' else resultado['msg'],
          'success' if resultado['status'] == 'ok' else 'error')
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
@requiere_rol('administrador')
def admin_dashboard():
    estadisticas = AdminModel.obtener_estadisticas()
    return render_template("admin/dashboard.html", stats=estadisticas)

@app.route("/admin/productos")
@requiere_rol('administrador')
def admin_productos():
    productos = ProductoModel.obtener_todos()
    return render_template("admin/productos/listar.html", productos=productos)


# ==================== RUTAS REPARTIDOR ====================
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
    flash('Estado del pedido actualizado' if resultado['status'] == 'ok' else resultado['msg'],
          'success' if resultado['status'] == 'ok' else 'error')
    return redirect(request.referrer or url_for('repartidor/dashboard.html'))

# ==================== MANEJO DE ERRORES ====================
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('errors/500.html'), 500



# ==================== AGREGAR ESTAS RUTAS A TU app.py ====================
# Agregar este import al inicio del archivo
from backend.admin_productos import AdminProductosModel

# ==================== RUTAS MEJORADAS DE CARRITO ====================

@app.route("/api/carrito/cantidad")
def obtener_cantidad_carrito():
    """API para obtener cantidad de items en el carrito"""
    if 'user_id' not in session or session.get('user_type') != 'cliente':
        return {'cantidad': 0}
    
    cantidad = CarritoModel.contar_items(session['user_id'])
    return {'cantidad': cantidad}

@app.route("/carrito/actualizar/<int:id_producto>", methods=['POST'])
@requiere_rol('cliente')
def actualizar_carrito(id_producto):
    """Actualiza la cantidad de un producto en el carrito"""
    cantidad = request.form.get('cantidad', 1)
    resultado = CarritoModel.actualizar_cantidad(session['user_id'], id_producto, cantidad)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return resultado
    
    flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    return redirect(url_for('carrito'))

@app.route("/carrito/eliminar/<int:id_producto>", methods=['POST'])
@requiere_rol('cliente')
def eliminar_del_carrito(id_producto):
    """Elimina un producto del carrito"""
    resultado = CarritoModel.eliminar_item(session['user_id'], id_producto)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return resultado
    
    flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    return redirect(url_for('carrito'))

@app.route("/carrito/vaciar", methods=['POST'])
@requiere_rol('cliente')
def vaciar_carrito():
    """Vacía todo el carrito"""
    resultado = CarritoModel.vaciar_carrito(session['user_id'])
    flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    return redirect(url_for('carrito'))

# ==================== RUTAS ADMIN - PRODUCTOS ====================

@app.route("/admin/productos/agregar", methods=['GET', 'POST'])
@requiere_rol('admin')
def admin_agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        id_categoria = request.form.get('id_categoria')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        existencias = request.form.get('existencias', 0)
        
        resultado = AdminProductosModel.crear_producto(
            nombre, id_categoria, descripcion, precio, existencias
        )
        
        flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
        
        if resultado['status'] == 'ok':
            return redirect(url_for('admin_productos'))
    
    categorias = AdminProductosModel.obtener_todas_categorias()
    return render_template("admin/productos/agregar.html", categorias=categorias)

@app.route("/admin/productos/editar/<int:id_producto>", methods=['GET', 'POST'])
@requiere_rol('admin')
def admin_editar_producto(id_producto):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        id_categoria = request.form.get('id_categoria')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        existencias = request.form.get('existencias')
        estado = request.form.get('estado', 'activo')
        
        resultado = AdminProductosModel.actualizar_producto(
            id_producto, nombre, id_categoria, descripcion, precio, existencias, estado
        )
        
        flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
        
        if resultado['status'] == 'ok':
            return redirect(url_for('admin_productos'))
    
    producto = AdminProductosModel.obtener_producto_por_id(id_producto)
    categorias = AdminProductosModel.obtener_todas_categorias()
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('admin_productos'))
    
    return render_template("admin/productos/editar.html", producto=producto, categorias=categorias)

@app.route("/admin/productos/eliminar/<int:id_producto>", methods=['POST'])
@requiere_rol('admin')
def admin_eliminar_producto(id_producto):
    """Descontinúa un producto"""
    resultado = AdminProductosModel.eliminar_producto(id_producto)
    flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    return redirect(url_for('admin_productos'))

@app.route("/admin/productos/stock-bajo")
@requiere_rol('admin')
def admin_productos_stock_bajo():
    """Muestra productos con stock bajo"""
    productos = AdminProductosModel.obtener_productos_bajo_stock(minimo=10)
    return render_template("admin/productos/stock_bajo.html", productos=productos)

@app.route("/admin/productos/actualizar-stock/<int:id_producto>", methods=['POST'])
@requiere_rol('admin')
def admin_actualizar_stock(id_producto):
    """Actualiza el stock de un producto"""
    cantidad = request.form.get('cantidad', 0)
    resultado = AdminProductosModel.actualizar_existencias(id_producto, cantidad)
    flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    return redirect(request.referrer or url_for('admin_productos'))

@app.route("/admin/categorias", methods=['GET', 'POST'])
@requiere_rol('admin')
def admin_categorias():
    """Gestión de categorías"""
    if request.method == 'POST':
        id_categoria = request.form.get('id_categoria')
        descripcion = request.form.get('descripcion')
        
        resultado = AdminProductosModel.crear_categoria(id_categoria, descripcion)
        flash(resultado['msg'], 'success' if resultado['status'] == 'ok' else 'error')
    
    categorias = AdminProductosModel.obtener_todas_categorias()
    return render_template("admin/categorias/listar.html", categorias=categorias)

@app.route("/admin/productos/buscar")
@requiere_rol('admin')
def admin_buscar_productos():
    """Busca productos"""
    termino = request.args.get('q', '')
    
    if termino:
        productos = AdminProductosModel.buscar_productos(termino)
    else:
        productos = ProductoModel.obtener_todos()
    
    return render_template("admin/productos/listar.html", productos=productos, termino=termino)


# Falta logica
@app.route("/admin/pedidos")
@requiere_rol('admin')
def admin_pedidos():
    """Vista de pedidos para administrador"""
    # Aquí implementar la lógica para obtener pedidos
    return render_template("admin/pedidos/listar.html")

@app.route("/repartidor/dashboard")
@requiere_rol('repartidor')
def repartidor_dashboard():
    """Dashboard del repartidor"""
    pedidos = PedidoModel.obtener_para_repartidor()
    return render_template("repartidor/dashboard.html", pedidos=pedidos)




if __name__ == "__main__":
    app.run(debug=True)
