# upload_images_gui.py
import mysql.connector
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

class ImageUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Subir Imágenes a Base de Datos")
        self.root.geometry("600x500")
        self.root.configure(bg='#ffe6f3')
        
        # Variables
        self.image_path = tk.StringVar()
        self.product_id = tk.StringVar()
        
        self.setup_ui()
    
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        try:
            return mysql.connector.connect(
                host="centerbeam.proxy.rlwy.net",
                user="APP_USER",
                password="4l1Sl4m4s",
                database="CHUCHERITAS_ARALAN"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la BD:\n{e}")
            return None
    
    def setup_ui(self):
        # Título
        title = tk.Label(self.root, text="🖼️ Subir Imágenes a la BD", 
                        font=('Arial', 16, 'bold'), bg='#ffe6f3', fg='#ff3b88')
        title.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#ffe6f3')
        main_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Seleccionar imagen
        tk.Label(main_frame, text="1. Seleccionar Imagen:", 
                font=('Arial', 11, 'bold'), bg='#ffe6f3').pack(anchor='w')
        
        image_frame = tk.Frame(main_frame, bg='#ffe6f3')
        image_frame.pack(fill='x', pady=5)
        
        tk.Entry(image_frame, textvariable=self.image_path, 
                width=50, font=('Arial', 10)).pack(side='left', padx=(0, 10))
        
        tk.Button(image_frame, text="📁 Examinar", 
                 command=self.select_image,
                 bg='#ff7ebf', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=15).pack(side='left')
        
        # Vista previa de imagen
        self.preview_label = tk.Label(main_frame, text="Vista previa aparecerá aquí", 
                                     bg='white', relief='sunken', width=60, height=10)
        self.preview_label.pack(pady=10)
        
        # ID del producto
        tk.Label(main_frame, text="2. ID del Producto:", 
                font=('Arial', 11, 'bold'), bg='#ffe6f3').pack(anchor='w')
        
        id_frame = tk.Frame(main_frame, bg='#ffe6f3')
        id_frame.pack(fill='x', pady=5)
        
        tk.Entry(id_frame, textvariable=self.product_id, 
                font=('Arial', 12), width=10).pack(side='left', padx=(0, 10))
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#ffe6f3')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="⬆️ Subir Imagen", 
                 command=self.upload_image,
                 bg='#28a745', fg='white', font=('Arial', 12, 'bold'),
                 relief='flat', padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="🔄 Subir Múltiples", 
                 command=self.upload_multiple,
                 bg='#007bff', fg='white', font=('Arial', 12, 'bold'),
                 relief='flat', padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="📋 Ver Imágenes en BD", 
                 command=self.view_images,
                 bg='#6c757d', fg='white', font=('Arial', 12, 'bold'),
                 relief='flat', padx=20, pady=10).pack(side='left', padx=10)
        
        # Área de log
        tk.Label(main_frame, text="Log de operaciones:", 
                font=('Arial', 11, 'bold'), bg='#ffe6f3').pack(anchor='w', pady=(20, 5))
        
        self.log_text = tk.Text(main_frame, height=8, width=70, font=('Arial', 9))
        self.log_text.pack(fill='both', expand=True)
        
        # Scrollbar para el log
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def select_image(self):
        """Abre diálogo para seleccionar imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.image_path.set(file_path)
            self.show_image_preview(file_path)
            self.log(f"📷 Imagen seleccionada: {os.path.basename(file_path)}")
    
    def show_image_preview(self, image_path):
        """Muestra vista previa de la imagen"""
        try:
            image = Image.open(image_path)
            # Redimensionar para vista previa
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Mantener referencia
        except Exception as e:
            self.preview_label.configure(image=None, text="❌ No se pudo cargar la vista previa")
            self.log(f"❌ Error en vista previa: {e}")
    
    def upload_image(self):
        """Sube una sola imagen a la base de datos"""
        if not self.image_path.get():
            messagebox.showwarning("Advertencia", "Por favor selecciona una imagen")
            return
        
        if not self.product_id.get().isdigit():
            messagebox.showwarning("Advertencia", "Por favor ingresa un ID de producto válido")
            return
        
        product_id = int(self.product_id.get())
        image_path = self.image_path.get()
        
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        try:
            with open(image_path, 'rb') as file:
                image_data = file.read()
            
            cursor.execute(
                "INSERT INTO fotos_productos (id_producto, foto) VALUES (%s, %s)",
                (product_id, image_data)
            )
            
            conn.commit()
            
            messagebox.showinfo("Éxito", f"✅ Imagen subida correctamente\nProducto ID: {product_id}")
            self.log(f"✅ SUBIDA EXITOSA: {os.path.basename(image_path)} → Producto {product_id}")
            
            # Limpiar campos
            self.image_path.set("")
            self.product_id.set("")
            self.preview_label.configure(image=None, text="Vista previa aparecerá aquí")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al subir imagen:\n{e}")
            self.log(f"❌ ERROR: {e}")
            conn.rollback()
        
        finally:
            cursor.close()
            conn.close()
    
    def upload_multiple(self):
        """Sube múltiples imágenes a la vez"""
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar múltiples imágenes",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_paths:
            return
        
        if not self.product_id.get().isdigit():
            messagebox.showwarning("Advertencia", "Por favor ingresa un ID de producto válido")
            return
        
        product_id = int(self.product_id.get())
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        success_count = 0
        error_count = 0
        
        try:
            for file_path in file_paths:
                try:
                    with open(file_path, 'rb') as file:
                        image_data = file.read()
                    
                    cursor.execute(
                        "INSERT INTO fotos_productos (id_producto, foto) VALUES (%s, %s)",
                        (product_id, image_data)
                    )
                    
                    success_count += 1
                    self.log(f"✅ {os.path.basename(file_path)} → Producto {product_id}")
                    
                except Exception as e:
                    error_count += 1
                    self.log(f"❌ {os.path.basename(file_path)}: {e}")
            
            conn.commit()
            
            messagebox.showinfo("Resultado", 
                              f"📊 Subida completada:\n✅ Éxitos: {success_count}\n❌ Errores: {error_count}")
            
            # Limpiar campos
            self.image_path.set("")
            self.product_id.set("")
            self.preview_label.configure(image=None, text="Vista previa aparecerá aquí")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error general: {e}")
            conn.rollback()
        
        finally:
            cursor.close()
            conn.close()
    
    def view_images(self):
        """Muestra todas las imágenes en la base de datos"""
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT fp.id_foto, fp.id_producto, p.nombre, LENGTH(fp.foto) as tamaño
                FROM fotos_productos fp
                LEFT JOIN productos p ON fp.id_producto = p.id_producto
                ORDER BY fp.id_producto
            """)
            
            images = cursor.fetchall()
            
            # Crear ventana de resultados
            result_window = tk.Toplevel(self.root)
            result_window.title("Imágenes en Base de Datos")
            result_window.geometry("500x400")
            
            tk.Label(result_window, text="📷 Imágenes en la Base de Datos", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Treeview para mostrar resultados
            tree = ttk.Treeview(result_window, columns=('ID', 'Producto', 'Nombre', 'Tamaño'), show='headings')
            tree.heading('ID', text='ID Foto')
            tree.heading('Producto', text='ID Producto')
            tree.heading('Nombre', text='Nombre Producto')
            tree.heading('Tamaño', text='Tamaño (bytes)')
            
            tree.column('ID', width=80)
            tree.column('Producto', width=100)
            tree.column('Nombre', width=150)
            tree.column('Tamaño', width=100)
            
            for img in images:
                tree.insert('', 'end', values=(
                    img['id_foto'],
                    img['id_producto'],
                    img['nombre'] or 'N/A',
                    img['tamaño']
                ))
            
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            self.log(f"📋 Consultadas {len(images)} imágenes de la BD")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al consultar imágenes:\n{e}")
            self.log(f"❌ ERROR en consulta: {e}")
        
        finally:
            cursor.close()
            conn.close()
    
    def log(self, message):
        """Agrega mensaje al log"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.log_text.update()

def main():
    root = tk.Tk()
    app = ImageUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()