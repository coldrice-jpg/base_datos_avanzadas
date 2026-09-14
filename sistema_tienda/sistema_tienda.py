from datetime import datetime, date
import os
import persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
import transaction
from ZODB import DB, FileStorage

class Producto(persistent.Persistent):

    def __init__(self, id_producto: str, nombre: str, precio: float, stock: int):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)
        self.activo = True

    def actualizar_datos(self, nombre: str, precio: float):
        self.nombre = nombre
        self.precio = float(precio)
        self._p_changed = True 

    def descontar_stock(self, cantidad: int) -> bool:
        if self.esta_disponible(cantidad):
            self.stock -= cantidad
            self._p_changed = True
            return True
        return False

    def reponer_stock(self, cantidad: int):
        self.stock += cantidad
        self._p_changed = True

    def esta_disponible(self, cantidad: int) -> bool:
        return self.activo and self.stock >= cantidad

    def desactivar(self):
        self.activo = False
        self._p_changed = True

    def __repr__(self):
        return (
            f"<Producto id={self.id_producto} nombre='{self.nombre}'"
            f" stock={self.stock} precio={self.precio} activo={self.activo}>"
        )


class ItemVenta(persistent.Persistent):

    def __init__(self, producto: Producto, cantidad: int):
        self.producto = producto
        self.cantidad = int(cantidad)
        self.precio_unitario = float(producto.precio)

    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario


class Venta(persistent.Persistent):

    def __init__(self, id_venta: str):
        self.id_venta = id_venta
        self.fecha_hora = datetime.now()
        self.items = PersistentList()
        self.total = 0.0

    def agregar_item(self, producto: Producto, cantidad: int):
        item = ItemVenta(producto, cantidad)
        self.items.append(item)
        self.calcular_total()

    def calcular_total(self) -> float:
        self.total = sum(item.subtotal() for item in self.items)
        self._p_changed = True
        return self.total

    def __repr__(self):
        return (
            f"<Venta id={self.id_venta} fecha={self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
            f" total={self.total:.2f} items={len(self.items)}>"
        )


class GestorBDOO:

    def __init__(self, db_path: str = "tienda_bdoo.fs"):
        self.db_path = db_path
        self.storage = FileStorage.FileStorage(self.db_path)
        self.db = DB(self.storage)
        self.conexion = self.db.open()
        self.raiz = self.conexion.root()

        if "productos" not in self.raiz:
            self.raiz["productos"] = PersistentMapping()
        if "ventas" not in self.raiz:
            self.raiz["ventas"] = PersistentList()
            transaction.commit()

    def confirmar(self):
        transaction.commit()

    def cerrar(self):
        transaction.commit()
        self.conexion.close()
        self.db.close()
        self.storage.close()


class TiendaService:

    def __init__(self, gestor: GestorBDOO):
        self.gestor = gestor
        self.productos = gestor.raiz["productos"]
        self.ventas = gestor.raiz["ventas"]

    def crear_producto(
        self, id_producto: str, nombre: str, precio: float, stock: int
    ) -> Producto:
        if id_producto in self.productos:
            raise ValueError(f"El producto con ID '{id_producto}' ya existe.")
        nuevo = Producto(id_producto, nombre, precio, stock)
        self.productos[id_producto] = nuevo
        self.gestor.confirmar()
        return nuevo

    def consultar_producto(self, id_producto: str) -> Producto:
        prod = self.productos.get(id_producto)
        if not prod or not prod.activo:
            return None
        return prod

    def modificar_producto(
        self, id_producto: str, nuevo_nombre: str, nuevo_precio: float
    ) -> bool:
        prod = self.consultar_producto(id_producto)
        if not prod:
            return False
        prod.actualizar_datos(nuevo_nombre, nuevo_precio)
        self.gestor.confirmar()
        return True

    def eliminar_producto(self, id_producto: str) -> bool:
        prod = self.consultar_producto(id_producto)
        if not prod:
            return False
        prod.desactivar()
        self.gestor.confirmar()
        return True

    def registrar_venta(self, items_solicitados: list) -> Venta:
        for p_id, cant in items_solicitados:
            prod = self.consultar_producto(p_id)
        if not prod or not prod.esta_disponible(cant):
            raise ValueError(f"Inventario insuficiente para: {p_id}")

        folio = f"V-{len(self.ventas) + 1:04d}"
        venta = Venta(id_venta=folio)

        for p_id, cant in items_solicitados:
            prod = self.consultar_producto(p_id)
            prod.descontar_stock(cant)
            venta.agregar_item(prod, cant)

        self.ventas.append(venta)
        self.gestor.confirmar()
        return venta

    def reporte_ventas_diarias(self, dia_objetivo: date) -> float:
        total_acumulado = 0.0
        for v in self.ventas:
            if v.fecha_hora.date() == dia_objetivo:
                total_acumulado += v.total
        return total_acumulado


def limpiar_archivos_bd(db_path: str = "tienda_bdoo.fs"):
    """Limpia el entorno para ejecutar una prueba desde cero."""
    for extra in ["", ".index", ".lock", ".tmp"]:
        archivo = db_path + extra
        if os.path.exists(archivo):
            os.remove(archivo)


