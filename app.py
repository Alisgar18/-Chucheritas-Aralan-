from flask import Flask, render_template, request, redirect, url_for, session, flash
from backend.models import ProductoModel, UsuarioModel
from backend.config import Config
from backend.database import is_database_available
import logging

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

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)