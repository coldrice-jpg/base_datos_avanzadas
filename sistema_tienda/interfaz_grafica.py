import os
import tkinter as tk
from tkinter import ttk, messagebox

from database import DatabaseManager
from servicios import InventarioService
from consultas import InventarioQueries
from excepciones import TiendaError


DB_PATH = os.path.join("data", "tienda.fs")


class TiendaApp:
    """Ventana principal para la gestión visual del inventario."""

    def __init__(self, root: tk.Tk) -> None:
        """Inicializa los componentes de la interfaz y la conexión a la BD."""
        self.root = root
        self.root.title("Gestión de Tienda - BDOO ZODB")
        self.root.geometry("780x520")

        # Inicialización de la persistencia y servicios
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.db_manager = DatabaseManager(filepath=DB_PATH)
        self.db_manager.initialize()

        self.inventario_service = InventarioService(self.db_manager)
        self.inventario_queries = InventarioQueries(self.db_manager)

        self._crear_widgets()
        self.actualizar_tabla()

    def _crear_widgets(self) -> None:
        """Construye los paneles, formularios y tablas de la interfaz."""
        # Contenedor del formulario de alta
        marco_form = ttk.LabelFrame(self.root, text=" Registrar Nuevo Producto ")
        marco_form.pack(fill="x", padx=12, pady=8)

        ttk.Label(marco_form, text="Código:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.ent_codigo = ttk.Entry(marco_form, width=12)
        self.ent_codigo.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(marco_form, text="Nombre:").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.ent_nombre = ttk.Entry(marco_form, width=22)
        self.ent_nombre.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(marco_form, text="Precio ($):").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.ent_precio = ttk.Entry(marco_form, width=10)
        self.ent_precio.grid(row=0, column=5, padx=6, pady=6)

        ttk.Label(marco_form, text="Stock:").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        self.ent_stock = ttk.Entry(marco_form, width=8)
        self.ent_stock.grid(row=0, column=7, padx=6, pady=6)

        btn_guardar = ttk.Button(marco_form, text="Guardar en ZODB", command=self._registrar_producto)
        btn_guardar.grid(row=0, column=8, padx=8, pady=6)

        # Contenedor de la tabla de visualización
        marco_tabla = ttk.LabelFrame(self.root, text=" Catálogo e Inventario Actual ")
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=6)

        columnas = ("codigo", "nombre", "precio", "stock")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=12)
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Nombre del Producto")
        self.tabla.heading("precio", text="Precio Unitario ($)")
        self.tabla.heading("stock", text="Stock Disponible")

        self.tabla.column("codigo", width=100, anchor="center")
        self.tabla.column("nombre", width=320)
        self.tabla.column("precio", width=140, anchor="e")
        self.tabla.column("stock", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 8))

        # Barra de acciones de consulta
        marco_acciones = ttk.Frame(self.root)
        marco_acciones.pack(fill="x", padx=12, pady=8)

        btn_todos = ttk.Button(marco_acciones, text="Ver Todos", command=self.actualizar_tabla)
        btn_todos.pack(side="left", padx=4)

        btn_bajo_stock = ttk.Button(
            marco_acciones, text="Filtrar Bajo Stock (<= 5)", command=self._mostrar_bajo_stock
        )
        btn_bajo_stock.pack(side="left", padx=4)

    def _limpiar_campos(self) -> None:
        """Borra el contenido de los campos de texto."""
        self.ent_codigo.delete(0, tk.END)
        self.ent_nombre.delete(0, tk.END)
        self.ent_precio.delete(0, tk.END)
        self.ent_stock.delete(0, tk.END)

    def _registrar_producto(self) -> None:
        """Captura los datos del formulario e invoca el servicio de negocio."""
        codigo = self.ent_codigo.get().strip()
        nombre = self.ent_nombre.get().strip()
        precio_str = self.ent_precio.get().strip()
        stock_str = self.ent_stock.get().strip()

        try:
            precio = float(precio_str)
            stock = int(stock_str)
            self.inventario_service.registrar_producto(codigo, nombre, precio, stock)
            messagebox.showinfo("Éxito", f"Producto '{nombre}' registrado en ZODB con éxito.")
            self._limpiar_campos()
            self.actualizar_tabla()
        except ValueError:
            messagebox.showwarning("Error de Formato", "El precio debe ser decimal y el stock entero.")
        except TiendaError as error_dominio:
            messagebox.showerror("Error de Operación", str(error_dominio))

    def actualizar_tabla(self) -> None:
        """Carga en la vista los productos disponibles mediante la capa de consultas."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        productos = self.inventario_queries.productos_disponibles()
        for prod in productos:
            self.tabla.insert(
                "", tk.END, values=(prod.codigo, prod.nombre, f"${prod.precio:,.2f}", prod.stock)
            )

    def _mostrar_bajo_stock(self) -> None:
        """Carga en la vista únicamente los productos con alerta de stock."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        productos_alerta = self.inventario_queries.productos_bajo_stock(umbral=5)
        for prod in productos_alerta:
            self.tabla.insert(
                "", tk.END, values=(prod.codigo, prod.nombre, f"${prod.precio:,.2f}", prod.stock)
            )

    def cerrar(self) -> None:
        """Garantiza el cierre seguro de ZODB al cerrar la ventana."""
        self.db_manager.close()
        self.root.destroy()


def main() -> None:
    """Arranca el bucle de eventos de la aplicación visual."""
    root = tk.Tk()
    app = TiendaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()


if __name__ == "__main__":
    main()