def ejecutar_pruebas():
    limpiar_archivos_bd()
    print("=" * 70)
    print("INICIANDO EJECUCIÓN DE PRUEBAS DEL SISTEMA BDOO")
    print("=" * 70)

    gestor = GestorBDOO()
    tienda = TiendaService(gestor)

    print("\n[PRUEBA 1] Crear producto: El producto queda almacenado.")
    p1 = tienda.crear_producto(
        id_producto="PROD-01", nombre="Mouse Ergonomico", precio=450.0, stock=20
    )
    p2 = tienda.crear_producto(
        id_producto="PROD-02", nombre="Teclado Mecanico", precio=1200.0, stock=10
    )
    print(f" -> Creado: {p1}")
    print(f" -> Creado: {p2}")

    print("\n[PRUEBA 2] Consultar producto: Se recupera correctamente.")
    prod_recuperado = tienda.consultar_producto("PROD-01")
    print(
        f" -> Recuperado: {prod_recuperado.nombre} | Stock:"
        f" {prod_recuperado.stock} | Precio: ${prod_recuperado.precio}"
    )

    print("\n[PRUEBA 3] Modificar producto: La información cambia.")
    tienda.modificar_producto(
        "PROD-01", nuevo_nombre="Mouse Ergonomico Inalambrico", nuevo_precio=499.99
    )
    prod_modificado = tienda.consultar_producto("PROD-01")
    print(
        f" -> Modificado: {prod_modificado.nombre} | Nuevo precio:"
        f" ${prod_modificado.precio}"
    )

    print(
        "\n[PRUEBA 4] Eliminar producto: El objeto deja de estar disponible en el"
        " catálogo."
    )
    tienda.crear_producto(
        id_producto="PROD-TEMP", nombre="Cable USB", precio=50.0, stock=5
    )
    print(f" -> Estado previo: {tienda.consultar_producto('PROD-TEMP')}")
    tienda.eliminar_producto("PROD-TEMP")
    resultado_consulta = tienda.consultar_producto("PROD-TEMP")
    print(
        f" -> Consulta post-eliminación: {resultado_consulta} (No disponible para"
        " venta)"
    )

    print("\n[PRUEBA 5] Registrar venta: Se genera una nueva venta.")
    print("[PRUEBA 6] Actualizar inventario: Las existencias cambian.")
    stock_inicial_p1 = tienda.consultar_producto("PROD-01").stock
    stock_inicial_p2 = tienda.consultar_producto("PROD-02").stock
    print(
        f" -> Stock previo venta: PROD-01: {stock_inicial_p1} | PROD-02:"
        f" {stock_inicial_p2}"
    )

    venta_realizada = tienda.registrar_venta([("PROD-01", 3), ("PROD-02", 2)])
    print(f" -> Venta confirmada: {venta_realizada}")
    for idx, it in enumerate(venta_realizada.items, start=1):
        print(
            f"    Item {idx}: {it.producto.nombre} x {it.cantidad} @ ${it.precio_unitario}"
            f" = Subtotal: ${it.subtotal():.2f}"
        )

    stock_final_p1 = tienda.consultar_producto("PROD-01").stock
    stock_final_p2 = tienda.consultar_producto("PROD-02").stock
    print(
        f" -> Stock posterior: PROD-01: {stock_final_p1} (Restaron 3) | PROD-02:"
        f" {stock_final_p2} (Restaron 2)"
    )

    print(
        "\n[PRUEBA 7] Consulta relacionada: Generar reporte de venta total diaria."
    )
    tienda.registrar_venta([("PROD-01", 1)])
    hoy = datetime.now().date()
    total_hoy = tienda.reporte_ventas_diarias(hoy)
    print(
        f" -> Fecha evaluada: {hoy} | Total recaudado en el dia: ${total_hoy:.2f}"
    )

    print("\n[PRUEBA 8] Cerrar y abrir el sistema: Los datos permanecen.")
    print(" -> Cerrando la conexion y liberando proceso...")
    gestor.cerrar()

    print(" -> Reabriendo archivo de base de datos 'tienda_bdoo.fs'...")
    nuevo_gestor = GestorBDOO()
    nueva_tienda = TiendaService(nuevo_gestor)

    p1_persistido = nueva_tienda.consultar_producto("PROD-01")
    ventas_persistidas = nueva_tienda.ventas
    total_persistido = nueva_tienda.reporte_ventas_diarias(hoy)

    print(
        f" -> Producto PROD-01 leido de disco: {p1_persistido.nombre} con stock:"
        f" {p1_persistido.stock}"
    )
    print(f" -> Total de ventas recuperadas: {len(ventas_persistidas)}")
    print(
        f" -> Total acumulado recalculado tras reinicio: ${total_persistido:.2f}"
    )

    nuevo_gestor.cerrar()
    print("\n" + "=" * 70)
    print("TODAS LAS PRUEBAS FINALIZARON EXITOSAMENTE.")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_pruebas()