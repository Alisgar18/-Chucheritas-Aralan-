from flask import Flask, render_template, request, redirect, url_for, session, flash
from backend.models import UsuarioModel, ProductoModel
from backend.config import Config

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = Config.SECRET_KEY

# ==================== RUTAS PÚBLICAS ====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/catalogo")
def catalogo():
    productos = ProductoModel.obtener_todos()
    return render_template("catalogo.html", productos=productos)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Si ya está logueado, redirigir al home
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
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
    # Si ya está logueado, redirigir al home
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
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

# ==================== RUTAS PROTEGIDAS ====================

@app.route("/perfil")
def perfil():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'error')
        return redirect(url_for('login'))
    
    return render_template("auth/perfil.html")

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('errors/500.html'), 500

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_user():
    """Inyecta información del usuario en todos los templates"""
    if 'user_id' in session:
        return {
            'current_user': {
                'id': session['user_id'],
                'name': session['user_name'],
                'email': session['user_email'],
                'type': session['user_type']
            }
        }
    return {'current_user': None}

if __name__ == "__main__":
    app.run(debug=True)